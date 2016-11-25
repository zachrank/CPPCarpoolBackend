from PIL import Image
from resizeimage import resizeimage

# returns an image that has been cropped and resized to 256x256
def resizeimage(incomingimage):
    #(incoming image, read/write binary option)
    with open(incomingimage, 'r+b') as incoming:
        with Image.open(incoming) as image:
            outgoing = resizeimage.resize_cover(image, [256, 256])
            return outgoing.save('resized-image.jpg', "JPEG")
