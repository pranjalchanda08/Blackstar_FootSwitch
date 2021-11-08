# 1. Blackstar Foot Switch
A Project to create BlackStart Foot Swith over USB

- [1. Blackstar Foot Switch](#1-blackstar-foot-switch)
  - [1.1. Installation](#11-installation)
  - [1.2. Setup default Audio PCM channel](#12-setup-default-audio-pcm-channel)
  - [1.3. Auto-start setup](#13-auto-start-setup)
  - [1.4. Pin config](#14-pin-config)

## 1.1. Installation

```sh
$ sudo apt-get install python3-setuptools python-usb
$ cd pyusb
$ sudo setup.py install
$ cd ../Adafruit_Python_SSD1306
$ sudo setup.py install
```

## 1.2. Setup default Audio PCM channel

```sh
$ aplay -l
```
- List the Card number and device ID

```sh
$ sudo nano /usr/share/alsa/alsa.conf
```

- Replace `defaults.pcm.card {}` and `defaults.pcm.device {}` as required

## 1.3. Auto-start setup

```sh
$ sudo systemctl enable nodered.service
$ crontab -e
```
- Add following lines at the last and save

```txt
@reboot cd /home/pi/Blackstar_FootSwitch/Foot_Swich; python3 Oled.py
@reboot cd /home/pi/Blackstar_FootSwitch/Foot_Swich; python3 foot_switch.py
```

## 1.4. Pin config


| Pin Type |Connection Name | BCM Pin Map | Pin Number|Direction|
|--|----------|-------------|-----------|----|
|GPIO|||||
||Patch up  | GPIO 05 | Pin 29 | Input |
||Patch down  | GPIO 06 | Pin 31 | Input |
||Mod Toggle  | GPIO 13 | Pin 33 | Input |
||Delay Toggle  | GPIO 19 | Pin 35 | Input |
||Reverb Toggle  | GPIO 26 | Pin 37 | Input |
|I2C Master||||
||OLED SCL|I2C1 SCL|Pin 5| Output |
||OLED SDA|I2C1 SDA|Pin 3| Input/Output |
|Power||||
||Common +3v3|3v3 Pwr|Pin 1| N/A |
||Common GND|GND|Pin 14| N/A |
