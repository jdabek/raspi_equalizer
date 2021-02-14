import RPi.GPIO as GPIO

pins = [26,19,13,6,5,16,20,21]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pins,GPIO.OUT)
GPIO.output(pins,GPIO.LOW)
