import time
from traceback import print_list
import RPi.GPIO as GPIO

#pin_list=[4,27,21,13,26,23,22,12,20,19,24,25,16,5,6,17,18,10,9,11,8]
#pin_list=[4]
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)
GPIO.setwarnings(False)

while True:
  GPIO.output(7,GPIO.LOW)
  time.sleep(0.5)
  GPIO.output(7,GPIO.HIGH)
  time.sleep(0.5)