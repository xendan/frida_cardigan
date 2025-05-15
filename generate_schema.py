import os, sys
import random
import math
from PIL import Image, ImageDraw, ImageFont

src_img = "img/Frida_With_Monkeys.jpg"
box = (0, 2, 665, 888)
wdc, hdc = 100, 74 
dx_img = (box[2] - box[0]) / wdc
dy_img = (box[3] - box[1]) / hdc
dc0_w_px, dc0_h_px = 30, 60
scale_w, scale_h = dc0_w_px * 2, dc0_h_px
grid_width = 3
font_size = 3

palette_img = "out/palette.jpg"

def to_rgb(hex_num):
    base = 256
    blue = hex_num % base
    green = int(((hex_num - blue) / base) % base)
    red = int(((hex_num - blue) - green * base) /(base * base))
    return (red, green, blue)

palette = list(map(to_rgb, [0xc8c7b0, 0xf0e8d8, 0xa5a773, 0xc5e1f7, 0x010101, 0xe03e24, 0xbccac0, 0xc56644, 0x785a45]))

def grid_color(num):
    if (num + 1) % 10 == 0:
        return "white"
    elif (num + 1) % 5 ==0:
        return "yellow"
    else:
        return "green"

def get_closest_color_index(color):
    color_dist_min = 3*(256**2)
    index_min = 0

    for i in range(len(palette)):
        p_color = palette[i]
        color_dist = sum((p_color[j] - color[j]) ** 2 for j in range(3))
        if (color_dist < color_dist_min):
            color_dist_min = color_dist
            index_min = i

    return index_min        
            

def get_max_index(buckets):    
    max_ind = 0
    for i in range(len(buckets)):
        if (buckets[i] > buckets[max_ind]):
            max_ind = i
    return max_ind

def average_color(img, x, y):
    buckets = [0] * len(palette)

    for i in range(math.floor(dx_img)):
        for j in range(math.floor(dy_img)):
            color = img.getpixel((int(box[0] + x * dx_img + i), int(box[1] + y * dy_img + j)))
           
            index = get_closest_color_index(color)
            buckets[index] = buckets[index] + 1
            
    max_ind = get_max_index(buckets)

    return (max_ind, palette[max_ind])

try:
    with Image.open(src_img) as img:
        print("Hola Frida!!")
        print(src_img, img.format, f"{img.size}x{img.mode}")
        out_w, out_h = (wdc + 1) * dc0_w_px - 1 + scale_w * 2, (hdc + 1) * dc0_h_px - 1 + scale_h * 2
        out = Image.new(mode="RGB", size=(out_w, out_h))
        img_l = ImageDraw.Draw(out)
        for x in range(wdc + 1):
            xl = scale_w + x * dc0_w_px
            #img_l.text((xl + dc0_w_px * 0.5, scale_h), str(x + 1), "yellow")
            img_l.line([(xl, 0), (xl, out_h)], fill = grid_color(x - 1), width = grid_width)
            for y in range(hdc + 1):
                yl = scale_h + y * dc0_h_px
                if (x < wdc) and (y < hdc):
                    index, color = average_color(img, x, y)
                    r_x = x * dc0_w_px + scale_w
                    r_y = y * dc0_h_px + scale_h
                    img_l.rectangle([(r_x, r_y), (r_x + dc0_w_px, r_y + dc0_h_px)], fill = color)
                    #img_l.text((r_x, r_y), s tr(index), font_size = 3)
                    img_l.text((r_x + int(0.2 * dc0_w_px), r_y + int(0.2 * dc0_h_px)), str(index), font_size = 32, fill = "blue")
                img_l.line([(0, yl), (out_w, yl)], fill = grid_color(hdc - y - 1), width = grid_width)
        #.show()        
        out.save(palette_img)
        img.close()
        out.close()
except OSError:
    print("It is a bad day for your image")
