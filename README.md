# Blackstar Foot Switch
A Project to create BlackStart Foot Swith over USB


## Installation

```sh
$ sudo apt-get install python3-setuptools python-usb
$ cd pyusb
$ sudo setup.py install
$ cd ../Adafruit_Python_SSD1306
$ sudo setup.py install
```

## Setup default Audio PCM channel

```sh
$ aplay -l
```
- List the Card number and device ID

```sh
$ sudo nano /usr/share/alsa/alsa.conf
```

- Replace `defaults.pcm.card {}` and `defaults.pcm.device {}` as required

