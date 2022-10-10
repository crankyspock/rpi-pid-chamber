# Install requirements with:
#    pip install w1thermsensor

import time
from w1thermsensor import W1ThermSensor

print(f'CTRL-C to exit...')
print(f'DS18B20 Temperature Sensors discovered:\n')

while True:
    for sensor in W1ThermSensor.get_available_sensors():
        print(f"Sensor {sensor.id} has temperature {sensor.get_temperature():.1f}\N{DEGREE SIGN}C")
    time.sleep(5)