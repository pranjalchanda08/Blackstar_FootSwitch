from blackstarid import BlackstarIDAmp, NoDataAvailable, NotConnectedError
import RPi.GPIO as GPIO
import logging
import threading, queue
import json
import signal
import os
import time
from numpy import interp
import paho.mqtt.client as mqtt

THREAD_EXIT = False

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
        "Control_save" : {},
        "Patch_index" : -1,
        "Patch_len": 0,
        "disp_payload" : {
            "gain" : 10,
            "voice" : 5,
            "patch" : "Metal Low",
            "volume" : 8,
            "isf" : 9, 
            "bass" : 5,
            "treble" : 3,
            "mod": 1,
            "delay" : 1,
            "reverb" : 1
        }
    }

    def __init__(self, logger, mqtt_client):
        """
            Initialise Foot Switch instance
        """
        GPIO.setmode(GPIO.BCM)
        self.mqtt_client = mqtt_client
        self.ms_start = 0
        for button in list(self.FS_BUTTON_DICT['Pins'].values()):
            GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(button, GPIO.BOTH, callback = self.fs_but_callback, bouncetime=500)
        
        self.logger = logger
        
        self.bs = BlackstarIDAmp()
        connected = self.bs.initialise()
        if connected:
            self.alive = True
            self.task_q = queue.Queue()
            self.read_thread = threading.Thread(target=self.foot_switch_thread_entry, args=(1,))
            self.read_thread.start()
            ret, len = self.set_selected_preset()
            if ret >= 0 :
                self.FS_BUTTON_DICT['Patch_index'], self.FS_BUTTON_DICT['Patch_len'] = ret, len
        else:
            logger.error("Failed to connect!")
    def close(self):
        try:
            self.alive = False
            self.bs.disconnect()
            self.task_q.join()
            self.read_thread.join()
            GPIO.cleanup()
            self.logger.info(" Device disconnected! ")
        except:
            pass

    def __del__(self):
        self.close()

    def oled_display(self, string):
        self.mqtt_client.publish(topic='Footswitch/Display', 
                                    payload=string,
                                    qos=1, 
                                    retain=True) 
    def TFT_display(self, dict):
        string = json.dumps(dict)
        self.mqtt_client.publish(topic='Footswitch/Display', 
                                    payload=string,
                                    qos=1, 
                                    retain=True)    

    def patch_range_human_to_device(self, control_dict, flag=True):
        """
            Convert ranges from human readable to device acceptable range

            flag - True for human readable to device and vice versa
        """
        new_control_dict = {}
        for element in control_dict:
            if flag:
                new_control_dict[element] = int(self._map_range(
                                                control_dict[element],
                                                self.bs.control_limits_rev[element],
                                                self.bs.control_limits[element]))
            else:
                x = round(self._map_range(
                          control_dict[element],
                          self.bs.control_limits[element],
                          self.bs.control_limits_rev[element]), 1)
                if float(x) == int(x):
                    new_control_dict[element] = int(x)
                else:
                    new_control_dict[element] = x
        return new_control_dict

    def foot_switch_thread_entry(self, name):
        """
            Thread Entry for foot_switch thread
        """
        json_file_path = "json/default.json"
        self.FS_BUTTON_DICT['Patch_name'], json_file_path = self.get_selected_preset()
        self.mqtt_client.publish(topic='Footswitch/PatchSelected', 
                                    payload=self.FS_BUTTON_DICT['Patch_name'],
                                    qos=1, 
                                    retain=True)
        while self.alive:
            self.FS_BUTTON_DICT['Patch_name'], json_file_path = self.get_selected_preset()
            if not self.FS_BUTTON_DICT['Control_save'] == {}:
                with open(json_file_path, 'r') as json_file:
                    file_dict = json.load(json_file)
                    file_dict['Control'].update(self.FS_BUTTON_DICT['Control_save'])
                    human_readable = self.patch_range_human_to_device(self.FS_BUTTON_DICT['Control'], False)
                    self.FS_BUTTON_DICT['disp_payload']['gain'] =   human_readable['gain']
                    self.FS_BUTTON_DICT['disp_payload']['voice'] =  human_readable['voice']
                    self.FS_BUTTON_DICT['disp_payload']['volume'] = human_readable['volume']
                    self.FS_BUTTON_DICT['disp_payload']['isf'] =    human_readable['isf']
                    self.FS_BUTTON_DICT['disp_payload']['bass'] =   human_readable['bass']
                    self.FS_BUTTON_DICT['disp_payload']['treble'] = human_readable['treble']
                    self.FS_BUTTON_DICT['disp_payload']['mod'] =    human_readable['mod_switch']
                    self.FS_BUTTON_DICT['disp_payload']['delay'] =  human_readable['delay_switch']
                    self.FS_BUTTON_DICT['disp_payload']['reverb'] = human_readable['reverb_switch']
                    self.FS_BUTTON_DICT['disp_payload']['patch'] =  self.FS_BUTTON_DICT['Patch_name']
                    self.TFT_display(self.FS_BUTTON_DICT['disp_payload'])
                with open(json_file_path + ".lock", 'w'):
                    with open(json_file_path, 'w') as json_file:
                        json.dump(file_dict, json_file, sort_keys=True, indent=4)
                
                    self.mqtt_client.publish(topic='Footswitch/PatchSelected', 
                                        payload=self.FS_BUTTON_DICT['Patch_name'],
                                        qos=1, 
                                        retain=True)
                os.remove(os.path.abspath(json_file_path + ".lock"))
                self.FS_BUTTON_DICT['Control_save'] = {}
            try:
                if self.task_q.empty() == False:
                    request = self.task_q.get()
                    self._foot_switch_actions(request=request)
                    self.task_q.task_done()
            except Exception as e:
                self.logger.error(" Device Error " + str(e))

            try:
                self.FS_BUTTON_DICT['Control'].update(self.bs.read_data())
                self.FS_BUTTON_DICT['Control_save'] = self.patch_range_human_to_device(self.FS_BUTTON_DICT['Control'], flag=False)
                self.logger.debug(self.FS_BUTTON_DICT['Control_save'])
            except NoDataAvailable:
                pass
            except KeyboardInterrupt:
                self.alive = False
        self.logger.info(" Foot Switch Thread Killed! ")

    def _millis(self):
        return time.time() * 1000

    def fs_but_callback(self, bcm_pin):
        """
            Callback for Button Events

            bcm_pin     Pin number of the event occur
        """
        if GPIO.input(bcm_pin):
            ms_release = self._millis()
            request = {
                "bcm_pin" : bcm_pin,
                "long_press" : False
                }
            if ms_release - self.ms_start > 2000:
                request['long_press'] = True
            self.task_q.put_nowait(request)

        elif not GPIO.input(bcm_pin):
            self.ms_start = self._millis()

    def _foot_switch_actions(self, request):
        bcm_pin = request['bcm_pin']
        if bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_PATCH_UP']:
            self.FS_BUTTON_DICT['Patch_index'] += 1
            self.FS_BUTTON_DICT['Patch_index'] %= self.FS_BUTTON_DICT['Patch_len']
            self.FS_BUTTON_DICT['Patch_len'], self.FS_BUTTON_DICT['Patch_name'] = \
                self.set_preset_index(self.FS_BUTTON_DICT['Patch_index'])
            

        elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_PATCH_DOWN']:
            self.FS_BUTTON_DICT['Patch_index'] -= 1
            self.FS_BUTTON_DICT['Patch_index'] %= self.FS_BUTTON_DICT['Patch_len']
            self.FS_BUTTON_DICT['Patch_len'], self.FS_BUTTON_DICT['Patch_name'] = \
                self.set_preset_index(self.FS_BUTTON_DICT['Patch_index'])
            self.mqtt_client.publish(topic='Footswitch/PatchSelected', 
                                    payload=self.FS_BUTTON_DICT['Patch_name'],
                                    qos=1, 
                                    retain=False)

        elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_MOD_TOGGLE']:
            if request['long_press']:
                control_str = 'mod_type'
                self.FS_BUTTON_DICT['Control'][control_str] += 1
                self.FS_BUTTON_DICT['Control'][control_str] %= self.bs.control_limits['mod_type'][1]
            else:
                control_str = 'mod_switch'
                self.FS_BUTTON_DICT['Control'][control_str] ^= 1
            self.bs.set_control(control_str, self.FS_BUTTON_DICT['Control']['mod_switch'])

        elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_DEL_TOGGLE']:
            if request['long_press']:
                control_str = 'delay_type'
                self.FS_BUTTON_DICT['Control'][control_str] += 1
                self.FS_BUTTON_DICT['Control'][control_str] %= self.bs.control_limits['mod_type'][1]
            else:
                control_str = 'delay_switch'
                self.FS_BUTTON_DICT['Control'][control_str] ^= 1
            self.bs.set_control(control_str, self.FS_BUTTON_DICT['Control']['mod_switch'])

        elif bcm_pin == self.FS_BUTTON_DICT['Pins']['FS_REV_TOGGLE']:
            if request['long_press']:
                control_str = 'reverb_type'
                self.FS_BUTTON_DICT['Control'][control_str] += 1
                self.FS_BUTTON_DICT['Control'][control_str] %= self.bs.control_limits['mod_type'][1]
            else:
                control_str = 'reverb_switch'
                self.FS_BUTTON_DICT['Control'][control_str] ^= 1
            self.bs.set_control(control_str, self.FS_BUTTON_DICT['Control']['mod_switch'])

    def _map_range(self, val, input_range, output_range):
        """
            Interpolation function
        """
        return interp(val, input_range, output_range)

    def set_limited_controls(self, update_dict):
        """
            Set Specefic controls using an update dictionary

            update_dict - Dictionary pointer of the updated setting of a patch
        """
        for control in update_dict:
            self.FS_BUTTON_DICT['Control'][control] = update_dict[control]
            if control == "delay_time":
                continue
            self.bs.set_control(control, self.FS_BUTTON_DICT['Control'][control])

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

    def get_selected_preset(self):
        """
            Get patch that is selected
        """
        file = "json/patch.json"
        with open(file, 'r') as patch_json_file:
            file_patch = json.load(patch_json_file)
        for patch in file_patch['patches']:
            if file_patch['patches'][patch]['selected'] is True:
                preset_name = patch
                return preset_name, file_patch['patches'][preset_name]['path']

        
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
                key_list.remove(preset_name)
                file_patch['patches'][preset_name]['selected'] = True
                for preset in key_list:
                    file_patch['patches'][preset]['selected'] = False

                with open(os.path.join('.', file_patch['patches'][preset_name]['path']), 'r') as json_file:
                    file_dict = json.load(json_file)
            else:
                self.logger.error("Invalid Preset")
                return -1, patch_reg_len

        with open('json/patch.json', 'w') as patch_json_file:
            json.dump(file_patch, patch_json_file, sort_keys=True, indent=4)

        self.FS_BUTTON_DICT['Control'] = self.patch_range_human_to_device(file_dict['Control'])
        self.set_all_controls(self.FS_BUTTON_DICT['Control'])
        return index, patch_reg_len

    def set_selected_preset(self):
        """
            Set patch that is selected
        """
        with open('json/patch.json', 'r') as patch_json_file:
            file_patch = json.load(patch_json_file)
        for patch in file_patch['patches']:
            if file_patch['patches'][patch]['selected'] is True:
                preset_name = patch
                return self.set_preset(preset_name=preset_name)

    def set_preset_index(self, index):
        """
            Set all the control settings according to index

            index - index of the patch starting from 0
        """
        if index > self.FS_BUTTON_DICT['Patch_len']:
            self.logger.error("Invalid index")
            return -1
        else:
            with open('json/patch.json', 'r') as patch_json_file:
                file_patch = json.load(patch_json_file)
                preset_name = list(file_patch['patches'].keys())[index]
                self.set_preset(preset_name=preset_name)
        return len(list(file_patch['patches'].keys())), preset_name

