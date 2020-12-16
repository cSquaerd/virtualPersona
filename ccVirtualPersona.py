# Written by Charlie Cook
# Begun December 12th, 2020
# Fully Operational by December 16th, 2020

# IMPORTS
import numpy as np
import sounddevice as sd
import tkinter as tk
import tkinter.filedialog as fdi
import tkinter.messagebox as mbx
import json

# CONSTANTS
w = 800#640
h = 600#480
mlh = 3 * h // 4 - 8
mlw = w // 32
statw = 21 * w // 32
stath = mlh

# Base Window
base = tk.Tk()
base.resizable(False, False)
base.title("Virtual Persona")
# Main Frame
controls = tk.LabelFrame(
	base,
	width = w, height = h,
	text = "Controls",
	bd = 4, relief = "raised"
)

# Mic Level Frame
mlFrame = tk.LabelFrame(
	controls, 
	relief = "sunken", bd = 4,
)
# Mic Level Canvas
micLevel = tk.Canvas(
	mlFrame,
	width = mlw, height = mlh,
)

# Talking Status Frame
statusFrame = tk.LabelFrame(
	controls, text = "Status",
	bd = 4, relief = "sunken"
)
# Talking Status Canvas
status = tk.Canvas(
	statusFrame,
	width = statw,
	height = stath
)
# Mouth Shape Variable
mouthShape = status.create_line(
	statw // 4, stath // 2,
	3 * statw // 4, stath // 2,
	width = 8
)
# Mouth flags
mouthOpenFull = False
mouthClosed = True
# Blink flag
blinking = False

# Audio Samples list and maximum
micSamples = []
msLimit = 12
# Maximum samples slider function
def changeSamples(val):
	global msLimit
	micSamples.clear()
	msLimit = int(val)
# Maximum samples slider
sampleSlider = tk.Scale(
	controls, label = "Samples",
	orient = tk.HORIZONTAL, command = changeSamples,
	resolution = 1,	from_ = 8, to = 32, 
	length = statw // 4, width = h // 16
)

# Threshold variables
thresholdVar = tk.DoubleVar()
thresholdFlag = tk.BooleanVar()
# Audio Threshold Slider
thresholdSlider = tk.Scale(
	controls, label = "Threshold",
	variable = thresholdVar, orient = tk.HORIZONTAL,
	resolution = 0.1, from_ = 1.0, to = 10.0,
	length = statw // 4, width = h // 16
)

# Mouth Wobble variable and slider
wobbleChance = tk.DoubleVar()
wobbleSlider = tk.Scale(
	controls, label = "Mouth Wobble",
	variable = wobbleChance, orient = tk.HORIZONTAL,
	resolution = 0.01, from_ = 0.0, to = 0.5,
	length = statw // 4, width = h // 16
)
# Blink variable and slider
blinkChance = tk.DoubleVar()
blinkSlider = tk.Scale(
	controls, label = "Blink Probability",
	variable = blinkChance, orient = tk.HORIZONTAL,
	resolution = 0.001, from_= 0.0, to = 0.05,
	length = statw // 4, width = h // 16
)

# Image filenames and tk.PhotoImage dictionaries
imageNames = {
	"OpenSmile" : tk.StringVar(),
	"OpenAh" : tk.StringVar(),
	"OpenOh" : tk.StringVar(),
	"BlinkSmile" : tk.StringVar(),
	"BlinkAh" : tk.StringVar(),
	"BlinkOh" : tk.StringVar()
}
images = {}
# Generic Image Filename Dialog function
getImage = lambda eyes, mouth : imageNames[eyes + mouth].set(
	fdi.askopenfilename(
		parent = base, title = "Select Image: " + eyes + ", " + mouth,
		filetypes = ( ("PNG", ".png"), ("JPEG", ".jpg") )
	)
)
# Frames for all Images
frameOS = tk.LabelFrame(controls, text = "Image: Open, Smile", bd = 4)
labelOS = tk.Entry(
	frameOS, state = tk.DISABLED, width = 20,
	textvariable = imageNames["OpenSmile"]
)
buttonOS = tk.Button(
	frameOS, text = "Set Image",
	command = lambda : getImage("Open", "Smile")
)

