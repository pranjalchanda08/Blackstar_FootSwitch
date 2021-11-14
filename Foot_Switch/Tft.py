from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import digitalio
import board

import time
import json
import subprocess

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO.SPI as SPI
import adafruit_rgb_display.ili9341 as ili9341

import paho.mqtt.client as mqtt
import queue


update_queue = queue.Queue()

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Raspberry Pi configuration.
DC = 25
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0
BACK_LED = 18

# BeagleBone Black configuration.
# DC = 'P9_15'
# RST = 'P9_12'
# SPI_PORT = 1
# SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

# Initialize display.
disp.begin()

# Clear the display to a red background.
# Can pass any tuple of red, green, blue values (from 0 to 255 each).
disp.clear((0, 0, 0))
disp.display()

# time.sleep(1)

disp = ili9341.ILI9341(
    spi,
    rotation=90,  # 2.2", 2.4", 2.8", 3.2" ILI9341
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)

# First define some constants to allow easy positioning of text.
padding = 4
x = 4

pwm_flag = False
refresh_flag = True
display = {
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
def on_message(client, userdata, message):
        global update_queue
        try: 
            msg = message.payload.decode()
            update_param = json.loads(msg)
            update_queue.put(update_param)
        except Exception as e:
            print(msg + str(e))

try:
    client = mqtt.Client("LocalHostDisplay")
    client.connect("localhost")
    client.subscribe("Footswitch/Display")
    client.loop_start()
    client.on_message=on_message
except Exception as e:
    print(" Exception in Parent thread: " + str(e))

def get_status_bar_fill(val, width_start, width_end, sections, scale:tuple):
    scale_len = scale[1] - scale [0]
    total_width = width_end - width_start
    section_width = (total_width / sections) * scale_len
    res_width = section_width * val
    return width_start + res_width

bg_color = 0 #(198, 71, 86) #(20,47,67)
status_bar_outline = bg_color
target_theme_color = (255, 255, 255)
outline_color = (255, 255, 255)

font = ImageFont.FreeTypeFont("font/Game Of Squids.otf", size=30)
font2 = ImageFont.FreeTypeFont("font/PixelOperatorHB.ttf", size=18)
# font2 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 20)
offset = 4
text_offset = 8

voice_list = ['Clean Warm', 'Clean Bright', 'Crunch', 'Super Crunch', 'Over Drive 1', 'Over Drive 2']

while True:
    if not update_queue.empty():
        update_param = update_queue.get()
        update_queue.task_done()
        if display != update_param:
            display.update(update_param)

            image = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(image)

            Patch = display['patch']
            Voice = "Voice:" + voice_list [display['voice']]
            MOD = display['mod']
            REV = display['reverb']
            DEL = display['delay']

            draw.text(xy= (width/2,(1*height)/4),text=Patch, font=font,anchor='mm', fill= target_theme_color)
            
            draw.rectangle(((2*width/3 - offset/2),height/2, width, height), outline=outline_color, width=offset)
            draw.rectangle((0,height/2, width, height), outline=outline_color, width=offset)
            draw.rectangle((0,0, width, height), outline=outline_color, width=offset)
            
            Vol = "Vol      "
            Gain = "Gain"
            Bass = "Bass"
            Trebble = "Treb"
            ISF = "ISF"

            status_bar_width = (2*width/3 - offset * 2)

            text_height_start = (height/2) + text_offset
            draw.text(xy= (text_offset,text_height_start) ,text=Voice, font=font2, fill=target_theme_color)
            text_height_start += draw.textsize(Voice, font=font2)[1] + 4
            
            next_text_height = draw.textsize(Vol, font=font2)[1]
            
            draw.text(xy= (text_offset,text_height_start) ,text=Gain, font=font2, fill=target_theme_color)
            rect_width = draw.textsize(Vol, font=font2)[0]
            fill_width = get_status_bar_fill(display['gain'], (rect_width + 1), status_bar_width, 100, scale=(0,10))
            draw.rectangle((rect_width,text_height_start, 2*width/3 - offset * 2, text_height_start + next_text_height), outline=status_bar_outline, width=1)
            draw.rectangle((rect_width + 1,text_height_start + 1, fill_width, text_height_start - 1 + next_text_height), fill=target_theme_color, width=1)
            text_height_start += draw.textsize(Bass, font=font2)[1]

            draw.text(xy= (text_offset,text_height_start) ,text=Vol, font=font2, fill=target_theme_color)
            draw.text(xy= (text_offset + 10+ status_bar_width,text_height_start) ,text="MOD", font=font2,
                            fill= target_theme_color if MOD else bg_color)
            
            rect_width = draw.textsize(Vol, font=font2)[0]
            fill_width = get_status_bar_fill(display['volume'], (rect_width + 1), status_bar_width, 100, scale=(0,10))
            draw.rectangle((rect_width,text_height_start, 2*width/3 - offset * 2, text_height_start + next_text_height), outline=status_bar_outline, width=1)
            draw.rectangle((rect_width + 1,text_height_start + 1, fill_width, text_height_start - 1 + next_text_height), fill=target_theme_color, width=1)
            text_height_start += next_text_height

            draw.text(xy= (text_offset,text_height_start) ,text=Bass, font=font2, fill=target_theme_color)
            draw.text(xy= (text_offset + 10+ status_bar_width,text_height_start) ,text="DELAY", font=font2,
                            fill= target_theme_color if DEL else bg_color)
            rect_width = draw.textsize(Vol, font=font2)[0]
            fill_width = get_status_bar_fill(display['bass'], (rect_width + 1), status_bar_width, 100, scale=(0,10))
            draw.rectangle((rect_width,text_height_start, 2*width/3 - offset * 2, text_height_start + next_text_height), outline=status_bar_outline, width=1)
            draw.rectangle((rect_width + 1,text_height_start + 1, fill_width, text_height_start - 1 + next_text_height), fill=target_theme_color, width=1)
            text_height_start += draw.textsize(Bass, font=font2)[1]

            draw.text(xy= (text_offset,text_height_start) ,text=Trebble, font=font2, fill=target_theme_color)
            draw.text(xy= (text_offset + 10+ status_bar_width,text_height_start) ,text="REVERB", font=font2,
                            fill= target_theme_color if REV else bg_color)

            rect_width = draw.textsize(Vol, font=font2)[0]
            fill_width = get_status_bar_fill(display['treble'], (rect_width + 1), status_bar_width, 100, scale=(0,10))
            draw.rectangle((rect_width,text_height_start, 2*width/3 - offset * 2, text_height_start + next_text_height), outline=status_bar_outline, width=1)
            draw.rectangle((rect_width + 1,text_height_start + 1, fill_width, text_height_start - 1 + next_text_height), fill=target_theme_color, width=1)

            text_height_start += draw.textsize(Trebble, font=font2)[1]

            draw.text(xy= (text_offset,text_height_start) ,text=ISF, font=font2, fill=target_theme_color)
            rect_width = draw.textsize(Vol, font=font2)[0]
            fill_width = get_status_bar_fill(display['isf'], (rect_width + 1), status_bar_width, 100, scale=(0,10))
            draw.rectangle((rect_width,text_height_start, 2*width/3 - offset * 2, text_height_start + next_text_height), outline=status_bar_outline, width=1)
            draw.rectangle((rect_width + 1,text_height_start + 1, fill_width, text_height_start - 1 + next_text_height), fill=target_theme_color, width=1)

            text_height_start += draw.textsize(ISF, font=font2)[1]

            disp.image(image)
            if not pwm_flag:
                pwm_flag = True
                process = subprocess.run(['gpio', '-g', 'mode', '{0}'.format(BACK_LED), 'pwm'])
                process = subprocess.run(['gpio', '-g', 'pwm', '{0}'.format(BACK_LED), '512'])