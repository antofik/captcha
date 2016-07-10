import sys
import os
import cv2
import numpy as np
from filter_image import parse_image
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

    orig, letters = parse_image(image)
    if not letters:
        return

    answers = []
    if index in cache:
        answers = cache[index]
        for i in range(len(answers)):
            save_letter(letters[i], answers[i], index, i)
    else:
        cv2.imshow("origin", orig)
        for i in range(len(letters)):
            letter = letters[i]
            cv2.imshow("im", letter)

            key = cv2.waitKey(0)
            if key == 27:
                sys.exit(0)
            elif key == 32:
                continue
            elif 256 > key > 32:
                answers.append(key)
                save_letter(letter, key, index, i)
        if len(answers) == 5:
            cache[index] = answers
            with open('cache.txt', 'w+') as f:
                f.write(json.dumps(cache))

for i in xrange(0,1000):
    train('images/%s.jpg' % i, str(i))