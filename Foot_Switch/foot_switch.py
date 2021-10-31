from blackstarid import BlackstarIDAmp, NoDataAvailable, NotConnectedError
import sys
import RPi.GPIO as GPIO
import logging
import threading
import json
from  beeprint import pp

class foot_switch():
    '''
    '''
    FS_BUTTON_DICT = {
        "Pins":{
            "FS_PATCH_UP": 5,
            "FS_PATCH_DOWN": 6,
            "FS_MOD_TOGGLE": 13,
            "FS_DEL_TOGGLE": 19,
            "FS_REV_TOGGLE": 26,
        },        
        "Control" : {}
    }
    def __init__(self):
        with open('patch.json', 'r') as patch_file:
            file_dict = json.load(patch_file)
            for patch in file_dict['patches']:
                if file_dict['default'] == patch['name']:
                    print("Default patch: " + patch['name'])
                    self.FS_BUTTON_DICT['Control'] = patch['Control']
        GPIO.setmode(GPIO.BCM)
        for button in list(self.FS_BUTTON_DICT['Pins'].values()):
            GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(button, GPIO.BOTH, callback = self.fs_but_callback, bouncetime=100)
        try:
            logging.basicConfig(level=logging.DEBUG)
            logging.getLogger('insider.blackstarid')
            
            self.bs = BlackstarIDAmp()
                
            if self.bs.connected is False:
                self.bs.connect()
                self.bs.drain()
                self.bs.startup()
                self.alive = True
                self.read_thread = threading.Thread(target=self.read_thread_entry, args=(1,))
                self.read_thread.start()
                for control in self.FS_BUTTON_DICT['Control']:
                    print(control)
                    if control == "delay_time":
                        continue
                    self.bs.set_control(control, self.FS_BUTTON_DICT['Control'][control])
                
        except NotConnectedError:
            raise NotConnectedError
    
    def __del__(self):
        try:
            self.alive = False
            self.read_thread.join()
        except:
            pass
                          
    def read_thread_entry(self, name):
        while self.alive:
            try:
                self.FS_BUTTON_DICT['Control'] = self.bs.read_data()
                logging.debug(self.FS_BUTTON_DICT['Control'])
            except NoDataAvailable:
                pass
            
    
    def fs_but_callback(self, channel):
        if GPIO.input(channel):
            return
        
        if channel == self.FS_BUTTON_DICT['Pins']['FS_PATCH_UP']:
            pass
        
        elif channel == self.FS_BUTTON_DICT['Pins']['FS_PATCH_DOWN']:
            pass
        
        elif channel == self.FS_BUTTON_DICT['Pins']['FS_MOD_TOGGLE']:
            self.FS_BUTTON_DICT['Control']['mod_switch'] ^= 1;
            self.bs.set_control('mod_switch', self.FS_BUTTON_DICT['Control']['mod_switch'])
            
        elif channel == self.FS_BUTTON_DICT['Pins']['FS_DEL_TOGGLE']:
            self.FS_BUTTON_DICT['Control']['delay_switch'] ^= 1;
            self.bs.set_control('delay_switch', self.FS_BUTTON_DICT['Control']['delay_switch'])
        
        elif channel == self.FS_BUTTON_DICT['Pins']['FS_REV_TOGGLE']:
            self.FS_BUTTON_DICT['Control']['reverb_switch'] ^= 1;
            self.bs.set_control('reverb_switch', self.FS_BUTTON_DICT['Control']['reverb_switch'])
            
if __name__ == '__main__':
    
    try:
        fs = foot_switch()
    except KeyboardInterrupt:
        sys.exit(1)