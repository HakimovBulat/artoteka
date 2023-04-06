from base64 import b64encode as enc64
from base64 import b64decode as dec64
from io import BytesIO
from PIL import Image


pict = "static\img\dog.webp"
def binary_pic(pict):
    with open(pict, "rb") as f:
        binary = enc64(f.read())
    return binary

def export(binary):
    image = BytesIO(dec64(binary))
    pillow = Image.open(image)
    x = pillow.show()


export(binary_pic(pict))