frameOA = tk.LabelFrame(controls, text = "Image: Open, Ah", bd = 4)
labelOA = tk.Entry(
	frameOA, state = tk.DISABLED, width = 20,
	textvariable = imageNames["OpenAh"]
)
buttonOA = tk.Button(
	frameOA, text = "Set Image",
	command = lambda : getImage("Open", "Ah")
)

frameOO = tk.LabelFrame(controls, text = "Image: Open, Oh", bd = 4)
labelOO = tk.Entry(
	frameOO, state = tk.DISABLED, width = 20,
	textvariable = imageNames["OpenOh"]
)
buttonOO = tk.Button(
	frameOO, text = "Set Image",
	command = lambda : getImage("Open", "Oh")
)

frameBS = tk.LabelFrame(controls, text = "Image: Blink, Smile", bd = 4)
labelBS = tk.Entry(
	frameBS, state = tk.DISABLED, width = 20,
	textvariable = imageNames["BlinkSmile"]
)
buttonBS = tk.Button(
	frameBS, text = "Set Image",
	command = lambda : getImage("Blink", "Smile")
)

frameBA = tk.LabelFrame(controls, text = "Image: Blink, Ah", bd = 4)
labelBA = tk.Entry(
	frameBA, state = tk.DISABLED, width = 20,
	textvariable = imageNames["BlinkAh"]
)
buttonBA = tk.Button(
	frameBA, text = "Set Image",
	command = lambda : getImage("Blink", "Ah")
)

frameBO = tk.LabelFrame(controls, text = "Image: Blink, Oh", bd = 4)
labelBO = tk.Entry(
	frameBO, state = tk.DISABLED, width = 20,
	textvariable = imageNames["BlinkOh"]
)
buttonBO = tk.Button(
	frameBO, text = "Set Image",
	command = lambda : getImage("Blink", "Oh")
)

# Persona View Window Class
class personaView(tk.Toplevel):
	# Constructor
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Your Persona")
		self.resizable(False, False)
		self.canvasFrame = tk.Frame(
			self, bd = 0, relief = "raised"
		)
		self.canvasFrame.pack()
		self.canvas = tk.Canvas(self.canvasFrame)
		self.canvas.pack()
		self.setImage("OpenSmile")
	# Image Update Method
	def setImage(self, imageKey):
		self.imageKey = imageKey
		self.image = images[imageKey]
		#print(self.image, self.imageKey)
		w = self.image.width()
		h = self.image.height()
		#print(w, h)
		self.canvas.configure(height = h, width = w)

		if hasattr(self, "imageOnCanvas"):
			self.canvas.delete(self.imageOnCanvas)
		# Coordinates provided will place the image onto the canvas
		# at said coordinates with the image centered, so the
		# halfway calculations are needed
		self.imageOnCanvas = self.canvas.create_image(
			w // 2, h // 2, image = self.image
		)
# Global handle for the View Window
personaViewHandle = None
# View Toggle Button function
def openPersonaView():
	# See if we have all image files
	for frame in imageNames.keys():
		try:
			#print(frame, imageNames[frame].get())
			if imageNames[frame].get() == '':
				mbx.showerror(
					"Path Not Set",
					"Frame " + frame + " has no image set yet, please set it."
				)
				return
			elif frame not in images.keys():
				#print("Setting Frame " + frame)
				images[frame] = tk.PhotoImage(file = imageNames[frame].get())
		except tk.TclError:
			mbx.showwarning(
				"Image Not Found",
				"No image can be found for the " + frame + " frame, please set it."
			)
			return
	
	global personaViewHandle
	# Only one instance of the View can be active, make sure this is so
	if personaViewHandle == None:
		#print("No Handle Yet")
		personaViewHandle = personaView(base)
	else:
		#print("Handle Exists")
		try:
			if personaViewHandle.state() == "normal":
				#print("Handle Exists And Is Live")
				return
		except tk.TclError:
			personaViewHandle = personaView(base)
