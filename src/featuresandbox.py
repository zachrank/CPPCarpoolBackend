from PIL import Image

from resizeimage import resizeimage

from api import db
from psycopg2.extras import DictCursor

with open('test-image.png', 'r+b') as f:
    with Image.open(f) as image:
        cover = resizeimage.resize_cover(image, [256, 256])
        cover.save('test-image-cover.png', image.format)
        #c.execute("SELECT * FROM users WHERE picture = cover")
