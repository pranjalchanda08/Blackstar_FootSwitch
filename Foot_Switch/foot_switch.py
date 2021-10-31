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
                with open('patch.json', 'r') as patch_file:
                    file_dict = json.load(patch_file)
                    self.set_preset(preset_name=file_dict['default'], file_dict=file_dict)
                
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
    
    def set_all_controls(self, control_dict):
        '''
            Set all the control params of a required patch
            
            control_dict - Dictionary pointer of the control setting of a patch
        '''
        self.FS_BUTTON_DICT['Control'] = control_dict
        for control in control_dict:
            print(control)
            if control == "delay_time":
                continue
            self.bs.set_control(control, self.FS_BUTTON_DICT['Control'][control])

    def set_preset(self, preset_name, file_dict):
        '''
            Set all the control settings according to patch name
            
            preset_name - Name of the reuired preset str
            file_dict - dictionary converted from patch.json
        '''
        set_flag = False
        for patch in file_dict['patches']:
            if preset_name == patch['name']:
                set_flag = True
                self.set_all_controls(patch['Control'])
        if not set_flag:
            logging.error("Invalid Preset")
        
    def set_preset_index(self, index, file_dict):
        '''
            Set all the control settings according to index
            
            index - index of the patch starting from 0
            file_dict - dictionary converted from patch.json
        '''
        if index > len(file_dict['patches']):
            logging.error("Invalid index")
            return
        self.set_all_controls(file_dict['patches'][index]['Control'])
        

if __name__ == '__main__':
    
    try:
        fs = foot_switch()
    except KeyboardInterrupt:
        sys.exit(1)