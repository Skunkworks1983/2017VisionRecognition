import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
if GPIO.input(4): os.system('sudo hostname gear-pi')
else: os.system('sudo hostname goal-pi')