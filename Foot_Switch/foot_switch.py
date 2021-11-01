from blackstarid import BlackstarIDAmp, NoDataAvailable, NotConnectedError
import RPi.GPIO as GPIO
import logging
import threading
import json
import signal
import os
from numpy import interp

class foot_switch():
    '''
        Class defination of foot_switch instance.
    '''
    FS_BUTTON_DICT = {
        "Pins":{
            "FS_PATCH_UP": 5,
            "FS_PATCH_DOWN": 6,
            "FS_MOD_TOGGLE": 13,
            "FS_DEL_TOGGLE": 19,
            "FS_REV_TOGGLE": 26,
        },
        "Control" : {},
        "Patch_index" : -1,
        "Patch_len": 0
    }
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for button in list(self.FS_BUTTON_DICT['Pins'].values()):
            GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(button, GPIO.BOTH, callback = self.fs_but_callback, bouncetime=100)
        try:
            logging.basicConfig(level=logging.NOTSET)
            self.logger = logging.getLogger(" FootSwitch ")

            self.bs = BlackstarIDAmp()

            if self.bs.connected is False:
                self.bs.connect()
                self.bs.drain()
                self.bs.startup()
                self.alive = True
                self.read_thread = threading.Thread(target=self.read_thread_entry, args=(1,))
                self.read_thread.start()
                with open('json/patch.json', 'r') as patch_file:
                    self.file_dict = json.load(patch_file)
                    self.patch_range_human_to_device(self.file_dict['patches'])
                    ret, len = self.set_preset(preset_name=self.file_dict['patch_select'], file_dict=self.file_dict)
                    if ret >= 0 :
                        self.FS_BUTTON_DICT['Patch_index'], self.FS_BUTTON_DICT['Patch_len'] = ret, len

        except NotConnectedError:
            raise NotConnectedError

    def __del__(self):
        try:
            self.alive = False
            self.bs.disconnect()
            self.logger.info(" Device disconnected! ")
        except:
            pass

    def patch_range_human_to_device(self, patches):
        for patch in patches:
            for element in patch['Control']:
                patch['Control'][element] = int(self.map_range(
                                                patch['Control'][element], 
                                                self.bs.control_limits_rev[element],
                                                self.bs.control_limits[element]))
    
    def read_thread_entry(self, name):
        while self.alive:
            try:
                self.FS_BUTTON_DICT['Control'].update(self.bs.read_data())
                self.logger.info(self.FS_BUTTON_DICT['Control'])                
            except NoDataAvailable:
                pass
            except KeyboardInterrupt:
                self.alive = False
        self.logger.info(" read_thread_entry Killed! ")


    def fs_but_callback(self, channel):
        if GPIO.input(channel):
            return

        if channel == self.FS_BUTTON_DICT['Pins']['FS_PATCH_UP']:
            self.FS_BUTTON_DICT['Patch_index'] += 1
            self.FS_BUTTON_DICT['Patch_index'] %= self.FS_BUTTON_DICT['Patch_len']
            self.set_preset_index(self.FS_BUTTON_DICT['Patch_index'], self.file_dict)

        elif channel == self.FS_BUTTON_DICT['Pins']['FS_PATCH_DOWN']:
            self.FS_BUTTON_DICT['Patch_index'] += 1
            self.FS_BUTTON_DICT['Patch_index'] %= self.FS_BUTTON_DICT['Patch_len']
            self.set_preset_index(self.FS_BUTTON_DICT['Patch_index'], self.file_dict)

        elif channel == self.FS_BUTTON_DICT['Pins']['FS_MOD_TOGGLE']:
            self.FS_BUTTON_DICT['Control']['mod_switch'] ^= 1;
            self.bs.set_control('mod_switch', self.FS_BUTTON_DICT['Control']['mod_switch'])

        elif channel == self.FS_BUTTON_DICT['Pins']['FS_DEL_TOGGLE']:
            self.FS_BUTTON_DICT['Control']['delay_switch'] ^= 1;
            self.bs.set_control('delay_switch', self.FS_BUTTON_DICT['Control']['delay_switch'])

        elif channel == self.FS_BUTTON_DICT['Pins']['FS_REV_TOGGLE']:
            self.FS_BUTTON_DICT['Control']['reverb_switch'] ^= 1;
            self.bs.set_control('reverb_switch', self.FS_BUTTON_DICT['Control']['reverb_switch'])

    def map_range(self, val, input_range, output_range):
        return interp(val, input_range, output_range)
    
    def set_all_controls(self, control_dict):
        '''
            Set all the control params of a required patch

            control_dict - Dictionary pointer of the control setting of a patch
        '''
        self.FS_BUTTON_DICT['Control'] = control_dict
        for control in control_dict:
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
                return file_dict['patches'].index(patch), len(file_dict['patches'])
        if not set_flag:
            self.logger.error("Invalid Preset")
            return -1, len(file_dict['patches'])

    def set_preset_index(self, index, file_dict):
        '''
            Set all the control settings according to index

            index - index of the patch starting from 0
            file_dict - dictionary converted from patch.json
        '''
        if index > len(file_dict['patches']):
            self.logger.error("Invalid index")
            return len(file_dict['patches'])
        self.set_all_controls(file_dict['patches'][index]['Control'])
        return len(file_dict['patches'])

def ctrl_c_handler(signal, abc):
    fs.__del__()
    fs.read_thread.join()
    GPIO.cleanup()
    os._exit(0)

fs = foot_switch()
signal.signal(signal.SIGINT, ctrl_c_handler)    
signal.signal(signal.SIGTERM, ctrl_c_handler)    