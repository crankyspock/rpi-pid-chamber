# Maintaining the Temperature of a 3D Resin Printer Chamber Using PID Control

## Why do this?

Safety issues had me relocate my printer to the shed. This unheated tin shed gets wild temperature swings so I had to come up with a solution to manage temperatures. A large enclosure for the entire printer is feasible, but has the drawback of having to open the enclosure to initiate the print from the touchscreen. I decided to replace the printer's cover with a XPS foam chamber that has a thermoelectric cooler/heater (TEC) attached, controlled by a Raspberry Pi running a Python script implementing PID controls. This allows me to control the printer without disturbing the chamber, so temperature control is maintained at all times. I seem to be able to maintain temperatures within +-0.2 C repeatably. Power-wise, when at the target temperature, the system is drawing around 30-35W from the wall, so it is not power-hungry. The system is surprisingly quick and simple to put together - well within the capabilities of most people. 
Some stats: the maximum temperature difference between the top of the chamber and the base is 2C... I can live with that. Another fan to circulate the air in the chamber would be better, but I am leaving that for v2.0. This is the original prototype that is being shown here.
![Chamber on the printer](https://user-images.githubusercontent.com/56422704/194804828-f257f0a8-3363-42ed-ab42-9d41bbcc9b37.jpeg)

Here is a Chamber & Ambient temperature chart showing the temperature over a two hour period. The chamber takes around 30 minutes to settle at the 30C target temperature and it maintains it within 0.2C thereafter. The ambient temperature increases from 15.2C to 18.6C over this time period. The temperature inside the chamber is not affected by the ambient temperature.
![Chamber & Ambient Temperature Chart](https://user-images.githubusercontent.com/56422704/194842887-2f704fea-28f7-4bea-bceb-071f1e721f3f.png)

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
- MDF 6mm or 12mm board (big box store)
- Small piece of clear acrylic sheet (big box store)
- BTS7960 Motor Board/Driver (IBT_2 module) (https://www.ebay.com/sch/i.html?_nkw=bts7960&_sacat=0)
- Thermoelectic Peltier Refrieration Cooling System Kit (https://www.ebay.com/sch/i.html?_nkw=Thermoelectric+Peltier+Refrigeration+Cooling+System+Kit+Cooler&_sacat=0)
- DS18B20 Temperature Sensor Kit (https://www.iot-store.com.au/products/waterproof-ds18b20-temperature-sensor-kit)
- Pack of M3 x 25mm Tapped Metal Spacers (https://www.jaycar.com.au/m3-x-25mm-tapped-metal-spacers-pk8/p/HP0907)
- Unknown length of twin core cable rated above 6A (enough for TEC module) 
        (https://www.jaycar.com.au/15a-twin-core-power-cable-sold-per-metre/p/WH3079)
            or
        (https://www.jaycar.com.au/red-heavy-duty-hook-up-wire-sold-per-metre/p/WH3040) and (https://www.jaycar.com.au/black-heavy-duty-hook-up-wire-sold-per-metre/p/WH3041)
- Unknown length of twin core cable to connect temperature sensors & power to the two fans on the Thermoelectic Peltier Refrieration Cooling System (https://www.jaycar.com.au/red-flexible-light-duty-hook-up-wire-sold-per-metre/p/WH3010) and (https://www.jaycar.com.au/black-flexible-light-duty-hook-up-wire-sold-per-metre/p/WH3011)

Miscellaneous
- Soldering iron & solder (optional as one can just use screw-down connectors)
- electrician's tape
- 3mm drill bit & drill to use on MDF
- crimping tool/pair of pliers
- coping saw/jigsaw
- box cutter/sharp knife

## Configuring the Raspberry Pi

### Configure the Raspbian OS
Download the official [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and install it.
Insert the microSD card into your PC/Mac using an adapter and start the Raspberry Pi Imager you have just installed.

Under the *CHOOSE OS* button, select *Raspberry Pi OS (other)* > *Raspberry Pi OS Lite (64-bit)*

Select your microSD card under *CHOOSE STORAGE*

Select the *Advanced options* menu (wheel cog in bottom right corner).

Set a hostname - anything will do. I use *rpicontroller*.

Check the *Enable SSH* and make sure *Use password authentication is selected*.

Set a username & password you want to use.

If you will be using WiFi, check the *Configure wireless LAN* and set the *SSID* and *password* to the WiFi network you use. Make sure you set the correct *Wireless LAN country* for your area.

Check the *Set locale settings* checkbox and set your *Time zone* correctly.

Click on the *Save* button and exit the dialog box.

Click on the *WRITE* button and wait for the image to be written to the microSD. When prompted, remove the microSD from your system.

### Determine the IP address of your Raspberry Pi so you can connect to it
Connect the Raspberry Pi to a PC monitor/TV and connect a keyboard.
Insert the microSD into the Raspberry Pi and turn it on.
After the Raspberry Pi has booted, log in using the username and password you provided when preparing the microSD.
Enter the following to get the Raspberry Pi's IP address
```
ip -f inet address | grep global
```
The IP address of the Raspberry Pi is the first four groups of numbers in the following format 'XXX.XXX.XXX.XXX/24' - remember these four numbers (excluding the '/24').
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
where &lt;username&gt; is the username you provided during the Raspbian OS configuration, and &lt;XXX.XXX.XXX.XXX&gt; is the IP address of your Raspberry Pi.
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

### Configure the python scripts
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
Select '3 Interface Options' > '17 1-Wire' and enable it. You will be have to reboot the OS after this. The 1-Wire protocol is now enabled.

### Mount the Raspberry Pi to the MDF board
Use the 3mm drill bit to carefully widen the mounting holes of the Raspberry Pi (they are just a fraction smaller than 3mm). This can and should be done by hand, Measure out the mounting locations on the MDF board and drill out the mounting holes. Use the M3 X 10mm Tapped Metal Spacers, the 3mm Steel Flat Washers and the 3mm x 6mm Screws to mount the Raspberry Pi to the MDF board.
![Components mounted to a MDF board](https://user-images.githubusercontent.com/56422704/194804863-6ca4d52a-4c55-4326-89aa-56c67fe95985.jpeg)

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
![DS18B20 Temperature Sensor Module mounted onto the mini breadboard](https://user-images.githubusercontent.com/56422704/194804869-dbc162b2-5115-42ab-8818-9caff18d56a0.jpeg)
Using the plug to socket jumper leads, connect the 3.3V row to *Physical Pin 1* on the Raspberry Pi's GPIO.
Now connect the GND row to any of the following: Physical Pin 6/9/14/20/30/34/39. I use *Physical Pin 9*.
Now connect the S row to *Physical Pin 7*.
Any additonal temperature sensors will be connected into and make use of these three S, 3.3V and GND rows on the mini breadboard. Each temperature sensor has a unique ID which identifies it on the S-row/1-Wire, and one can have as many different sensors connected together in this way.
The last wiring to the mini breadboard is to connect each of the following to its own row on the mini breadboard: *Physical Pin 2* (5V), *Physical Pin 6* (GND) and *Physical Pin 17* (3.3V). These 5V & GND rows are used to power the IBT_2 module/driver, while the 3.3V row is used to enable the module/driver. Any additional IBT_2 modules/drivers will also make use of these three rows.
If one runs out of connections in a row, remember that the full row can be connected to another empty row using a plug to plug jumper lead.
![Raspberry Pi hooked up](https://user-images.githubusercontent.com/56422704/194804883-f3b85b53-af98-47c2-a2c4-187b8cb4cab3.jpeg)
Turn on the Raspberry Pi and connect to it over SSH.
Change into the *rpi-pid-chamber* directory and run the *sensors.py* python script
```
cd ~/rpi-pid-chamber
python sensors.py
```
This script will print out the sensor ID and the temperature of all the DS18B20 sensors connected to the Raspberry Pi. Placing a finger on the sensor will increase the temperature that is being read - this can be used to identify the sensor ID when there are multiple sensors connected.
Take note of the ID of the DS18B20 Temperature Sensor Module - this sensor is used to measure the ambient temperature of the room.
The script can be stopped by pressing *CTRL+C*.
The Raspberry Pi is now set up!

## Wiring up the power supply
Measure out the mounting holes at the top and bottom edge of the power supply onto the MDF board. Using an old power cable (or old kettle cord), cut off the appliance end and strip the insulation from the wires using a sharp knife. Crimping the ends is the safest way of connecting the wires to the power supply Crimp an eye terminal onto the exposed wire using a crimping tool or a pair of pliers (I just soldered the wires onto the eye terminal).
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
Assemble the DS18B20 Temperature Sensor Kit as shown [in this YouTube video](https://www.youtube.com/watch?v=mMoRSgNoOoE)
![DS18B20 Temperature Sensor Module](https://user-images.githubusercontent.com/56422704/194804856-fa8487c0-4e9b-4010-8c91-30f3a2995175.jpeg)
Using the plug to plug jumper leads (if close enough), connect the S row on the mini breadboard to the D1 socket of the black connector, the 3.3V row on the mini breadboard to the +ve socket, and the GND row to the -ve socket on the black connector, using the diagram shown in the [YouTube video](https://www.youtube.com/watch?v=mMoRSgNoOoE).
Run the *sensors.py* python script to confirm the sensor is recognised.
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

Note that it is not important which of of these two GPIO pins are connected to which IBT_2 pins. They can be set correctly in the software.

Strip the wires at the ends of the twin core/heavy duty hook-up wires. Connect the red and black wires of one end to the M+ and M- terminal block.

Carefully turn the IBT_2 module/driver upside-down so the heat sink is facing upwards and screw the module to the tapped metal spacers.

## Construct the chamber out of XPS foam
Make a close-fitting MDF skirt to support the XPS foam chamber. 
![MDF shelf to support the enclosure](https://user-images.githubusercontent.com/56422704/194804841-80fb968f-5ce3-4871-893a-2cf5621d8a06.jpeg)
The width must be able to accomodate the thickness of the XPS foam you are using. Measure out and cut the sides and the top.
In one of the sides, use a router/sharp knife to make a rebate for an acrylic window to monitor print progress. 
![Acrylic window](https://user-images.githubusercontent.com/56422704/194804890-a619e3f5-5301-49ac-a04f-76f77bd12849.jpeg)
I have a piece of XPS foam I use to cover the window when printing. In some instances, leaving the window uncovered results in good performance, as the heater/cooler is 'pulling' against a small inflow/outflow of heat. But this is very sensitive to the PID variables, as well as the chamber/ambient temperature difference.
![Cover for acrylic window]https://user-images.githubusercontent.com/56422704/195497023-4d02d445-c84a-41d2-b1ad-1584ebd93236.jpg
In the top, create an opening to accomodate the small heatsink of the TEC Cooler.
![TEC on top of the chamber](https://user-images.githubusercontent.com/56422704/194804907-6e3036b9-fbe8-486a-9cb3-148e156bc091.jpeg)
![TEC removed](https://user-images.githubusercontent.com/56422704/194804921-0a060da6-35e5-4ee5-8ac9-2b843284c57d.jpeg)
Create a rebate for an acrylic support block for the TEC to rest on.
![TEC & acrylic support with rebate](https://user-images.githubusercontent.com/56422704/194804900-5d3eb920-801b-4638-a170-3f665d075c4b.jpeg)
The acrylic support must have a rectangular opening that is snug with the small heatsink. Inside the chamber on the top side, cut out two relief channels to allow better airflow out of the small heatsink, or the small heatsink will be embedded in the XPS foam. Since air can only exit the small heatsink in two directions, you only need two channels.
![Inside the chamber showing the relief channels to help with airlow](https://user-images.githubusercontent.com/56422704/194804819-1ee78754-e6e5-417e-b73c-372662cad7ab.jpeg)
Glue all the components together with Original Gorilla glue and prime the chamber with two coats of Mod Podge to protect the chamber.
Assemble the chamber with the TEC and the acrylic support plate.
Place a small hole in the top of the chamber to pass the power cables through for the small fan.
Place a hole near the bottom of the chamber so the temperature sensor is just above the resin vat. I have placed it near the back so it does not get in the way of the build plate.
![Location of the temperature sensor](https://user-images.githubusercontent.com/56422704/194804848-52c2f169-7a2d-4656-9c09-05403cc5d964.jpeg)

## Wiring up the thermoelectic module
Connect/solder the end of the twin core/heavy duty hook-up wire from the IBT_2 module to the peltier module.
Connect/solder the end of the twin core/light duty hook-up wire from the power supply to the two fans on the Thermoelectic Peltier Refrieration Cooling System.

## Test the system
Insert the temperature sensor into the chamber and seal with Blue Tack.
Connect the power supply to the wall socket and turn it on - the two fans on the TEC will produce significant noise, as they are runnng at full power. They are also VERY cheap, so their bearings will add to the noise after a short while. Since my setup is in a shed out back, the noise is not a problem for me, so I have not looked for a solution. Another IBT_2 could be used to control the speed of the fans, but the system has better efficiency when the heatsinks are flushed as quickly as possible. The only advice I can give is to just replace the fans with good quality ones if noise is a problem.
Log into the Raspberry Pi over SSH, change into the *rpi-pid-chamber* directory.
Run the *sensors.py* script to identify the sensor IDs of the temperature probes.
```
cd ~/rpi-pid-chamber
python sensors.py
```
Now run the *optimize.py* script, remembering to use the *--ambient-sensor* and *--chamber-sensor* switches with the sensor IDs you have just obtained.
```
python optimize.py --help
python optimize.py 30 --ambient-sensor <ambient-sensor-id-you-recorded> --chamber-sensor <chamber-sensor-id-you-recorded>
```
The temperature inside the chamber should start increasing/decrease depending on the target temperature.
If the temperature is moving the wrong way, then stop the script with *CTRL-C* and swap the pin settings of the script
```
python optimize.py 30 --cooling-pin 15 --heating-pin 13 --ambient-sensor <ambient-sensor-id-you-recorded> --chamber-sensor <chamber-sensor-id-you-recorded>
```
When all is in order, log the output so you can examine the csv data in Excel.
Use this script to optimise the P, I & D parameters. Play around... The ideal is that the system settles down with the TEC havig a duty cycle around 20%. Small fluctuations around the target temperature are expected and can be addressed using the derivative gain - I do not bother as it is good enough as it is.

When you have reasonable PID variables, update the *config.txt* configuration file with all your data. I use the *nano* editor - save the file with *CTRL-O* and exit with *CTRL-X*.
```
nano config.txt
```
Then you can run the *control.py* script and start printing...
```
python control.py
```

I use the linux program *tmux* to give me a terminal that will run the scripts indefinitely. I can disconnect from the Raspberry Pi and the scripts will continue to run in the background.
To create a tmux session
```
tmux new-session -s chamber
```
This opens another terminal you can use. Run all your python scripts in this terminal, such as
```
python control.py
```

To detach from this terminal and leave it running in the background, press *CTRL+B* **THEN** *D*. You can then log out of the Raspberry Pi with
```
exit
```
When you log back into the Raspberry Pi, you can attach to the running terminal with
```
tmux a
```
and you will be back in the terminal running the python script.

You can split the *tmux* terminal vertically with *CTRL+B* **THEN** *%*, or horizontally with *CTRL+B* **THEN** *"*. Navigate between the windows/panels using *CTRL+B* **THEN** &lt;*arrow keys*&gt;. To remove a panel, just type
```
exit
```
in the window/panel and it will close.

You can use this feature of *tmux* to run several chambers at once from a single Raspberry Pi. Just add another IBT_2 module and use a bigger power supply or put it on its own extra power supply.