'''
Install the dependencies using the following command:

pip install w1thermsensor RPi.GPIO

For TEC1-12706 Thermoelectric Cooler:
About 50W with 12V/6A
P - 20.0
I - 0.3
D - 0.0

For TEC1-12708 Thermoelectric Cooler:
About 68W with 12V/8A
P - 15.0
I - 0.2
D - 0.0
30C / 17C @ 21%
Power draw from wall outlet: 66W @ maximum, 36W @ 30C
'''

import argparse
import time
import datetime
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor, Sensor

parser = argparse.ArgumentParser(description="Maintains the temperature in the enclosure using PID control")
parser.add_argument('temperature', help='Target temperature (\N{DEGREE SIGN}C)', type=float)
parser.add_argument('-p', metavar='proportional', dest='proportional_gain', help='Proportional gain to use in PID calculations (default is 15.0)', required=False, default=15.0, type=float)
parser.add_argument('-i', metavar='integral', dest='integral_gain', help='Integral gain to use in PID calculations (default is 0.2)', required=False, default=0.2, type=float)
parser.add_argument('-d', metavar='derivative', dest='derivative_gain', help='Derivative gain to use in PID calculations (default is 0.0)', required=False, default=0.0, type=float)
parser.add_argument('-s', metavar='sampling-interval', dest='pid_sampling_interval', help='PID sampling interval in seconds (default is 2.0)', required=False, default=2.0, type=float)
parser.add_argument('-w', metavar='windup', dest='windup', help='To prevent windup, I & D calculations are not used if the temperature error is greater than this value (default is 2.0)', required=False, default=2.0, type=float)
parser.add_argument('--cool-pin', metavar='cooling-pwm-pin', dest='cooling_pwm_pin', help='BCM pin used for PWM cooling (default is pin 27)', required=False, default=27, type=int)
parser.add_argument('--heat-pin', metavar='heating-pwm-pin', dest='heating_pwm_pin', help='BCM pin used for PWM heating (default is pin 22)', required=False, default=22, type=int)
parser.add_argument('--pwm-frequency', metavar='pwm-frequency', dest='pwm_frequency', help='PWM frequencies less than 2000Hz will dammage peltier/TEC modules (default is 5000)', required=False, default=5000, type=int)
parser.add_argument('--ambient-sensor', metavar='ambient-temp-sensor', dest='ambient_sensor_id', help='1-Wire senor ID for ambient temperature sensor', required=False, default='011441bdcfaa')
parser.add_argument('--enclosure-sensor', metavar='enclosure-sensor-id', dest='enclosure_sensor_id', help='1-Wire sensor ID for enclosure temperature sensor', required=False, default='01191136490c')
parser.add_argument('--log', metavar='log-name', dest='log_name', help='Log data to this filename', required=False, default=None)
args = parser.parse_args()

output_pins = (args.cooling_pwm_pin, args.heating_pwm_pin)
cooler_on = False
heater_on = False
pwm_duty_cycle = 10
previous_error = 0.0
cumulative_error = 0.0
previous_time = datetime.datetime.now()
time.sleep(args.pid_sampling_interval) # Initialise a time interval for PID calculations

GPIO.setmode(GPIO.BCM)
GPIO.setup(output_pins, GPIO.OUT)
cooler = GPIO.PWM(args.cooling_pwm_pin, args.pwm_frequency)
heater = GPIO.PWM(args.heating_pwm_pin, args.pwm_frequency)
print(f'\nRaspberry Pi BCM pin configuration for the IBT_2 module:\nCooling pin {args.cooling_pwm_pin}\nHeating pin {args.heating_pwm_pin}\nPWM Frequency: {args.pwm_frequency}Hz')

enclosure_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=args.enclosure_sensor_id)
ambient_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=args.ambient_sensor_id)

session_details = str(f'Starting Time: {time.strftime("%Y%m%d-%H%M%S", time.localtime())}\nTarget temperature: {args.temperature}\nProportional Gain: {args.proportional_gain}\nIntegral Gain: {args.integral_gain}\nDerivative Gain: {args.derivative_gain}\n')
csv_header = str(f'Time,Chamber Temp,Ambient Temp,Proportional_Response,Integral_Response,Derivative_Response,Duty_Cycle,Heater_On,Cooler_On\n')
if args.log_name:
    with open(args.log_name, 'a') as f:
        f.write(session_details)
        f.write(csv_header)

try:
    while True:
        current_temp = enclosure_sensor.get_temperature()
        ambient_temp = ambient_sensor.get_temperature()
        current_time = datetime.datetime.now()
        current_error = args.temperature - current_temp

        proportional_response = args.proportional_gain * current_error

        # Only calculate the integral & derivative response when close to the target temperature - prevents windup
        if abs(current_error) < args.windup:
            cumulative_error = cumulative_error + current_error * ((current_time - previous_time).total_seconds())
            integral_response = args.integral_gain * cumulative_error
            derivative_response = args.derivative_gain * (current_error - previous_error)/args.pid_sampling_interval
        else:
            cumulative_error = 0.0
            integral_response = 0.0
            derivative_response = 0.0

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
                print('Heater is now on')
        else: # Cooler must be on
            if cooler_on:
                cooler.ChangeDutyCycle(abs(pwm_duty_cycle))
            else:
                if heater_on:
                    heater.stop()
                    heater_on = False
                cooler.start(abs(pwm_duty_cycle))
                cooler_on = True
                print('Cooler is now on')

        print(f'{time.strftime("%H:%M:%S", time.localtime())} Tc: {current_temp:.1f}\N{DEGREE SIGN}C | Ta: {ambient_temp:.1f}\N{DEGREE SIGN}C | P: {int(proportional_response)}% | I: {int(integral_response)}% | D: {int(derivative_response)}% | DC: {int(pwm_duty_cycle)}% | Heater_On: {heater_on} | Cooler_On: {cooler_on}')
        if args.log_name:
            with open(args.log_name, 'a') as f:
                f.write(f'{time.strftime("%Y%m%d-%H%M%S", time.localtime())},{current_temp:.1f},{ambient_temp:.1f},{int(proportional_response)},{int(integral_response)},{int(derivative_response)},{int(pwm_duty_cycle)},{heater_on},{cooler_on}\n')

        previous_error = current_error
        previous_time = current_time
        time.sleep(args.pid_sampling_interval)
except KeyboardInterrupt: # Ctrl-C to exit
    cooler.stop()
    print(f'\nCooler has been stopped')
    heater.stop()
    print(f'Heater has been stopped')
    GPIO.cleanup()
    print(f'All pins set to input and cleared')
