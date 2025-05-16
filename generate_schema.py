import os, sys
import random
import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from sklearn.cluster import KMeans

src_img = "img/Frida_With_Monkeys.jpg"
colors_dir = "img/colors"
box = (0, 2, 665, 888)
wdc, hdc = 100, 74 
dx_img = (box[2] - box[0]) / wdc
dy_img = (box[3] - box[1]) / hdc
dc0_w_px, dc0_h_px = 40, 80
scale_w, scale_h = dc0_w_px * 2, dc0_h_px
grid_width = 3
font_size = 3
text_color = "blue"

schema_img = "out/schema.jpg"
colors_img = "out/colors.jpg"
col_sample_width = 1000
col_sample_heigth = 500 
col_sample_padding_y = 50
col_sample_padding_x = 150
col_width = col_sample_width * 2 + 4 * col_sample_padding_x
folder_y_padding = 30
dir_font_size = 48
dir_font_padding = 6

def to_rgb(hex_num):
    print(hex_num)
    base = 256
    blue = hex_num % base
    green = int(((hex_num - blue) / base) % base)
    red = int(((hex_num - blue) - green * base) /(base * base))
    return (red, green, blue)


def grid_color(num):
    if (num + 1) % 10 == 0:
        return "white"
    elif (num + 1) % 5 ==0:
        return "yellow"
    else:
        return "green"

def get_closest_color_index(palette, color):
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

def closest_color(img, palette, x, y):
   color = img.getpixel((int(box[0] + (x + 0.5) * dx_img), int(box[1] + (y+0.5) * dy_img )))
   ind = get_closest_color_index(palette, color)
   return (ind, palette[ind], color)

def get_dominant_color(img):
    res_img = img.resize((200, 200))
    img_np = np.array(img)

    pixels = img_np.reshape(-1, 3)

    k = 3
    kmeans = KMeans(n_clusters = k, random_state = 43, n_init = 5)
    kmeans.fit(pixels)

    counts = np.bincount(kmeans.labels_)
    dominant_color = kmeans.cluster_centers_[np.argmax(counts)].astype(int)
    return tuple(dominant_color)

    
def generate_palette():

    def get_dir_heigth(colors):
        return dir_font_size + dir_font_padding * 2 + int(math.ceil(len(colors) * 0.5))* (col_sample_heigth + col_sample_padding_y*2)

    print("Generating color palette..")
    palette = []

    color_files_by_dir = dict()
    for d in os.listdir(colors_dir):
        dir_path = os.path.join(colors_dir, d)
        color_files_by_dir[d] = os.listdir(dir_path)

    col_heigth = folder_y_padding * 2
    for (dir_name, colors) in color_files_by_dir.items():
        col_heigth = col_heigth + get_dir_heigth(colors)

    out = Image.new(mode = "RGB", size=(col_width, col_heigth), color = "gray")
    

    out_draw = ImageDraw.Draw(out)
    folder_title_y = folder_y_padding
    y0 = 0
    for dir_name, colors in color_files_by_dir.items():
        out_draw.text((col_sample_padding_x, folder_title_y), dir_name, font_size = dir_font_size, fill = "white")
        folder_title_y = folder_title_y + folder_y_padding + get_dir_heigth(colors)
        for i in range(len(colors)):
            color = colors[i]
            x = int(col_sample_padding_x if (i < len(colors) * 0.5) else col_sample_padding_x * 3 + col_sample_width)
            y = y0 + int((i % int(math.ceil(len(colors) * 0.5))) * (col_sample_heigth + col_sample_padding_y )) + dir_font_size + dir_font_padding * 2 + folder_y_padding + col_sample_padding_y
            img_path = os.path.join("img/colors", dir_name, color)
            print("... for " + img_path)
            with Image.open(img_path) as color_img:
                w = 5
                w_half = int(col_sample_width * 0.5)
                out_draw.rectangle([(x - w, y - w), (x + w_half + w, y + col_sample_heigth + w)], outline="white", width = w)
                dominant_color = get_dominant_color(color_img)
                palette.append(dominant_color)
                out_draw.rectangle([(x + w_half , y - w), (x + col_sample_width + w, y + col_sample_heigth + w)], outline="white", width = w, fill = dominant_color)
                out_draw.text((x + w_half , y - w), str(len(palette) - 1), font_size = 128,  fill = text_color)
                out.paste(color_img.resize((int(col_sample_width * 0.5), col_sample_heigth)), (x, y))
                
            color_img.close()
        y0 = y0 + get_dir_heigth(colors)   
            #out.show()
    out.save(colors_img)
    out.close()
    print("Colors generated")
    return palette

palette = generate_palette()
print(palette)

try:
    with Image.open(src_img) as img:
        print("Hola Frida!!")
        out_w, out_h = (wdc + 1) * dc0_w_px - 1 + scale_w * 2, (hdc + 1) * dc0_h_px - 1 + scale_h * 2
        out = Image.new(mode="RGB", size=(out_w, out_h))
        img_l = ImageDraw.Draw(out)
        not_used_colors = [True] * len(palette)
        for x in range(wdc + 1):
            xl = scale_w + x * dc0_w_px
            img_l.line([(xl, 0), (xl, out_h)], fill = grid_color(x - 1), width = grid_width)
            for y in range(hdc + 1):
                yl = scale_h + y * dc0_h_px
                if (x < wdc) and (y < hdc):
                    index, color, initial_color = closest_color(img, palette, x, y)
                    not_used_colors[index] = False
                    r_x = x * dc0_w_px + scale_w
                    r_y = y * dc0_h_px + scale_h
                    #iimg_l.rectangle([(r_x, r_y), (r_x + dc0_w_px, r_y + dc0_h_px)], fill = color)
                    img_l.polygon([(r_x, r_y), (r_x + dc0_w_px, r_y), (r_x, r_y + dc0_h_px)], fill = color)
                    img_l.polygon([(r_x + dc0_w_px, r_y), (r_x + dc0_w_px, r_y + dc0_h_px), (r_x, r_y + dc0_h_px)], fill = initial_color)
                    img_l.text((r_x + int(0.1 * dc0_w_px), r_y + int(0.2 * dc0_h_px)), str(index), font_size = 32, fill = text_color)
                img_l.line([(0, yl), (out_w, yl)], fill = grid_color(hdc - y - 1), width = grid_width)
        out.save(schema_img)
        img.close()
        out.close()
        for i in range(len(not_used_colors)):
            if (not_used_colors[i]):
                print("Color " + str(i) + " : "+ str(palette[i]) + ", not used")
except OSError:
    print("It is a bad day for your image")
