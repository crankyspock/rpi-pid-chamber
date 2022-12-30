import time
from traceback import print_list
import RPi.GPIO as GPIO

pin_list=[23,24]
#pin_list=[4]
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_list,GPIO.OUT)
GPIO.setwarnings(False)

while True:
  GPIO.output(pin_list,GPIO.LOW)
  time.sleep(0.5)
  GPIO.output(pin_list,GPIO.HIGH)
  time.sleep(0.5)