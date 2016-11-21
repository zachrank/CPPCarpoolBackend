from PIL import Image
from resizeimage import resizeimage

#(incoming image, read/write binary option)
with open('test-image.png', 'r+b') as incoming:
    with Image.open(incoming) as image:
        outgoing = resizeimage.resize_cover(image, [256, 256])
        outgoing.save('test-image-modified.jpg', "JPEG")
        #c.execute("SELECT * FROM users WHERE picture = cover")
