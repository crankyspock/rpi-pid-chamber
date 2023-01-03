import argparse
import configparser
import time
import datetime
import math
import itertools
from collections import deque
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor, Sensor

parser = argparse.ArgumentParser(description="Control the temperature of the chamber specified in the config file")
parser.add_argument('--config', metavar='config-filename', dest='config_filename', help='Config filename containing the chamber definitions (default is config.txt', required=False, default='config.txt')
parser.add_argument('--log', metavar='enable-logging', dest='enable_logging', help='Enable logging (default is False)', required=False, default=False)
parser.add_argument('--integral-response', metavar='ontegral-response', dest='integral_response', help='Provide an integral-response on start if within the integral range (default is 0.0)', required=False, default=0.0, type=float)
args = parser.parse_args()
config = configparser.ConfigParser()
config.read(args.config_filename)
chamber = config.sections()[0]

output_pins = (config.getint(chamber, 'cooling-pin'), config.getint(chamber, 'heating-pin'))
GPIO.setmode(GPIO.BOARD)
GPIO.setup(output_pins, GPIO.OUT)
cooler = GPIO.PWM(config.getint(chamber, 'cooling-pin'), config.getint(chamber, 'pwm-frequency'))
heater = GPIO.PWM(config.getint(chamber, 'heating-pin'), config.getint(chamber, 'pwm-frequency'))
print(f'\nRaspberry Pi Board pin configuration for the IBT_2 module:\nCooling pin {config.getint(chamber, "cooling-pin")}\nHeating pin {config.getint(chamber, "heating-pin")}\nPWM Frequency: {config.getint(chamber, "pwm-frequency")}Hz')

chamber_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=config.get(chamber, 'chamber-sensor-id'))
ambient_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=config.get(chamber, 'ambient-sensor-id'))

session_details = str(f'Chamber: {chamber}\nStarting Time: {time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())}\nTarget temperature: {config.getfloat(chamber, "target-temperature")}\nProportional Gain: {config.getfloat(chamber, "proportional-gain")}\nIntegral Gain: {config.getfloat(chamber, "integral-gain")}\nDerivative Gain: {config.getfloat(chamber, "derivative-gain")}\nSampling Interval: {config.getfloat(chamber, "sampling-interval")}')
csv_header = str(f'Date,Time,Chamber Temp,Ambient Temp,Proportional_Response,Integral_Response,Derivative_Response,Duty_Cycle,RMSError 1min,RMSError 5min,RMSError 10min,Mode\n')
print(session_details)
print('\nCTRL-C to exit.....\n')
if args.enable_logging:
    logname = str(config.get(chamber, 'logname-prefix') + '-' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.log')
    with open(logname, 'a') as f:
        f.write(session_details)
        f.write(csv_header)

cooler_on = False
heater_on = False
pwm_duty_cycle = 10
previous_error = 0.0
cumulative_error = args.integral_response / config.getfloat(chamber, "integral-gain")
error_square = deque([], maxlen=int(600/config.getfloat(chamber, 'sampling-interval')))
previous_time = datetime.datetime.now()
time.sleep(config.getfloat(chamber, 'sampling-interval')) # Initialise a time interval for PID calculations

try:
    while True:
        current_temp = chamber_sensor.get_temperature()
        ambient_temp = ambient_sensor.get_temperature()
        current_time = datetime.datetime.now()
        current_error = config.getfloat(chamber, "target-temperature") - current_temp
        error_square.appendleft(current_error ** 2)

        proportional_response = config.getfloat(chamber, "proportional-gain") * current_error

        cumulative_error = cumulative_error + current_error * ((current_time - previous_time).total_seconds())
        if abs(config.getfloat(chamber, 'windup')/config.getfloat(chamber, "integral-gain")) < abs(cumulative_error): # Clamp the cumulative error to prevent windup
            cumulative_error = config.getfloat(chamber, 'windup')/config.getfloat(chamber, "integral-gain") if 0 < cumulative_error else -1*(config.getfloat(chamber, 'windup')/config.getfloat(chamber, "integral-gain"))
        integral_response = config.getfloat(chamber, "integral-gain") * cumulative_error
        derivative_response = config.getfloat(chamber, "derivative-gain") * (current_error - previous_error)/config.getfloat(chamber, 'sampling-interval')

        calculated_response = proportional_response + integral_response + derivative_response

        # Duty Cycle cannot be greater than 100%
        if calculated_response <= -100:
            pwm_duty_cycle = int(-100)
        elif calculated_response >= 100:
            pwm_duty_cycle = int(100)
        else:
            pwm_duty_cycle = calculated_response

        if pwm_duty_cycle > 0: # Heater must be on
            if heater_on:
                heater.ChangeDutyCycle(pwm_duty_cycle)
            else:
                if cooler_on:
                    cooler.stop()
                    cooler_on = False
                heater.start(pwm_duty_cycle)
                heater_on = True
        else: # Cooler must be on
            if cooler_on:
                cooler.ChangeDutyCycle(abs(pwm_duty_cycle))
            else:
                if heater_on:
                    heater.stop()
                    heater_on = False
                cooler.start(abs(pwm_duty_cycle))
                cooler_on = True

        rms_1min = math.sqrt(sum(itertools.islice(error_square, 0, int(60/config.getfloat(chamber, 'sampling-interval'))))/(len(error_square) if len(error_square) < int(60/config.getfloat(chamber, 'sampling-interval')) else int(60/config.getfloat(chamber, 'sampling-interval'))))
        rms_5min = math.sqrt(sum(itertools.islice(error_square, 0, int(300/config.getfloat(chamber, 'sampling-interval'))))/(len(error_square) if len(error_square) < int(300/config.getfloat(chamber, 'sampling-interval')) else int(300/config.getfloat(chamber, 'sampling-interval'))))
        rms_10min = math.sqrt(sum(itertools.islice(error_square, 0, int(600/config.getfloat(chamber, 'sampling-interval'))))/(len(error_square) if len(error_square) < int(600/config.getfloat(chamber, 'sampling-interval')) else int(600/config.getfloat(chamber, 'sampling-interval'))))

        print(f'{time.strftime("%H:%M:%S", time.localtime())} Tc: {current_temp:.1f}\N{DEGREE SIGN}C | Ta: {ambient_temp:.1f}\N{DEGREE SIGN}C | P: {int(proportional_response): >3}% | I: {int(integral_response): >3}% | D: {int(derivative_response): >3}% | DC: {int(pwm_duty_cycle): >3}% | RMSErr1: {rms_1min:.2f} | RMSErr5: {rms_5min:.2f} | RMSErr10: {rms_10min:.2f} | {"Heater On" if heater_on else "Cooler On"}')
        if args.enable_logging:
            with open(logname, 'a') as f:
                f.write(f'{time.strftime("%Y/%m/%d,%H:%M:%S", time.localtime())},{current_temp:.1f},{ambient_temp:.1f},{int(proportional_response)},{int(integral_response)},{int(derivative_response)},{int(pwm_duty_cycle)},{rms_1min:.2f},{rms_5min:.2f},{rms_10min:.2f},{"Heater On" if heater_on else "Cooler On"}\n')

        previous_error = current_error
        previous_time = current_time
        time.sleep(config.getfloat(chamber, 'sampling-interval'))
except KeyboardInterrupt: # Ctrl-C to exit
    cooler.stop()
    print(f'\nCooler has been stopped')
    heater.stop()
    print(f'Heater has been stopped')
    GPIO.cleanup(output_pins)
    print(f'All pins set to input and cleared')