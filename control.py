import argparse
import configparser
import time
import datetime
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor, Sensor

parser = argparse.ArgumentParser(description="Control the temperature of all chambers specified in the config file")
parser.add_argument('--config', metavar='config-filename', dest='config_filename', help='Config filename containing the chamber definitions (default is config.txt', required=False, default='config.txt')
parser.add_argument('--log', metavar='enable-logging', dest='log_bool', help='Enable logging (default is False)', required=False, default=False)
args = parser.parse_args()
config = configparser.ConfigParser()
config.read(args.config_filename)

output_pins = (config.sections()[0].getint('cooling-pin'), config.sections()[0].getint('heating-pin'))
GPIO.setmode(GPIO.BOARD)
GPIO.setup(output_pins, GPIO.OUT)
cooler = GPIO.PWM(config.getint('cooling-pin'), config.getint('pwm-frequency'))
heater = GPIO.PWM(config.getint('heating-pin'), config.getint('pwm-frequency'))
print(f'\nRaspberry Pi Board pin configuration for the IBT_2 module:\nCooling pin {config.getint("cooling-pin")}\nHeating pin {config.getint("heating-pin")}\nPWM Frequency: {config.getint("pwm-frequency")}Hz')

chamber_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=config.sections()[0]['chamber-sensor'])
ambient_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=config.sections()[0]['ambient-sensor'])

session_details = str(f'Chamber: {config.sections()[0]}\nStarting Time: {time.strftime("%Y%m%d-%H%M%S", time.localtime())}\nTarget temperature: {config.sections()[0]["target-temperature"]}\nProportional Gain: {config.sections()[0]["proportional-gain"]}\nIntegral Gain: {config.sections()[0]["integral-gain"]}\nDerivative Gain: {config.sections()[0]["derivative-gain"]}\n')

GPIO.cleanup(output_pins)