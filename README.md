# Maintaining the Temperature of a 3D Resin Printer Chamber Using PID Control

## Why do this?
Ventilation is a hard problem - to circumvent it, place the printer in a place away from others. Tin shed out back... But temperatures vary wildly, to place the build space in a small, but tightly controlled chamber. Can place this setup outside under the veranda. Probably what I will have to do during summer, when my shed can reach above 60C if the doors are shut. Leave the printer out in the elements, but the build chamber is at a steady, controlled temperature. Printer is on a wheeled station, so can move it outdoors.

## Shopping List

- Raspberry Pi 3B or later with its own power supply
- microSD card for Raspbian OS
- Meanwell 12v/12.5A power supply (https://www.jaycar.com.au/mean-well-150w-12v-12-5a-power-supply/p/MP3291)
- Pack of Plug to Socket Jumper Leads (https://www.jaycar.com.au/150mm-plug-to-socket-jumper-leads-40-pieces/p/WC6028)
- Pack of Plug to Plug Jumper Leads (https://www.jaycar.com.au/150mm-plug-to-plug-jumper-leads-40-piece/p/WC6024)
- Mini breadboard (https://www.jaycar.com.au/arduino-compatible-mini-breadboard-with-170-tie-points/p/PB8817)
- Pack of M3 x 10mm Tapped Metal Spacers (https://www.jaycar.com.au/m3-x-10mm-tapped-metal-spacers-pk8/p/HP0900)
- Pack of M3 x 6mm Steel Screws (https://www.jaycar.com.au/m3-x-6mm-steel-screws-pk-25/p/HP0400)
- Pack of 3mm flat washers (https://www.jaycar.com.au/3mm-flat-steel-washers-pk-25/p/HP0430)
- Pack of Eye Terminals (optional) (https://www.jaycar.com.au/eye-terminal-blue-pk-8/p/PT4614)
- 3mm MDF board to mount components (big box store)
- DS18B20 Temperature Sensor Module (https://www.jaycar.com.au/digital-temperature-sensor-module/p/XC3700)

Components for each 3D printer
- XPS Foam board (big box store)
- MDF board (big box store)
- Small piece of clear acrylic sheet (big box store)
- BTS7960 Motor Board/Driver (IBT_2 module) (https://www.ebay.com/sch/i.html?_nkw=bts7960&_sacat=0)
- Thermoelectic Peltier Refrieration Cooling System Kit (https://www.ebay.com/sch/i.html?_nkw=Thermoelectric+Peltier+Refrigeration+Cooling+System+Kit+Cooler&_sacat=0)
- DS18B20 Temperature Sensor Kit (https://www.iot-store.com.au/products/waterproof-ds18b20-temperature-sensor-kit)
- Pack of M3 x 25mm Tapped Metal Spacers (https://www.jaycar.com.au/m3-x-25mm-tapped-metal-spacers-pk8/p/HP0907)
- Xm of twin cable rated (enough for TEC module) 
        (https://www.jaycar.com.au/15a-twin-core-power-cable-sold-per-metre/p/WH3079)
            or
        (https://www.jaycar.com.au/red-heavy-duty-hook-up-wire-sold-per-metre/p/WH3040) and (https://www.jaycar.com.au/black-heavy-duty-hook-up-wire-sold-per-metre/p/WH3041)
- Xm of twin cable to connect temperature sensors & power to the two fans on the Thermoelectic Peltier Refrieration Cooling System (https://www.jaycar.com.au/red-flexible-light-duty-hook-up-wire-sold-per-metre/p/WH3010) and (https://www.jaycar.com.au/black-flexible-light-duty-hook-up-wire-sold-per-metre/p/WH3011)

Miscellaneous
- Soldering iron & solder (optional as one can just use connectors)
- electrician's tape
- 3mm and a large drill bit & drill
- crimping tool/pair of pliers
- coping saw/jigsaw
- box cutter/sharp knife

## Configuring the Raspberry Pi

### Configure the Raspbian OS
Download the official [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and install it.
Insert the microSD card into your PC/Mac using an adapter and start the Raspberry Pi Imager you have just installed.
Select the image (headless without desktop) and then the microSD under .
Select the Settings menu (wheel cog in bottom right) to get to the advanced settings.
Select a hostname, a user name, a password.
Select the SSH server.
Set the country and localization.
Set the WiFi SSID and password.
Go back and write the image.
When done, remove the microSD.

### Determine the IP address of your Raspberry Pi
Connect the Raspberry Pi to your PC monitor/TV and connect a keyboard.
Insert the microSD into the Raspberry Pi and turn it on.
After the Raspberry Pi has booted, log in using the username and password you provided when preparing the microSD.
Enter the following to get the Raspberry Pi's IP address
```
ip -f inet address | grep global
```
The IP address of the Raspberry Pi is the first four groups of numbers before the 'XXX.XXX.XXX.XXX/24' - remember these four numbers.
Power off the Raspberry Pi with
```
sudo poweroff
```
and remove it from any monitors/TV and keyboards.

### Connect to your Raspberry Pi over SSH using Windows Terminal
Start up your Raspberry Pi without any peripherals.
For windows, go to the Microsoft Store and install the 'Windows Terminal' App from the 'Microsoft Corporation'
Start up Windows Terminal and connect to your Raspberry Pi over SSH with
```
ssh <username>@<XXX.XXX.XXX.XXX>
```
where '<username>' is the username you provided during the Raspbian OS configuration, and <XXX.XXX.XXX.XXX> is the IP address of your Raspberry Pi.
You will be required to enter in the password you set during the Raspbian OS configuration.
You have connected to your Raspberry Pi over SSH successfully if you see the prompt.
To disconnect, enter
```
exit
```
after which you can close Windows Terminal.
This is the recommended method of connecting to the Raspberry Pi.

### Update the Raspbian OS
Connect to the Raspberry Pi over SSH using Windows Terminal.
Update the Raspbian OS with the following command.
```
sudo apt update && sudo apt upgrade -y
```
Do this once in a while

### Confgure the python scripts
Connect to the Raspberry Pi over SSH using Windows Terminal and update the system.
Install the following packages
```
sudo apt install -y git python3-venv python3-pip tmux
```
Create a python virtual environment inside the home directory and activate it on login with
```
python3 -m venv venv
echo "source ~/venv/bin/activate" >> ~/.bashrc
source ~/venv/bin/activate
```

Clone the repository that contains all the python scripts with
```
git clone https://github.com/crankyspock/rpi-pid-chamber.git
```
Git will create a *rpi-pid-chamber* directory and install the cloned repository there. Change into the directory just created with
```
cd rpi-pid-chamber
```
Install the required python packages to run the scripts with
```
pip install -r requirements.txt
```

### Configure the One-wire protocol for the temperature sensors
Enter the Raspberry Pi configuration utility with
```
sudo raspi-config
```
Select '3 Interface Options' > '17 1-Wire' and enable it. You will be have to reboot the OS after this. The 1-Wire protocal is now enabled.

### Mount the Raspberry Pi to the MDF board
Use the 3mm drill bit to carefully widen the mounting holes of the Raspberry Pi (they are just a fraction smaller than 3mm). This can and should be done by hand, Measure out the mounting locations on the MDF board and drill out the mounting holes. Use the M3 X 10mm Tapped Metal Spacers, the 3mm Steel Flat Washers and the 3mm x 6mm Screws to mount the Raspberry Pi to the MDF board.

### Mount the mini breadboard to the MDF board
The mini breadboard is there to facilitate the connections between the Raspberry Pi and peripherals. This is not ideal as there is exposed wiring that can be dislodged if not careful, but it is functional and quick enough to mitigate this risk.
The mini breadboard usually comes with double-sided adhesive tape on the underside, so stick it to the MDF board in an accessible position.

### Wire up the Raspberry Pi to the mini breadboard
Turn off the Raspberry Pi while doing any wiring!
Use the [Raspberry Pip Pinout Reference](https://pinout.xyz/) to assist in wiring up the SIX connections to the mini breadboard.
The [DS18B20 Temperature Sensor Module](https://www.jaycar.com.au/digital-temperature-sensor-module/p/XC3700) comes with three pins.
![DS18B20 Temperature Sensor Module](https://www.jaycar.com.au/medias/sys_master/images/images/9725855367198/XC3700-digital-temperature-sensor-modulegallery5-300.jpg)

Take note which pin is the signal (S), which is the +ve (3.3V) and which is the -ve (GND).
Insert the module pins into the mini breadboard on the edge so that the bulk of the module hangs off the mini breadboard. Take note which row of the mini breadboard is associated with the signal (S), the 3.3V and the GND of the module.
Using the plug to socket jumper leads, connect the 3.3V row to *Physical Pin 1* on the Raspberry Pi's GPIO.
Now connect the GND row to any of the following: Physical Pin 6/9/14/20/30/34/39. Most people will just use *Physical Pin 9*.
Now connect the S row to *Physical Pin 7*.
Any additonal temperature sensors will be connected into and make use of these three S, 3.3V and GND rows. Each temperature sensor has a unique ID which identifies it on the S-row/1-Wire, and one can have as many different sensors connected together in this way.
The last wiring to the mini breadboard is to connect each of the following to its own row on the mini breadboard: *Physical Pin 2* (5V), *Physical Pin 6* (GND) and *Physical Pin 17* (3.3V). These 5V & GND rows are used to power the IBT_2 module/driver, while the 3.3V row is used to enable the module/driver. Any additional IBT_2 modules/drivers will also make use of these three rows.
If one runs out of connections in a row, remember that the full row can be connected to another empty row using a plug to plug jumper lead.

Turn on the Raspberry Pi and connect to it over SSH.
Change into the *rpi-pid-chamber* directory and run the *sensors.py* python script
```
cd ~/rpi-pid-chamber
python sensors.py
```
This script will print out the sensor ID and the temperature of all the DS18B20 sensors connected to the Raspberry Pi. Placing a finger on the sensor will increase the temperature that is being read - this can be used to identify the sensor ID when there are multiple sensors connected.
Take note of the ID of the DS18B20 Temperature Sensor Module - this sensor is used to measure the ambient temperature of the room.
The Raspberry Pi is now set up!

## Wiring up the power supply
Measure out the mounting holes at the top and bottom edge of the power supply onto the MDF board. Using an old power cable (or old kettle cord), cut off the appliance end and strip the insulation from the wires using a sharp knife. Crimp an eye terminal onto the exposed wire using a crimping tool or a pair of pliers (I just soldered the wires onto the eye terminal).
Cut a short length of the twin core or heavy duty hook-up wire to connect the power supply to the IBT_2 module/driver. Strip the insulation from both ends of the wire and crimp/solder eye terminals to one end of the wire.
Screw the eye terminals to the power supply.
Brown power cord - Live
Blue power cord - Neutral
Yellow/Green power cord - Earth
Red core/hookup - V+
Black core/hookup - V-

Cut and strip both ends of the twin cable or light duty hook-up wire to provide power to the fans on the Thermoelectic Peltier Refrieration Cooling System. Crimp/solder eye terminals to one end of the wire and screw the eye terminals to the power supply using the empty connection points.
Red core/hookup - V+
Black core/hookup - V-

## Wiring up the temperature sensors
Assemble the DS18B20 Temperature Sensor Kit as shown [here](https://www.youtube.com/watch?v=mMoRSgNoOoE)
Using the plug to plug jumper leads (if close enough), connect the S row on the mini breadboard to the D1 socket of the black connector, the 3.3V row on the mini breadboard to the +ve socket, and the GND row to the -ve socket on the black connector.
Run the *sensors.py* python script to confirm the sensor is recognised so the sensor ID can be recognised
```
cd ~/rpi-pid-chamber
python sensors.py
```
Take note of the sensor ID as it will be required later.
Note that longer wires can be used to allow the temperature sensor kit to be located further away from the Raspberry Pi. Lengthen to taste...

## Wiring up the IBT_2 module
Measure out the mounting hole spacing of the IBT_2 module/driver onto the MDF board.
Drill out 3mm holes and mount the M3 x 25mm Tapped Metal Spacers to the MDF board using the M3 x 6mm Steel Screws & washers.
Screw the V+ wire from the power supply to the B+ terminal block.
Screw the V- wire from the power supply to the B- terminal block.
Using the plug to socket jumper leads, connect the following:
Mini bread board    ->  IBT_2
5V row              ->  Pin 7 (Vcc)
GND row             ->  Pin 8 (GND)
3.3V row            ->  Pin 3 (R_EN)
3.3V row            ->  Pin 4 (L_EN)

Using the socket to socket jumper leads, connect the following:
Raspberry Pi        ->  IBT_2
Physical Pin 13     ->  Pin 1 (RPWM)
Physical Pin 15     ->  Pin 2 (LPWM)
Note that it is not important which of of these two pins are connected to which. They can be set in the software.

Strip the wires at the ends of the twin core/heavy duty hook-up wires. Connect the red and black wires of one end to the M+ and M- terminal block.

Carefully turn the IBT_2 module/driver upside-down so the heat sink is facing upwards and screw the module to the tapped metal spacers.

## Construct the chamber out of XPS foam
Make a close-fitting MDF skirt to replace the 3D printer cover. The width must be able to accomodate the thickness of the XPS foam you are using. Measure out and cut the sides and the top.
In one of the sides, use a router/sharp knife to make a rebate for an acrylic window to monitor print progress.
In the top, create an opening to accomodate the small heatsink of the TEC Cooler. Create a rebate for an acrylic support block for the TEC to rest on. The acrylic support must have a rectangular opening the same size as that in the XPS foam top. On the inside face of the top, cut out two relief channels to allow better airflow out of the small heatsink.
Glue all the components together with Gorilla glue and prime the chamber with two coats of Mod Podge to protect the chamber.
Assemble the chamber with the TEC and the acrylic support plate.
Place a small hole in the top of the chamber to pass the power cables through for the small fan.
Place a hole near the bottom of the chamber so the temperature sensor is just above the resin vat.

## Wiring up the thermoelectic module
Connect/solder the other end of the twin core/heavy duty hook-up wire to the peltier module.
Connect/solder the end of the twin core/light duty hook-up wire from the power supply to the two fans on the Thermoelectic Peltier Refrieration Cooling System.

## Test the system
Insert the temperature sensor into the chamber and seal with Blue Tack.
Connect the power supply to the wall socket and turn it on - the two fans on the TEC will produce significant noise, as they are runnng at full power. They are also VERY cheap, so their bearings will add to the noise after a short while. Since my setup is in a shed out back, the noise is not a problem to me, so I have not incorporated a solution. Another IBT_2 could be used to control the fans, but the system has better efficiency when the heatsinks are flushed as quickly as possible. The only advice I can give is to just replace the fans with good quality ones.
Then log into the Raspberry Pi over SSH, change into the directory and run the *temperature.py* script.
```
cd ~/rpi-pid-chamber
python temperature.py --help
python temperature.py 30
```
The temperature inside the chamber should start increasing/decrease depending on the target temperature.
If the temperature is moving the wrong way, then stop the script with *CTRL-C* and change the pin settings of the script
```
python temperature.py 30 --cooling-pin 22 --heating-pin 27
```
When all is in order, log the output so you can examine the csv data in Excel.
Use this script to optimise the P, I & D parameters. Play around... The ideal is that the system settles down with the TEC havig a duty cycle around 20%. Small fluctuations around the target temperature results in the duty cycle varying in the range 10%-30%. One can get a +-0.1C variation from the target temperature.