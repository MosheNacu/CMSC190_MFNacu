#Hardware Connections
	- Connect Button to GPIO Pin 18
	- Connect left buzzer to GPIO Pin 26
	- Connect right buzzer to GPIO Pin 12
	- Connect Raspberry Pi Camera
	
#Installation
Install Raspbian OS into an SD card for a Raspberry Pi
	- https://www.raspberrypi.org/downloads/raspbian/
Install Python 3
	- https://docs.python-guide.org/starting/install3/linux/
Install OpenCV 2
	- https://pypi.org/project/opencv-python/
Install Packages
	- python3 -m pip install numpy
	- sudo apt-get install rpi.gpio
Copy pathfinder.py to desired folder
	#Presentation Mode
		- sudo nano /home/pi/.bashrc
		- add “python /home/pi/your_directory/pathfinder.py” to the last line and save
		- to remove, just delete the last line
	#Headless Mode
		- comment out line 163 from python.py
		- sudo nano /home/pi/.bashrc
		- add “python /home/pi/your_directory/pathfinder.py” to the last line and save
		- cd home/pi/.config/lxsession/LXDE-pi/
		- nano autostart
		- add “@lxterminal” to the last line and save
		- sudo restart
		- to remove follow https://stackoverflow.com/questions/24774762/when-i-boots-up-my-raspberry-pi-desktop-become-black and remove last line from .bashrc

	



