from __future__ import division

import math
from StringIO import StringIO

from werkzeug import FileStorage
from PIL import Image


# full size -> square cropped at NxN
# full size -> thumbnailed to NxM


def square(image, size=None):
    width, height = image.size
    offset_from, offset = square_offset(image)
    if width > height:
        crop = (offset, 0, offset + height, height)
    else:
        crop = (0, offset, width, offset + width)
    image = image.crop(crop)
    if size is not None:
        image = image.resize((size, size), Image.ANTIALIAS)
    return ensure_rgb(image)


def constrain_width(image, new_width):
    width, height = image.size
    ratio = new_width / width
    # XXX handle images that are too small
    size = (new_width, int(height * ratio))
    image = image.resize(size, Image.ANTIALIAS)
    return ensure_rgb(image)


def to_storage(image, filename):
    outf = StringIO()
    image.save(outf, 'JPEG')
    outf.seek(0)
    return FileStorage(outf, filename, content_type='image/jpeg')


def ensure_rgb(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image


# XXX should we be saving retina-capable thumbnails?
# XXX how does the front-end handle an image that's smaller than the
# thumbnail and not square?
def constrain_shortest_dimension(image, max_size):
    """Resize image setting the smaller dimension to max_size."""
    width, height = image.size
    if height > width:
        ratio = max_size / width
        size = (max_size, int(height * ratio))
    else:
        ratio = max_size / height
        size = (int(width * ratio), max_size)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    # XXX what to do if the image is smaller than this?
    return image.resize(size, Image.ANTIALIAS)


def square_offset(image):
    """Return hints at how to crop the image, leaving the best square."""
    width, height = image.size
    offset_from = None
    offset = 0
    max_chunk_size = 10

    if width > height:
        offset_from = 'left'
        while (width - offset) > height:
            chunk_size = min(width - offset - height, max_chunk_size)
            left = image.crop((offset, 0, offset + chunk_size, height))
            right = image.crop((width - chunk_size, 0, width, height))
            if entropy(left) < entropy(right):
                offset += chunk_size
            else:
                width -= chunk_size
    elif height > width:
        offset_from = 'top'
        while (height - offset) > width:
            chunk_size = min(height - offset - width, max_chunk_size)
            top = image.crop((0, offset, width, offset + chunk_size))
            bottom = image.crop((0, height - chunk_size, width, height))
            if entropy(top) < entropy(bottom):
                offset += chunk_size
            else:
                height -= chunk_size

    return (offset_from, offset)


def entropy(image):
    """Calculate the image's entropy: -sum(p * log2(p))."""
    from pprint import pprint
    hist = image.histogram()
    total_pixels = sum(hist)
    hist = [h / total_pixels for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])
