from blackstarid import BlackstarIDAmp, NoDataAvailable, NotConnectedError
import sys
import RPi.GPIO as GPIO
import signal
import logging
import threading

class foot_switch():
    '''
    '''
    FS_BUTTON_LIST = [5, 6, 13, 19, 26]
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for button in self.FS_BUTTON_LIST:
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
                self.read_thread = threading.Thread(target=self.read_thread_entry, args=(1,))
                self.alive = True
                self.control = {}
                self.read_thread.start()
                
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
                self.control = self.bs.read_data()
            except NoDataAvailable:
                pass
            
    
    def fs_but_callback(self, channel):
        if GPIO.input(channel):
            return
        if channel == self.FS_BUTTON_LIST[0]:
            self.bs.set_control('isf', 125)
        elif channel == self.FS_BUTTON_LIST[1]:
            pass
        elif channel == self.FS_BUTTON_LIST[2]:
            pass
        elif channel == self.FS_BUTTON_LIST[3]:
            pass
        elif channel == self.FS_BUTTON_LIST[4]:
            pass
        
     
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
       
if __name__ == '__main__':
    
    try:
        fs = foot_switch()
    except KeyboardInterrupt:
        sys.exit(1)