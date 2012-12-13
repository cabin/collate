from __future__ import division

import math

from PIL import Image


# XXX how does the front-end handle an image that's smaller than the
# thumbnail and not square?

# what I really want:
#    one full sized image -- full_filename
#    one image constrained to an arbitrary width -- grid_filename
#    one (direction, pixel count) offset tuple to use with grid_filename to
#        present a square image
#    maybe one mid_filename for saving bandwidth/browser crop?


# XXX could combine square_*_image functions very easily
# XXX could reduce croppings per https://gist.github.com/a54cd41137b678935c91
# rather than actually cropping, how about keeping just one max-width image
# that can be too tall, and saving the crop offset for square?

########
# initial upload: dim, max-height & max-width so we don't have to crop in JS
# catch upload in python, figure out orientation (landscape or portrait ... or
# square!) and how much to crop off of the top/left; save and return all that
#       original_size_urL
#       thumb_size_url (which is really thumb_width and full height)
#       orientation (landscape/portrait/square)
#       original filename? source url? caption?
# when returns, blend through into the new image (via rendering a backbone
# view)


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





''' Ruby version!

  def crop(crop_width = 100, crop_height = 100)
    x, y, width, height = 0, 0, @image.width, @image.height
    slice_length = 16

    while (width - x) > crop_width
      slice_width = [width - x - crop_width, slice_length].min

      left = @image.crop(x, 0, slice_width, @image.height)
      right = @image.crop(width - slice_width, 0, slice_width, @image.height)

      if entropy(left) < entropy(right)
        x += slice_width
      else
        width -= slice_width
      end
    end

    while (height - y) > crop_height
      slice_height = [height - y - crop_height, slice_length].min

      top = @image.crop(0, y, @image.width, slice_height)
      bottom = @image.crop(0, height - slice_height, @image.width, slice_height)

      if entropy(top) < entropy(bottom)
        y += slice_height
      else
        height -= slice_height
      end
    end

    if debug
      return @image.rect(x, y, x + crop_width, y + crop_height, ChunkyPNG::Color::WHITE)
    end

    @image.crop(x, y, crop_width, crop_height)
  end


'''
