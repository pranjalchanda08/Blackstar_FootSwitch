sudo apt update -y && sudo apt install mosquitto mosquitto-clients -y
sudo apt-get install -y python3-setuptools
cd pyusb
sudo python3 setup.py install
sudo pip3 install Adafruit_SSD1306
sudo pip3 install paho-mqtt
#bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered) --node16 --confirm-pi --restart
#npm install node-red-dashboard
#npm install node-red-contrib-python3-function
git config --global user.email "pranjalchanda08@gmail.com"
git config --global user.name "Pranjal"