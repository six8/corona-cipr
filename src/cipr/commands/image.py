import math
import Image
from os import path
from cipr.commands import app

def scale_and_fit(im, requested_size):
    im = im.copy()

    x, y   = [float(v) for v in im.size]
    xr, yr = [float(v) for v in requested_size]

    ratio = min(xr/x, yr/y)

    width = int(math.ceil(x * ratio))
    height = int(math.ceil(y * ratio))

    width, height = int(width), int(height)
    if width != x or height != y:
        im.thumbnail((width, height), resample=Image.ANTIALIAS)

    return im

def scale_and_crop(im, requested_size):
    im = im.copy()

    x, y   = [float(v) for v in im.size]
    xr, yr = [float(v) for v in requested_size]

    ratio = max(xr/x, yr/y)

    width = int(math.ceil(x * ratio))
    height = int(math.ceil(y * ratio))

    width, height = int(width), int(height)
    if width != x or height != y:
        im.thumbnail((width, height), resample=Image.ANTIALIAS)

    x, y   = [float(v) for v in im.size]
    ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
    if ex or ey:
        s = (int(math.ceil(ex)), int(math.ceil(ey)), int(math.ceil(x-ex)), int(math.ceil(y-ey)))
        im = im.crop(s)

    return im
    
icon_sizes = {
    # 'iTunesArtwork' : ('icon', 512, 512, scale_and_crop),
    'Icon.png' : ('icon', 57, 57, scale_and_crop),
    'Icon@2x.png' : ('icon', 114, 114, scale_and_crop),
    'Icon-72.png' : ('icon', 72, 72, scale_and_crop),
    'Icon-Small.png' : ('icon', 29, 29, scale_and_crop),
    'Icon-Small@2x.png' : ('icon', 58, 58, scale_and_crop),
    'Icon-Small-50.png' : ('icon', 50, 50, scale_and_crop),
}

@app.command
def makeicons(source):
    """
    Create all the neccessary icons from source image
    """
    im = Image.open(source)
    for name, (_, w, h, func) in icon_sizes.iteritems():
        print('Making icon %s...' % name)
        tn = func(im, (w, h))
        bg = Image.new('RGBA', (w, h), (255, 255, 255))
        x = (w / 2) - (tn.size[0] / 2)
        y = (h / 2) - (tn.size[1] / 2)
        bg.paste(tn, (x, y))

        bg.save(path.join(env.dir, name))            