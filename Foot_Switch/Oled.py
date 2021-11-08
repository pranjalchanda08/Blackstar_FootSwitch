import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import logging
import time
import paho.mqtt.client as mqtt

def animate(mqtt_client):
    global text
    def on_message(client, userdata, message):
        global text
        text = message.payload.decode()

    mqtt_client.on_message=on_message

    disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
    disp.begin()
    width = disp.width
    height = disp.height
    disp.clear()
    disp.display()
    image = Image.new('1', (width, height))
    font = ImageFont.truetype('font/PixelOperatorMono8-Bold.ttf', 20)
    draw = ImageDraw.Draw(image)
    offset = height/2 - 4
    velocity = -20
    startpos = width
    print('Press Ctrl-C to quit.')
    pos = startpos
    while True:
        maxwidth,_ = draw.textsize(text, font=font)
        # Clear image buffer by drawing a black filled box.
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        # Enumerate characters and draw them offset vertically based on a sine wave.
        x = pos
        for i, c in enumerate(text):
            # Stop drawing if off the right side of screen.
            if x > width:
                break
            # Calculate width but skip drawing if off the left side of screen.
            if x < -10:
                char_width,_ = draw.textsize(c, font=font)
                x += char_width
                continue
            # Calculate offset from sine wave.
            y = offset
            # Draw text.
            draw.text((x, y), c, font=font, fill=255)
            # Increment x position based on chacacter width.
            char_width,_ = draw.textsize(c, font=font)
            x += char_width
        # Draw the image buffer.
        disp.image(image)
        disp.display()
        # Move position for next frame.
        pos += velocity
        # Start over if text has scrolled completely off left side of screen.
        if pos < -maxwidth:
            pos = startpos
        # Pause briefly before drawing next frame.
        time.sleep(0.1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" OLED ")

try:
    client = mqtt.Client("LocalHostDisplay")
    client.connect("localhost")
    client.subscribe("Footswitch/Display")
    client.loop_start()
    animate(mqtt_client=client)
except Exception as e:
    logger.error(" Exception in Parent thread: " + str(e))
