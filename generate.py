import random 
from PIL import Image, ImageDraw
import math
import os
import json
from dotenv import load_dotenv
load_dotenv()

# RGBeads: 42x42 pixel beads for digital necklaces, bracelets, etc.
# Traits: Size (sm: 20%, med: 50%, large: 30%), 
# Color: randomly selected RG and B, 
# Pattern (plain: 95%, btc-coated: 2%, eth-coated: 2%, btc-eth-coated: %1), Shape (circle: 44%, square: 44%, diamond: 2%)

traits = [{"trait_type": "Size", "value": {"small": .20, "medium": .50, "large": .30}},
            {"trait_type": "Color", "value": {}}]

coating_rgb_values = {"plain": None, "btc": (247,147,26), "eth": (192,192,192)}
size_values = {"small": [10,10], "medium": [20,20], "large": [30,30]}

NODE_PATH = os.getenv('NODE_PATH')
print(NODE_PATH)
NUM_BEADS = int(os.getenv('NUM_BEADS'))

def generate(save_path="./beads"):
    for i in range(NUM_BEADS):
        # select size
        size = random.choices(["small", "medium", "large"], weights=[20, 50, 30])[0]
        # select R,G and B
        r = random.randrange(1, 255)
        g = random.randrange(1, 255)
        b = random.randrange(1, 255)
        rgb = (r,g,b)
        # select shape
        shape = random.choices(["circle", "square", "diamond"], weights=[44,44,2])[0]
        # select coating
        coating = random.choices(["plain", "btc", "eth"], weights=[95,4,1])[0]
        if coating in ["btc", "eth"]:
            print(f"{coating} COATING: ", i)
        if size == "large":
            print("LARGE: ", i)
        wh = size_values[size]
        coating_rgb = coating_rgb_values[coating]
        img = render_image(wh, rgb, shape, coating_rgb, i)
        
        img_folder_path = os.path.join(save_path, str(i))
        if not os.path.exists(img_folder_path):
            os.makedirs(img_folder_path)
        img_path = os.path.join(img_folder_path,  f"{i}.png")
        metadata_path = os.path.join(img_folder_path, f"{i}.json")

        metadata = {"attributes": [{"trait_type": "Red", "diplay_type": "number", "value": r, "max_value": 255},
                        {"trait_type": "Green", "diplay_type": "number", "value": g, "max_value": 255},
                        {"trait_type": "Blue", "diplay_type": "number", "value": b, "max_value": 255},
                        {"trait_type": "Shape", "value": shape},
                        {"trait_type": "Coating", "value": coating},
                        {"trait_type": "Size", "value": size}]}

        img.resize((350, 350)).save(img_path, format='PNG')
        json.dump(metadata, open(metadata_path, "w"))

def render_image(wh, rgb, shape, coating_rgb, i):
    def distance(ax, ay, bx, by):
        return math.sqrt((by - ay)**2 + (bx - ax)**2)

    #rotates point `A` about point `B` by `angle` radians clockwise.
    def rotated_about(ax, ay, bx, by, angle):
        radius = distance(ax,ay,bx,by)
        angle += math.atan2(ay-by, ax-bx)
        return (
            round(bx + radius * math.cos(angle)),
            round(by + radius * math.sin(angle))
        )

    w, h = tuple(wh)
    im = Image.new('RGB', (50, 50), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    cx, cy = 25, 25
    x1 = cx - (w/2)
    x2 = cx + (w/2)
    y1 = cy - (h/2)
    y2 = cy + (h/2)
    vertices = (x1,y1,x2,y2)
    
    if shape == "circle":
        # drawing circle
        draw.ellipse(vertices, fill=rgb, outline=coating_rgb)
    elif shape == "square":
        draw.rectangle(vertices, fill=rgb, outline=coating_rgb)            
    elif shape == "diamond":
        print("DIAMOND: ", i)
        vertices = ((x1,y1),(x2,y2))
        draw.rectangle(vertices, fill=rgb, outline=coating_rgb)
        im = im.rotate(45).convert("RGBA")
        fff = Image.new('RGBA', im.size, (255,)*4)
        # create a composite image using the alpha layer of rot as a mask
        out = Image.composite(im, fff, im)
        # save your work (converting back to mode='1' or whatever..)
        im = out.convert(im.mode)

        datas = im.getdata()

        new_image_data = []
        for item in datas:
            # change all black pixels to white
            if item == (0,0,0,255):
                # print("replace black")
                new_image_data.append((255, 255, 255))
            else:
                new_image_data.append(item)
                
        # update image data
        im.putdata(new_image_data)

    return im

# Create Data: Generate and save images and metadata blobs
generate()
