# Virtual Persona
### A Streaming Utility
### Written by Charlie Cook

## Description
This program detects the volume level of your system's main input audio stream (usually a microphone) with the `sounddevice` module, and uses it to animate user-generated frames of an avatar of the user.
Six total frames can be provided to the program: One smiling, one vocalizing an "Ah" sound, and one vocalizing and "Oh" sound, with two groups of these, either with eyes open or eyes blinking.
The program overall uses `tkinter` for the GUI, which is a standard but not pre-installed Python module on most systems, make sure you select Tcl/tk when installing Python on your system.

## How To Use
Simply enter `python ccVirtualPersona.py` in a command prompt or shell.
You are prompted on exiting the program if you wish to save your configuration.
If so, your paths to the animation frames and the values for the four sliders will be written to a file and automatically reloaded when next starting the program.
### Required Modules
* `sounddevice` (for microphone volume sampling)
* `tkinter` (for GUI)
* `numpy` (for sample processing and random numbers)
* `json` (for config file I/O, should be standard)
