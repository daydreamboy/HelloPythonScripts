import sys
from PIL import Image

dark = Image.open(sys.argv[1], 'r').convert('LA').split()[0]
bright = Image.open(sys.argv[2], 'r').convert('LA').split()[0]
assert dark.size == bright.size


def conv(c1, c2):
    c = round(255 * c1 / (255 + c1 - c2)) if 255 + c1 - c2 != 0 else 0
    alpha = 255 + c1 - c2 if 255 + c1 - c2 <= 255 else 255
    global distortion
    if 255 + c1 - c2 > 255: distortion += 1
    return (c, alpha)

distortion = 0
newdata = list(map(conv, dark.getdata(), bright.getdata()))
print('distortion:%.2f%%' % (distortion / len(newdata) * 100))

img = Image.new('LA', dark.size)
img.putdata(newdata)

img.save(sys.argv[3], "PNG")
