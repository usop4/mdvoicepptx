from PIL import Image, ImageDraw, ImageFont

def min2sec(s):
    min, sec = map(int, s.split(":"))
    return min * 60 + sec

im_width = 720
im = Image.new(
    "RGBA",
    size=(im_width,50),
    color=(0,0,0,0))
draw = ImageDraw.Draw(im)

def gen_img(s):

    mv_length = min2sec("10:16")
    mv_pos = min2sec(s)

    pos = im_width * mv_pos / mv_length

    triangle_width = 20
    triangle_height = 15
    draw.polygon(
        [
            (pos, 0), 
            (pos-triangle_width/2, triangle_height), 
            (pos+triangle_width/2, triangle_height)
        ], 
        fill=(255, 0, 0, 128), 
        outline=(255, 0, 0, 255)) 

    im.save("timebar.png")

gen_img("09:20")

