import sys
import os
import numpy as np
from library import *
import json

global cache

try:
    with open('cache.txt', 'r') as f:
        cache = json.loads(f.read()) or {}
except Exception,e:
    cache = {}
if not os.path.exists("letters"):
    os.makedirs("letters")


def save_letter(roi, letter, i, j):
    dir = "letters/%s" % chr(letter)
    if not os.path.exists(dir):
        os.makedirs(dir)
    cv2.imwrite("%s/%s_%s.png"% (dir,i,j), roi)


def train(image, index):
    global samples
    global cache

    im, t = filter_image(image)
    b = find_letters(t.copy())
    if len(b) != 5:
        return


    display_bounds(im.copy(), b)
    cv2.imshow("im", t)
    cv2.waitKey(0)

    print 'Enter captcha %s' % image
    if index in cache:
        answers = cache[index]
    else:
        answers = []
        while len(answers)<5:
            key = cv2.waitKey(0)
            if key == 27:
                sys.exit(0)
            elif key == 8:
                answers = answers[:-1]
            elif 256 > key > 32:
                answers.append(key)
        cache[index] = answers
        with open('cache.txt', 'w+') as f:
            f.write(json.dumps(cache))

    rois = get_roi(t, b)
    for i in xrange(5):
        roi = rois[i]
        #save_letter(roi.reshape((height, width, 1)), answers[i], index, i)

for i in xrange(100,1000):
    train('images/%s.jpg' % i, str(i))