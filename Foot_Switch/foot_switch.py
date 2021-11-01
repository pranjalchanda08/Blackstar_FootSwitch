from blackstarid import BlackstarIDAmp, NoDataAvailable, NotConnectedError
import RPi.GPIO as GPIO
import logging
import threading, queue
import json
import signal
import os
import sys
from numpy import interp
import paho.mqtt.client as mqtt

MAIN_EXIT = False

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(" FootSwitch ")
                
class foot_switch():
    """
        Class defination of foot_switch instance.
    """
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
    
    def __init__(self, logger):
        """
            Initialise Foot Switch instance
        """
        GPIO.setmode(GPIO.BCM)
        for button in list(self.FS_BUTTON_DICT['Pins'].values()):
            GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(button, GPIO.BOTH, callback = self.fs_but_callback, bouncetime=100)
        self.logger = logger
        self.bs = BlackstarIDAmp()
        if self.bs.connected is False:
            self.bs.connect()
            self.bs.drain()
            self.bs.startup()
            self.alive = True
            self.task_q = queue.Queue()
            self.read_thread = threading.Thread(target=self.foot_switch_thread_entry, args=(1,))
            self.read_thread.start()
            ret, len = self.set_preset(preset_name='default')
            if ret >= 0 :
                self.FS_BUTTON_DICT['Patch_index'], self.FS_BUTTON_DICT['Patch_len'] = ret, len

    def __del__(self):
        try:
            self.alive = False
            self.bs.disconnect()
            self.task_q.join()
            self.read_thread.join()
            GPIO.cleanup()
            self.logger.info(" Device disconnected! ")
        except:
            pass

    def patch_range_human_to_device(self, control_dict, flag=True):
        """
            Convert ranges from human readable to device acceptable range
            
            flag - True for human readable to device and vice versa
        """
        new_control_dict = {}
        for element in control_dict:
            new_control_dict[element] = int(self.map_range(
                                            control_dict[element],
                                            self.bs.control_limits_rev[element] if flag else self.bs.control_limits[element],
                                            self.bs.control_limits[element] if flag else self.bs.control_limits_rev[element]))
        return new_control_dict

    def foot_switch_thread_entry(self, name):
        """
            Thread Entry for foot_switch thread
        """
        while self.alive:
            try:
                if self.task_q.empty() == False:
                    bcm_pin = self.task_q.get()                    
                    if bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_PATCH_UP']:
                        self.FS_BUTTON_DICT['Patch_index'] += 1
                        self.FS_BUTTON_DICT['Patch_index'] %= self.FS_BUTTON_DICT['Patch_len']
                        self.set_preset_index(self.FS_BUTTON_DICT['Patch_index'], self.file_dict)

                    elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_PATCH_DOWN']:
                        self.FS_BUTTON_DICT['Patch_index'] += 1
                        self.FS_BUTTON_DICT['Patch_index'] %= self.FS_BUTTON_DICT['Patch_len']
                        self.set_preset_index(self.FS_BUTTON_DICT['Patch_index'], self.file_dict)

                    elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_MOD_TOGGLE']:
                        self.FS_BUTTON_DICT['Control']['mod_switch'] ^= 1;
                        self.bs.set_control('mod_switch', self.FS_BUTTON_DICT['Control']['mod_switch'])

                    elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_DEL_TOGGLE']:
                        self.FS_BUTTON_DICT['Control']['delay_switch'] ^= 1;
                        self.bs.set_control('delay_switch', self.FS_BUTTON_DICT['Control']['delay_switch'])

                    elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_REV_TOGGLE']:
                        self.FS_BUTTON_DICT['Control']['reverb_switch'] ^= 1;
                        self.bs.set_control('reverb_switch', self.FS_BUTTON_DICT['Control']['reverb_switch'])                
                    
                    self.task_q.task_done()
                
            except Exception as e:
                self.logger.error(" Device Error " + str(e))
            try:
                self.FS_BUTTON_DICT['Control'].update(self.bs.read_data())
                self.logger.debug(self.FS_BUTTON_DICT['Control'])
            except NoDataAvailable:
                pass
            except KeyboardInterrupt:
                self.alive = False
        self.logger.info(" read_thread_entry Killed! ")


    def fs_but_callback(self, bcm_pin):
        """
            Callback for Button Events
            
            bcm_pin     Pin number of the event occur
        """
        if GPIO.input(bcm_pin):
            return
        self.task_q.put_nowait(bcm_pin)
        
        
    def map_range(self, val, input_range, output_range):
        return interp(val, input_range, output_range)

    def set_all_controls(self, control_dict):
        """
            Set all the control params of a required patch

            control_dict - Dictionary pointer of the control setting of a patch
        """
        self.FS_BUTTON_DICT['Control'] = control_dict
        for control in control_dict:
            if control == "delay_time":
                continue
            self.bs.set_control(control, self.FS_BUTTON_DICT['Control'][control])

    def set_preset(self, preset_name):
        """
            Set all the control settings according to patch name

            preset_name - Name of the reuired preset str
            file_dict - dictionary converted from patch.json
        """
        index = 0
        with open('json/patch.json', 'r') as patch_json_file:
            file_patch = json.load(patch_json_file)
            patch_reg_len = len(list(file_patch['patches'].keys()))
            key_list = list(file_patch['patches'].keys())
            if preset_name in key_list:
                index = key_list.index(preset_name)
                with open(os.path.join('.', file_patch['patches'][preset_name]), 'r') as json_file:
                    file_dict = json.load(json_file)
            else:
                self.logger.error("Invalid Preset")
                return -1, patch_reg_len
        self.FS_BUTTON_DICT['Control'] = self.patch_range_human_to_device(file_dict['Control'])
        self.set_all_controls(self.FS_BUTTON_DICT['Control'])
        return index, patch_reg_len

    def set_preset_index(self, index, file_dict):
        """
            Set all the control settings according to index

            index - index of the patch starting from 0
            file_dict - dictionary converted from patch.json
        """
        if index > self.FS_BUTTON_DICT['Patch_len']:
            self.logger.error("Invalid index")
            return -1
        else:
            with open('json/patch.json', 'r') as patch_json_file:
                file_patch = json.load(patch_json_file)
                preset_name = list(file_patch['patches'].keys())[index]
            with open(os.path.join('.', file_patch['patches'][preset_name]), 'r') as json_file:
                file_dict = json.load(json_file)

        self.FS_BUTTON_DICT['Control'] = self.patch_range_human_to_device(file_dict['Control'])
        self.set_all_controls(self.FS_BUTTON_DICT['Control'])
        return len(file_dict['patches'])

