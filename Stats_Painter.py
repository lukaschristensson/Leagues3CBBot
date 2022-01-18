import math
import random
import time
import threading
from PIL import ImageDraw, Image, ImageFont
from ColorManip import *

# the colors used for the categories
IRON_REPUBLIC = {
    'color': '#5F45F45F4'
}
ONE_SHOT = {
    'color': '#806000000'
}

images = {}
fonts = {}

png_lock = threading.Lock()

# these are the categories that'll be drawn
CATEGORIES = {
    'HIGHEST MAX XP'       : {'title':'HIGHEST MAX XP'        , 'point_func':lambda p:p['total']['xp']},
    'HIGHEST TOTAL LVL'    : {'title':'HIGHEST TOTAL LVL'     , 'point_func':lambda p:p['total']['level']},
    'HIGHEST MAX CLUES'    : {'title':'HIGHEST MAX CLUES'     , 'point_func':lambda p:p['Clue Scrolls (all)']['kc']},
    'HIGHEST MAX ZULRAH KC': {'title':'HIGHEST MAX ZULRAH KC' , 'point_func':lambda p:p['Zulrah']['kc']},
    'HIGHEST MAX BOSS KC1' : {'title':'HIGHEST MAX BOSS KC1'  , 'point_func':lambda p:10**11},
    'HIGHEST MAX BOSS KC2' : {'title':'HIGHEST MAX BOSS KC2'  , 'point_func':lambda p:random.uniform(0, 10**7)},
    'HIGHEST MAX BOSS KC3' : {'title':'HIGHEST MAX BOSS KC3'  , 'point_func':lambda p:random.uniform(0, 10**7)},
    'HIGHEST MAX BOSS KC4' : {'title':'HIGHEST MAX BOSS KC4'  , 'point_func':lambda p:random.uniform(0, 10**7)},
    'HIGHEST MAX BOSS KC5' : {'title':'HIGHEST MAX BOSS KC5'  , 'point_func':lambda p:random.uniform(0, 10**7)},
}
CATEGORY_SIZE = 40, 60  # inner and outer radius of the category orb


'''
originally made the script for a tkinter canvas, switched to PILs image draw function
so imma just translate from tkinter commands to pil commands using this, that way
i can draw on the image like i would in tkinter
'''
class UtilCanvas:
    def __init__(self, background):
        self.im = background
        self.draw = ImageDraw.Draw(background, 'RGBA')

    @staticmethod
    def to_pil_fill(s):
        if type(s) != str: return s
        char_l = (len(s)-1) // 3
        return \
            int(255*int(s[1+char_l*0:1+char_l*1], 16)/((16**char_l)-1)), \
            int(255*int(s[1+char_l*1:1+char_l*2], 16)/((16**char_l)-1)), \
            int(255*int(s[1+char_l*2:1+char_l*3], 16)/((16**char_l)-1)), \
            255

    def create_image(self, x0, y0, image):
        self.im.paste(image, (int(x0 - image.size[0]/2), int(y0 - image.size[1]/2)), image.convert('RGBA'))

    def create_text(self, x0, y0, text='', fill='#000', font=('COCO SHARP', 36), anchor=None):
        fill = UtilCanvas.to_pil_fill(fill)
        font = ImageFont.truetype(fonts[font[0]], font[1])
        w, h = self.draw.textsize(text, font=font)

        if anchor is None:
            self.draw.text((x0 - w/2, y0 - h/2), text, fill=fill, font=font, align='left')
        elif anchor == 'left':
            self.draw.text((x0, y0 - h/2), text, fill=fill, font=font, align=anchor)
        else:
            self.draw.text((x0-w, y0 - h/2), text, fill=fill, font=font, align=anchor)

    def create_line(self, x0, y0, x1, y1, fill='#000', width=1):
        fill = UtilCanvas.to_pil_fill(fill)
        self.draw.line([x0, y0, x1, y1], fill=fill, width=width)

    # can't make it transparent with just an alpha channel, since the draw replaces whatever pixels
    # are there, so gotta draw it on a temp img, then alpha_composite it together... ugh
    def create_empty_circle(self, x0, y0, x1, y1, width, outline):
        temp = Image.new('RGBA', self.im.size, (0, 0, 0 ,0))
        ImageDraw.Draw(temp, 'RGBA').ellipse((x0-width/2, y0-width/2, x1+width/2, y1+width/2), fill=(0, 0, 0, 0), outline=outline, width=width)
        self.im.paste(Image.alpha_composite(self.im, temp))

    def rounded_rect(self, x0, y0, x1, y1, fill='#000', outline=None, width=0, radius=3):
        fill = UtilCanvas.to_pil_fill(fill)
        self.draw.rounded_rectangle((x0, y0, x1, y1), fill=fill, outline=outline, width=width, radius=radius)

    def save(self, name='snapshot'):
        self.im.resize((2000, 2000)).save('./Res/'+name+'.png', 'PNG')

    def draw_arc(self, x0, y0, r1, r2, from_angle, to_angle, fill, lamp_color=None):
        num_pix_in_outer = int(math.ceil(2 * r2 * math.pi) * abs(from_angle - to_angle) / (2 * math.pi))
        # adjust angles .5 pi to make the 0 angle represent the top of the circle
        from_angle -= math.pi / 2
        to_angle -= math.pi / 2
        for i in range(num_pix_in_outer):
            # find the approximate pixel on the inner and outer circle
            ang = from_angle + (to_angle - from_angle) * i / num_pix_in_outer
            inner_pix = x0 + math.cos(ang) * r1, y0 + math.sin(ang) * r1
            outer_pix = x0 + math.cos(ang) * r2, y0 + math.sin(ang) * r2

            # draw a line between the pixels
            # the mix in this case acts as if it's light hitting a surface, part of the light bouncing back is from the light source, part is from the object
            # if it's mixed as a function of a distance from something, you get a light source(ish, inverse square law and stuff)
            if lamp_color:
                self.create_line(inner_pix[0], inner_pix[1], outer_pix[0], outer_pix[1],
                              fill=UtilCanvas.to_pil_fill(mix_color(lamp_color, fill, 0.7 * (1 / (1 + abs(ang - to_angle) ** 2)))), width=2)
            else:
                self.create_line(inner_pix[0], inner_pix[1], outer_pix[0], outer_pix[1], fill=UtilCanvas.to_pil_fill(fill), width=2)