# View Window Toggle Button
viewButton = tk.Button(
	controls, text = "View Persona",
	command = openPersonaView
)

# Microphone listening toggle function
def micToggle():
	buttonState = micButton.configure("relief")[-1]
	if buttonState == "raised":
		micStream.start()
		micButton.configure(relief = "sunken")
	elif buttonState == "sunken":
		micStream.stop()
		micButton.configure(relief = "raised")
# Microphone listening toggle button
micButton = tk.Button(
	controls, text = "Listen",
	bd = 2, relief = "sunken",
	command = micToggle
)
# Microphone sample processing callback function
def micCallback(data, f, t, s):
	sample = np.linalg.norm(data)
	micSamples.insert(0, sample)
	if len(micSamples) > msLimit:
		micSamples.pop()
# Microphone Stream Object
micStream = sd.InputStream(callback = micCallback)

# Animation Loop for Mic Level and Talking Status
def animationLoop():
	global mouthShape
	global mouthOpenFull
	global mouthClosed
	global blinking
	global personaViewHandle
	if len(micSamples) > 0: # do nothing if we have no audio samples
		average = np.average(micSamples) # average the samples
		mlFrame.configure(text = format(average, "0>5.2f")) # show the average
		if average < 12.0: # Choose the color of the mic level bar
			color = "green"
		elif average < 16.0:
			color = "yellow"
		else:
			color = "red"

		micLevel.delete("all") # Redraw the mic level bar
		micLevel.create_rectangle(
			0, mlh,
			mlw, mlh - 20 * average, #mlh * np.sin(2 * time.time()) ** 2,
			fill = color, width = 0
		)
		# Change the mouth if need be
		if not thresholdFlag.get() and average >= thresholdVar.get():
			thresholdFlag.set(True)
			status.delete(mouthShape)
			mouthShape = status.create_polygon(
				statw // 4, stath // 2,
				3 * statw // 4, stath // 2,
				statw // 2, 3 * stath // 4, 
				width = 8
			)
			mouthOpenFull = True
			mouthClosed = False
		elif thresholdFlag.get() and average < thresholdVar.get():
			thresholdFlag.set(False)
			status.delete(mouthShape)
			mouthShape = status.create_line(
				statw // 4, stath // 2,
				3 * statw // 4, stath // 2,
				width = 8
			)
			mouthClosed = True
		# Get a random value to use for blink and mouth shape
		r = np.random.uniform()
		# Randomly alter the mouth if open
		if thresholdFlag.get() and micButton.configure("relief")[-1] == "sunken":
			if r < wobbleChance.get():
				if mouthOpenFull:
					status.scale(mouthShape, stath // 2, stath // 2, 1, 1/2)
				else:
					status.scale(mouthShape, stath // 2, stath // 2, 1, 2)

				mouthOpenFull = not mouthOpenFull
		# Randomly blink
		if not blinking and r < blinkChance.get():
			blinking = True
		elif blinking and r < 1.0 - blinkChance.get() * 10:
			blinking = False
		# Update the viewer
		if personaViewHandle != None:
			try:
				if personaViewHandle.state() == "normal": # Main body
					if mouthClosed:
						if blinking and personaViewHandle.imageKey != "BlinkSmile":
							personaViewHandle.setImage("BlinkSmile")
						elif not blinking and personaViewHandle.imageKey != "OpenSmile":
							personaViewHandle.setImage("OpenSmile")
					else:
						if mouthOpenFull:
							if blinking and personaViewHandle.imageKey != "BlinkAh":
								personaViewHandle.setImage("BlinkAh")
							elif not blinking and personaViewHandle.imageKey != "OpenAh":
								personaViewHandle.setImage("OpenAh")
						else:
							if blinking and personaViewHandle.imageKey != "BlinkOh":
								personaViewHandle.setImage("BlinkOh")
							elif not blinking and personaViewHandle.imageKey != "OpenOh":
								personaViewHandle.setImage("OpenOh")
			except tk.TclError:
				pass
	
	base.after(12, animationLoop) # reschedule this function
# GUI Layout
controls.pack(padx = 4, pady = 4)
controls.grid_propagate(False)

mlFrame.grid(
	row = 0, column = 0,
	rowspan = 6,
	padx = 4, pady = 4
)
micLevel.pack()
thresholdSlider.grid(
	row = 6, column = 0,
	rowspan = 2, columnspan = 2,
	sticky = tk.W, padx = 2
)
statusFrame.grid(
	row = 0, column = 1,
	rowspan = 6, columnspan = 4,
	sticky = tk.W, padx = 4, pady = 4
)
status.pack()
sampleSlider.grid(
	row = 6, column = 2,
	rowspan = 2, padx = 2
)
wobbleSlider.grid(
	row = 6, column = 3,
	rowspan = 2,
	padx = 2
)
blinkSlider.grid(
	row = 6, column = 4,
	rowspan = 2,
	sticky = tk.W
)
micButton.grid(
	row = 7, column = 5,
	sticky = tk.S
)

frameOS.grid(
	row = 0, column = 5,
	sticky = tk.N, padx = 4, pady = 4
)
labelOS.grid(row = 0, column = 0)
buttonOS.grid(row = 1, column = 0)

frameOA.grid(
	row = 1, column = 5,
	sticky = tk.N, padx = 4, pady = 4
)
labelOA.grid(row = 0, column = 0)
buttonOA.grid(row = 1, column = 0)

frameOO.grid(
	row = 2, column = 5,
	sticky = tk.N, padx = 4, pady = 4
)
labelOO.grid(row = 0, column = 0)
buttonOO.grid(row = 1, column = 0)

frameBS.grid(
	row = 3, column = 5,
	sticky = tk.N, padx = 4, pady = 4
)
labelBS.grid(row = 0, column = 0)
buttonBS.grid(row = 1, column = 0)

frameBA.grid(
	row = 4, column = 5,
	sticky = tk.N, padx = 4, pady = 4
)
labelBA.grid(row = 0, column = 0)
buttonBA.grid(row = 1, column = 0)

frameBO.grid(
	row = 5, column = 5,
	sticky = tk.N, padx = 4, pady = 4
)
labelBO.grid(row = 0, column = 0)
buttonBO.grid(row = 1, column = 0)

viewButton.grid(
	row = 6, column = 5,
	sticky = tk.S
)
# Variable Initialization
sampleSlider.set(20)
thresholdVar.set(3.5)
wobbleChance.set(0.1)
blinkChance.set(0.01)
status.create_line(
	statw // 2 - 50, stath // 6,
	statw // 2 - 50, stath // 3,
	width = 8
)
status.create_line(
	statw // 2 + 50, stath // 6,
	statw // 2 + 50, stath // 3,
	width = 8
)
# Exit Function (save state to JSON)
def shutdown():
	if mbx.askyesno(
		"Save State?",
		"Do you wish to save the program's configuration?"
	):
		configFile = open(".ccvp_conf.json", 'w')
		json.dump({
			"imageNames": {
				key : imageNames[key].get()
				for key in imageNames.keys()
			},
			"threshold" : thresholdVar.get(),
			"samples" : sampleSlider.get(),
			"wobble" : wobbleChance.get(),
			"blink" : blinkChance.get()
		}, configFile, indent = 4)
		configFile.close()
		print("Config file is: .ccvp_conf.json")
	base.destroy()
# Enter Function (load state from JSON)
def startup():
	try:
		configFile = open(".ccvp_conf.json", 'r')
	except FileNotFoundError:
		return
	
	data = json.load(configFile)
	configFile.close()
	print("Found configuration!", data)

	thresholdVar.set(data["threshold"])
	sampleSlider.set(data["samples"])
	wobbleChance.set(data["wobble"])
	blinkChance.set(data["blink"])

	for frame in data["imageNames"].keys():
		imageNames[frame].set(data["imageNames"][frame])

base.protocol("WM_DELETE_WINDOW", shutdown)
# Microphone and Animaiton Initialization
micStream.start()
base.after(2, startup)
base.after(12, animationLoop)
# GUI Initialization
base.mainloop()
# Microphone and Animation Cleanup
base.after_cancel(animationLoop)
micStream.stop()

