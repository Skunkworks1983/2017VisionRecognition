#!/usr/bin/python 
#
# Script for boot time configuration
# Checks for presence of a jumper on GPIO, uses that to
# determine role in the robot network - gear or goal (turret).
# This allows us to use a single image on both RPi's.
#
# Connect GPIO 21 (pin 40) to GND (pin 39) to set it as gearPI.
# Connect GPIO 26 (pin 37) to GND (pin 39) to set it as goalPI.
# Connect no pins to set it as genericPI.
#
import os
import RPi.GPIO as GPIO
import filecmp

def configData(IP):
        return str('#static ip\ninterface eth0\nstatic ip_address='+IP+'/24\nstatic routers=10.19.83.1\nstatic domain_name_servers=8.8.8.8 8.8.4.4\n')

def lowPowerConfig():
        os.system("/opt/vc/bin/tvservice -o");
        # turn off wifi
        os.system('sudo ifconfig wlan0 down')


GPIO.setmode(GPIO.BCM)  # use GPIO numbering (https://pinout.xyz/ was helpful here)
GearSignalPin = 21
GoalSignalPin = 26
GPIO.setup(GearSignalPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # so it reads high if not grounded
GPIO.setup(GoalSignalPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # so it reads high if not grounded

gearIP = '10.19.83.6'
goalIP = '10.19.83.7'

gearPI = 'gear-pi'
goalPI = 'goal-pi'
genericPI = 'generic-pi'

generic = False

# read the dhcpconf file to see if need changing
dhcpconf = '/etc/dhcpcd.conf'
with open(dhcpconf, 'r') as myfile:
        dhcpConfigData=myfile.read()

# get the current hostname
with open('/etc/hostname','r') as myhfile:
	oldHostname = myhfile.read()

if not GPIO.input(GearSignalPin):
	print 'Jumper on gear pin'
	desiredHostname = gearPI
	desiredIP = gearIP
	wrongIP = goalIP

	# turn hdmi off
	lowPowerConfig()
elif not GPIO.input(GoalSignalPin):
	print 'Jumper on goal pin'
	desiredHostname = goalPI
	desiredIP = goalIP
	wrongIP = gearIP

	#turn hdmi off
	lowPowerConfig()
else:
	print 'No jumpers installed'
	# do we need to revert IP and/or hostname?
	if gearIP in dhcpConfigData or goalPI in oldHostname or goalIP in dhcpConfigData or goalPI in oldHostname:
		if goalIP in dhcpConfigData:
            print 'goalIP'
			dhcpConfigData = dhcpConfigData.replace(configData(goalIP),'#generic no static')
		if gearIP in dhcpConfigData:
            print 'gearIP'
			dhcpConfigData = dhcpConfigData.replace(configData(gearIP),'#generic no static')
		with open(dhcpconf, 'w') as myfile:
			myfile.write(dhcpConfigData)
			
		# update hostname - requires changes in two locations
		with open('/etc/hostname','w') as myhfile:
			myhfile.write(genericPI + '\n')
			
		with open('/etc/hosts','r') as myhostsfile:
			oldhosts = myhostsfile.read()
		with open('/etc/hosts','w') as myhostsfile:
			myhostsfile.write(oldhosts.replace(oldHostname, genericPI + '\n'))
		# restart using new config
		print 'Used generic'
		os.system('sudo shutdown -r now')
	generic = True
	
# do we need to update IP and/or hostname?
if not generic:
        if desiredIP not in dhcpConfigData or desiredHostname not in oldHostname:

                # update dhcpconf with static IP info
                if goalIP not in dhcpConfigData and gearIP not in dhcpConfigData:
                        # first time here, append the static IP config
                        dhcpConfigData += configData(desiredIP)
                else:
                        # swap identities
                        dhcpConfigData = dhcpConfigData.replace(wrongIP, desiredIP)
                with open(dhcpconf, 'w') as myfile:
                        myfile.write(dhcpConfigData)

                # update hostname - requires changes in two locations
                with open('/etc/hostname','w') as myhfile:
                        myhfile.write(desiredHostname+"\n")
                with open('/etc/hosts','r+') as myhostsfile:
                        oldhosts = myhostsfile.read()
                        myhostsfile.write(oldhosts.replace(oldHostname, desiredHostname+"\n"))
                        
                # restart using new config
                print 'did not use generic'
                os.system('sudo shutdown -r now')

# Check for tracker daemon startup
if not os.path.exists('/lib/systemd/system/tracker.service') or not open('/lib/systemd/system/tracker.service', 'r').read() == open('/home/pi/2017VisionRecognition/tracker.service', 'r').read() :
    print 'updating tracker startup daemon'
    os.system("cp -f /home/pi/2017VisionRecognition/tracker.service /lib/systemd/system/tracker.service")
    os.system("chmod 755 /lib/systemd/system/tracker.service")
    os.system("systemctl daemon-reload")
    os.system("systemctl enable tracker.service")
    os.system('sudo shutdown -r now')

