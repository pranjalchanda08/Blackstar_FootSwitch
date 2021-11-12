from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import digitalio
import board

import time
import json

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO.SPI as SPI
import adafruit_rgb_display.ili9341 as ili9341

import paho.mqtt.client as mqtt

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

# Load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 20)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf", 30)

display = {
    "patch" : "default",
    "volume" : 10,
    "ISF" : 9, 
    "Base" : 5,
    "Treble" : 3
}
def on_message(client, userdata, message):
        global display
        msg = message.payload.decode()
        update_param = json.loads(msg)
        display.update(update_param)
        print(display)

try:
    client = mqtt.Client("LocalHostDisplay")
    client.connect("localhost")
    client.subscribe("Footswitch/Display")
    client.loop_start()
    client.on_message=on_message
except Exception as e:
    print(" Exception in Parent thread: " + str(e))

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=(255, 255, 255), width = 2, fill=0)
    
    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    
    # Write four lines of text.
    y = padding
    
    vol = "Volume  :{}".format(display['volume'])
    isf = "ISF     :{}".format(display['ISF'])
    Base = "Base    :{}".format(display['Base'])
    Treble = "Treble  :{}".format(display['Treble'])
    patch =  "{}".format(display['patch'])
    draw.text((x, y), vol, font=font, fill="#FFFF00")
    y += font.getsize(vol)[1]
    
    draw.text((x, y), isf, font=font, fill="#00FF00")
    y += font.getsize(isf)[1]
    
    draw.text((x, y), Base, font=font, fill="#0000FF")
    y += font.getsize(Base)[1]
    
    draw.text((x, y), Treble, font=font, fill="#FF00FF")
    y += font.getsize(Treble)[1]
    
    draw.text((x, y), patch, font=font2, fill="#FFFFFF")
    y += font.getsize(patch)[1]
    # Display image.
    disp.image(image)
    time.sleep(1)
    
# draw = disp.draw()

# font = ImageFont.truetype('font/PixelOperator8.ttf', 30)

# def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
#     # Get rendered font width and height.
#     draw = ImageDraw.Draw(image)
#     width, height = draw.textsize(text, font=font)
#     # Create a new image with transparent background to store the text.
#     textimage = Image.new('RGBA', (width, height), (0,0,0,0))
#     # Render the text.
#     textdraw = ImageDraw.Draw(textimage)
#     textdraw.text((0,0), text, font=font, fill=fill)
#     # Rotate the text image.
#     rotated = textimage.rotate(angle, expand=1)
#     # Paste the text into the image, using it as a mask for transparency.
#     image.paste(rotated, position, rotated)


# draw_rotated_text(disp.buffer, "Your dad's name is Natesh", (90, -(10 * 10)), 90, font, fill=(255,0,255))
# disp.display()