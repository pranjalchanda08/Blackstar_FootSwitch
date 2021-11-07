import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class OLED():

    def __init__(self):
        # 128x32 display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        # Initialize library.
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        self.padding = -2
        self.top = self.padding
        self.bottom = self.height-self.padding

    def disp_text(self, text_str:str, xy_pos:tuple):
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
        self.draw.text(text=text_str, xy=xy_pos, font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()