def load_resources():
    images['background']  = Image.open('./Res/3Dbackground_3.png').resize((1000, 1000))
    images['swords']      = Image.open('./Res/combat_icon.png').resize((40, 40))
    fonts['COCO SHARP'] = './Res/CocoSharp-Bold.otf'

def __draw_category__(c, category, ir_members, os_members, DRAWN_CATEGORIES):
    font_size = 14
    r1, r2 = CATEGORY_SIZE
    # x is just padding and y is to accommodate for the backgrounds header
    startx = 150
    starty = 390
    # 4 per row except for the last one
   # if len(DRAWN_CATEGORIES)//4 != 2:
    x0 = startx + ((len(DRAWN_CATEGORIES)%3)+0.25)*((1000 - 2*startx)//2.5)
   # else:
   #     x0 = startx + ((int(c['width']) - 2*startx)//2)

    y0 = starty + ((1000 - starty)//2.5)*(len(DRAWN_CATEGORIES)//3)

    # find the best player from each clan in the category
    best_os = max(os_members, key=category['point_func'])
    best_ir = max(ir_members, key=category['point_func'])

    # reformat for easier use, could be better structured but i cba
    best_os = best_os['rsn'], int(category['point_func'](best_os))
    best_ir = best_ir['rsn'], int(category['point_func'](best_ir))

    ANGLE = 2*math.pi*int(best_ir[1])/(int(best_ir[1])+int(best_os[1]))
    # dirty conversion to ks and ms
    if 10000 > best_os[1]:
        best_os = best_os[0], str(best_os[1])
    elif 1000000 > best_os[1] >= 10000:
        best_os = best_os[0], str(best_os[1]//1000) + 'k'
    elif 1000000000 > best_os[1] >= 1000000:
        best_os = best_os[0], str(best_os[1]//1000000) + 'm'
    else:
        best_os = best_os[0], str(best_os[1] // 1000000000) + 'b'

    if 10000 > best_ir[1]:
        best_ir = best_ir[0], str(best_ir[1])
    elif 1000000 > best_ir[1] >= 10000:
        best_ir = best_ir[0], str(best_ir[1]//1000) + 'k'
    elif 1000000000 > best_ir[1] >= 1000000:
        best_ir = best_ir[0], str(best_ir[1]//1000000) + 'm'
    else:
        best_ir = best_ir[0], str(best_ir[1] // 1000000000) + 'b'

    # draw a sort of framing for the category
    c.rounded_rect(
        x0 - r2*1.7,
        y0 - r2 - 30 - 3.2 * font_size - 1.6*font_size,
        x0 + r2*1.7,
        y0 + r2 + 10,
        radius=10,
        fill='#222'
    )
    # draws an arc for each clan with respective colors, results in a circle
    c.draw_arc(x0, y0, r1, r2, 0, ANGLE, IRON_REPUBLIC['color']   ,'#fffffffff')#'#000fff000' if ANGLE % (math.pi*2) > math.pi else '#fff000000')#'#fffffffff' if ANGLE % (math.pi*2) > math.pi else '#fff000000')
    c.draw_arc(x0, y0, r1, r2, math.pi*2, ANGLE, ONE_SHOT['color'],'#000000000')#'#000fff000' if ANGLE % (math.pi*2) < math.pi else '#fff000000')#'#fffffffff' if ANGLE % (math.pi*2) > math.pi else '#fff000000')

    #draws the outlines of the 2 arcs
    ANGLE -= math.pi/2
    c.create_empty_circle(x0-r1, y0-r1, x0+r1, y0+r1, outline='#000', width=7)
    c.create_empty_circle(x0-r2, y0-r2, x0+r2, y0+r2, outline='#000', width=7)
    c.create_line(
        x0+math.cos(ANGLE) * r1,
        y0+math.sin(ANGLE) * r1,
        x0+math.cos(ANGLE) * r2,
        y0+math.sin(ANGLE) * r2,
        width=9, fill='#000'
    )
    c.create_line(
        x0+math.cos(ANGLE) * r1,
        y0+math.sin(ANGLE) * r1,
        x0+math.cos(ANGLE) * r2,
        y0+math.sin(ANGLE) * r2,
        width=4, fill=intensify(IRON_REPUBLIC['color'] if ANGLE > math.pi/2 else ONE_SHOT['color'], 2) # lighten to give the appearance of being illuminated
    )
    c.create_line(x0, y0-r1, x0, y0-r2, width=7, fill='#000')

    # draw the swords
    c.create_image(x0, y0-r2-(r1-r2)/2., image=images['swords'])

    # draws text above the progression orbs
    c.create_text(
        x0,
        y0 - r2 - 30 - 3.2*font_size,
        text=category['title'], font=('COCO SHARP', int(font_size*1.1), 'bold'),fill='#ccc'
    )
    c.create_text(
        x0 + font_size*1 - font_size*7,
        y0 - r2 - 30 - 1*font_size*1.3,
        text=best_os[0], font=('COCO SHARP', font_size), anchor='left',fill='#ccc'
    )
    c.create_text(
        x0 + font_size*3,
        y0 - r2 - 30 - 1*font_size*1.3,
        text='OS', font=('COCO SHARP', font_size), anchor='right',fill='#ccc'
    )
    c.create_text(
        x0 + font_size*6,
        y0 - r2 - 30 - 1*font_size*1.3,
        text=best_os[1], font=('COCO SHARP', font_size), anchor='right',fill='#ccc'
    )
    c.create_text(
        x0 + font_size*1 - font_size*7,
        y0 - r2 - 30 - 0*font_size*1.3,
        text=best_ir[0],font=('COCO SHARP', font_size), anchor='left',fill='#ccc'
    )
    c.create_text(
        x0 + font_size*3,
        y0 - r2 - 30 - 0*font_size*1.3,
        text='IR',font=('COCO SHARP', font_size), anchor='right',fill='#ccc'
    )
    c.create_text(
        x0 + font_size*6,
        y0 - r2 - 30 - 0*font_size*1.3,
        text=best_ir[1], font=('COCO SHARP', font_size), anchor='right',fill='#ccc'
    )

    # line under the title
    c.create_line(
        x0-90,
        y0 - r2 - 30 - 2.5*font_size,
        x0+90,
        y0 - r2 - 30 - 2.5*font_size,
        width=2, fill='#ccc'
    )

    # keep track of which categories have been drawn
    DRAWN_CATEGORIES.append(category)

def draw_all_categories(ir_data, os_data):
    c = UtilCanvas(images['background'])
    DRAWN_CATEGORIES = []
    start_time = time.time()
    part_time = time.time()
    for cat in CATEGORIES:
        __draw_category__(c, CATEGORIES[cat], ir_data, os_data, DRAWN_CATEGORIES)
    print('Categories drawn',time.time() - part_time, 's')
    part_time = time.time()
    # c.im.show()
    png_lock.acquire()
    c.save()

    print('Image saved',time.time() - part_time, 's')
    print('Total time: %3f s'%(time.time() - start_time))
    return png_lock
