import rpi.GPIO as GPIO

lightPin = 12
dutyCycle = 100
FREQUENCY = 50
delta = 20

GPIO.setmode(GPIO.BCM) 
GPIO.setup(lightPin, GPIO.OUT)
pwm = GPIO.PWM(lightPin, FREQUENCY)
pwm.start(dutyCycle) # start the PWM

while(True):
    input = raw_input("Set duty cycle: ")
    if input == "down":
        dutyCycle -= delta
    elif input == "up":
        dutyCycle += delta
    else:
        dutyCycle = int(input)
    
    pwm.ChangeDutyCycle(dutyCycle)