"""Image Utils."""
# Standard Python Libraries
import base64
from io import BytesIO

# Third-Party Libraries
from PIL import Image


def reduce_image_size(fp, filetype):
    """Reduce image to a maximum of 400px by 400px."""
    image = Image.open(fp)
    maxsize = (400, 400)
    image.thumbnail(maxsize, Image.ANTIALIAS)
    buffer = BytesIO()
    image.save(buffer, filetype.split("/")[-1].upper())
    buffer.seek(0)
    return buffer


def base64_encode_image(fp):
    """Return base64 encoded version of image."""
    return base64.b64encode(fp.read())