def on_connect(client, userdata, flags, rc):
    """
        MQTT on_connect callback
    """
    logger.info(" MQTT Client connected ")
    
def on_message(client, userdata, message):
    """
        MQTT on_message callback
    """
    msg_json = json.loads(message.payload.decode('utf-8'))
    mqtt_task_q.put_nowait(msg_json)
    logger.debug(str(msg_json))

def ctrl_c_handler(signal, dummy):
    """
        Termination Signal Handler    
    """
    fs.__del__()
    mqtt_task_q.join()
    MAIN_EXIT = True
    main_task.join()
    client.loop_stop()
    os._exit(0)

def main_thread_entry(name, Terminate=MAIN_EXIT):
    while not Terminate:
        if mqtt_task_q.empty() == False:
            control_change = mqtt_task_q.get()
            with open('json/default.json', 'r+') as json_file:
                file_dict = json.load(json_file)
                file_dict['Control'][list(control_change.keys())[0]] = list(control_change.values())[0]
                json_file.seek(0)
                json.dump(file_dict, json_file, sort_keys=True, indent=4)
            mqtt_task_q.task_done()
            
try:
    fs = foot_switch(logger=logger)
    mqtt_task_q = queue.Queue()
    main_task = threading.Thread(target=main_thread_entry, args=(1,))
    main_task.start()
    client = mqtt.Client("LocalHost")
    client.connect("localhost")
    client.subscribe("Footswitch/Control")
    client.on_message = on_message
    client.on_connect = on_connect
    signal.signal(signal.SIGINT, ctrl_c_handler)
    signal.signal(signal.SIGTERM, ctrl_c_handler)
    client.loop_start()
except Exception as e:
    logger.error(" Exception in main thread " + str(e))