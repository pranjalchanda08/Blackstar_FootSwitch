# from PIL import Image
# from PIL import ImageDraw
# from PIL import ImageFont

# import Adafruit_ILI9341 as TFT
# import Adafruit_GPIO as GPIO
# import Adafruit_GPIO.SPI as SPI


# # Raspberry Pi configuration.
# DC = 24
# RST = 25
# SPI_PORT = 0
# SPI_DEVICE = 0

# # BeagleBone Black configuration.
# # DC = 'P9_15'
# # RST = 'P9_12'
# # SPI_PORT = 1
# # SPI_DEVICE = 0

# # Create TFT LCD display class.
# disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

# # Initialize display.
# disp.begin()

# # Clear the display to a red background.
# # Can pass any tuple of red, green, blue values (from 0 to 255 each).
# disp.clear((0, 0, 0))

# draw = disp.draw()

# font = ImageFont.truetype('font/PixelOperator8.ttf', 16)

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

# draw_rotated_text(disp.buffer, 'My name is pranjal.', (170, 90), 90, font, fill=(255,255,255))

# disp.display()


import time
import busio
import digitalio
from board import SCK, MOSI, MISO, D2, D8, D24

from adafruit_rgb_display import color565
import adafruit_rgb_display.ili9341 as ili9341


# Configuration for CS and DC pins:
CS_PIN = D8
DC_PIN = D24

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)

# Create the ILI9341 display:
display = ili9341.ILI9341(spi, cs=digitalio.DigitalInOut(CS_PIN),
                          dc=digitalio.DigitalInOut(DC_PIN))

# Main loop:
while True:
    # Clear the display
    display.fill(0)
    # Draw a red pixel in the center.
    display.pixel(120, 160, color565(255, 0, 0))
    # Pause 2 seconds.
    time.sleep(2)
    # Clear the screen blue.
    display.fill(color565(0, 0, 255))
    # Pause 2 seconds.
    time.sleep(2)