def on_connect(client, userdata, flags, rc):
    """
        MQTT on_connect callback
    """
    logger.info(" MQTT Client connected ")

def on_message(client, userdata, message):
    """
        MQTT on_message callback
    """
    try:
        msg_json = json.loads(message.payload.decode('utf-8'))
    except:
        pass
    if message.topic == 'Footswitch/Patch':
        print(msg_json)
        fs.fs_but_callback(msg_json['bcm_pin'])
    else:
        mqtt_task_q.put_nowait(msg_json)
        logger.debug(str(msg_json))

def ctrl_c_handler(signal, dummy):
    """
        Termination Signal Handler
    """
    global THREAD_EXIT
    fs.close()
    mqtt_task_q.join()
    THREAD_EXIT = True
    main_task.join()
    client.loop_stop()
    os._exit(0)

def main_thread_entry(name):
    global THREAD_EXIT
    while not THREAD_EXIT:
        try:
            if mqtt_task_q.empty() == False:
                control_change = mqtt_task_q.get()
                fs.FS_BUTTON_DICT['Control_save'][list(control_change.keys())[0]] = list(control_change.values())[0]
                fs.set_limited_controls(fs.patch_range_human_to_device(control_change, flag=True))
                mqtt_task_q.task_done()
        except json.decoder.JSONDecodeError as e:
            logger.error(" Json decode error occured! " + str(e))
    logger.info(" Main Thread Killed!")

try:
    mqtt_task_q = queue.Queue()
    main_task = threading.Thread(target=main_thread_entry, args=(1,))
    main_task.start()
    client = mqtt.Client("LocalHost")
    client.connect("localhost")
    client.subscribe("Footswitch/Control")
    client.subscribe("Footswitch/Patch")
    client.on_message = on_message
    client.on_connect = on_connect
    try:
        fs = foot_switch(logger=logger, mqtt_client=client)
    except Exception as e:
        logger.error(" Exception in Parent thread: " + str(e))
        ctrl_c_handler(0,0)
    signal.signal(signal.SIGINT, ctrl_c_handler)
    signal.signal(signal.SIGTERM, ctrl_c_handler)
    client.loop_start()
except Exception as e:
    logger.error(" Exception in Parent thread: " + str(e))