#!/usr/bin/python 
#
# Script for boot time configuration
# Checks for presence of a jumper on GPIO, uses that to
# determine role in the robot network - gear or goal (turret).
# This allows us to use a single image on both RPi's.
#
# Connect GPIO 21 (pin 40) to GND (pin 39) to set it as gear-pi.
# Connect GPIO 26 (pin 37) to GND (pin 39) to set it as goal-pi.
# Connect no pins to set it as generic-pi.
#
import os
import RPi.GPIO as GPIO

def configData(IP):
    return str('#static ip\ninterface eth0\nstatic ip_address='+IP+'/24\nstatic routers=10.19.83.1\nstatic domain_name_servers=8.8.8.8 8.8.4.4\n')

GPIO.setmode(GPIO.BCM)  # use GPIO numbering (https://pinout.xyz/ was helpful here)
GearSignalPin = 21
GoalSignalPin = 26
GPIO.setup(SignalPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # so it reads high if not grounded

gearIP = '10.19.83.6'
goalIP = '10.19.83.7'

gear-pi = 'gear-pi'
goal-pi = 'goal-pi'
generic-pi = 'generic-pi'

# read the dhcpconf file to see if need changing
dhcpconf = '/etc/dhcpcd.conf'
with open(dhcpconf, 'r') as myfile:
	dhcpConfigData=myfile.read()

# get the current hostname
with open('/etc/hostname','r') as myhfile:
	oldHostname = myhfile.read()

if not GPIO.input(GearSignalPin):
    print 'Jumper on gear pin, setting gearPi'
    desiredHostname = gear-pi
	desiredIP = gearIP
	wrongIP = goalIP
elif not GPIO.input(GoalSignalPin):
    print 'Jumper on goal pin, setting goalPi'
	desiredHostname = goal-pi
	desiredIP = goalIP
	wrongIP = gearIP
else:
    print 'No jumpers installed, reverting to dhcp'
    
    # do we need to revert IP and/or hostname?
    if gearIP in dhcpConfigData or gear-pi in oldHostname or goalIP in dhcpConfigData or goal-pi in oldHostname:
        if goalIP in dhcpConfigData:
            dhcpConfigData.replace(configData(goalIP),'')
        if gearIP in dhcpConfigData:
            dhcpConfigData.replace(configData(gearIP),'')
            
        with open(dhcpconf, 'w') as myfile:
            myfile.write(dhcpConfigData)
            
        # update hostname - requires changes in two locations
        with open('/etc/hostname','w') as myhfile:
            myhfile.write(generic-pi + '\n')
            
        with open('/etc/hosts','r') as myhostsfile:
            oldhosts = myhostsfile.read()
        with open('/etc/hosts','w') as myhostsfile:
            myhostsfile.write(oldhosts.replace(oldHostname, generic-pi + '\n'))
        # restart using new config
        os.system('sudo shutdown -r now')
    exit()
            
# turn off wifi
#os.system('sudo ifconfig wlan0 down')

# do we need to update IP and/or hostname?
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
	os.system('sudo shutdown -r now')
