from __future__ import division

import math

from PIL import Image


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
    # XXX what to do if the image is smaller than this?
    return image.resize(size, Image.ANTIALIAS)


def square_offset(image):
    """Return hints at how to crop the image, leaving the best square."""
    width, height = image.size
    orientation = 'square'
    offset = 0
    max_chunk_size = 10

    if width > height:
        orientation = 'landscape'
        while (width - offset) > height:
            chunk_size = min(width - offset - height, max_chunk_size)
            left = image.crop((offset, 0, offset + chunk_size, height))
            right = image.crop((width - chunk_size, 0, width, height))
            if entropy(left) < entropy(right):
                offset += chunk_size
            else:
                width -= chunk_size
    elif height > width:
        orientation = 'portrait'
        while (height - offset) > width:
            chunk_size = min(height - offset - width, max_chunk_size)
            top = image.crop((0, offset, width, offset + chunk_size))
            bottom = image.crop((0, height - chunk_size, width, height))
            if entropy(top) < entropy(bottom):
                offset += chunk_size
            else:
                height -= chunk_size

    return {'orientation': orientation, 'offset': offset}


def entropy(image):
    """Calculate the image's entropy: -sum(p * log2(p))."""
    from pprint import pprint
    hist = image.histogram()
    total_pixels = sum(hist)
    hist = [h / total_pixels for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])
