# encoding=utf-8

import __builtin__
import os
import cv2
from cv2 import *
import sys
from library import *
import numpy as np
from library import height
from library import width

#######   training part    ###############
samples = np.loadtxt('generalsamples.data',np.float32)
responses = np.loadtxt('generalresponses.data',np.float32)
responses = responses.reshape((responses.size,1))

model = cv2.KNearest()
model.train(samples,responses)


def wait():
    key = cv2.waitKey(0)
    if key == 27:
        sys.exit(0)


def remove_small_bounds(im, size=0):
    contours, _ = cv2.findContours(im.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) < 10]
    for i in xrange(len(contours)):
        if cv2.contourArea(contours[i]) > size:
            continue
        black = (100,0,0)
        cv2.drawContours(im, contours, i, black, 3)
    return im


def split_to_images(filename):
    im = imread(filename.encode('utf8'))
    if im is None:
        return None, None
    t = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    images = []
    for i in xrange(5):
        width = 40
        height = 60
        x = i*width
        images.append(t[0:height, x:x+width])
    return images, im

def parse_image(filename):
    images, orig = split_to_images(filename)
    if not images:
        return None, None
    letters = [filter_image(im) for im in images]
    #imshow("origin", orig)
    #for i in letters:
    #    imshow("xxx", i)
    #    cv2.waitKey(0)
    return orig, letters if len(letters) == 5 else None

def filter_image(im):
    t = - im
    t = cv2.GaussianBlur(t, (3, 3), 0)
    _, t = cv2.threshold(t, 140, 255, cv2.THRESH_BINARY)

    mask = GaussianBlur(t, (3,3), 0)
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours)==0:
        return None

    contour = sorted(contours, key=lambda x : -cv2.contourArea(x))[0]
    t5 = cv2.cvtColor(t, cv2.COLOR_GRAY2BGR)
    rect = cv2.minAreaRect(contour)
    (x,y), (w,h), angle = rect
    x,y,w,h,angle = (int(i) for i in [x,y,w,h,angle])
    if angle < -45:
        angle += 90
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(t5,[box],0,(0,255,0),1)

    M = cv2.getRotationMatrix2D((x,y), angle, 1)
    t2 = cv2.warpAffine(t, M, (40,60))
    if w > h: w,h=h,w
    t6 = cv2.getRectSubPix(t2, (int(w),int(h)), (x, y))
    #imshow("t", t)
    #imshow("t2", t2)
    #imshow("t5", t5)
    #imshow("t6", t6)
    return t6

def recognize(image):
    orig, letters = parse_image(image)
    result = []
    for i in xrange(len(letters)):
        roi = letters[i]
        w,h = roi.shape
        if w < 10 or h < 10:
            return orig, []
        roi = cv2.resize(roi, (width, height))
        roi = roi.reshape((1, width * height))
        roi = np.float32(roi)
        retval, results, neigh_resp, dists = model.find_nearest(roi, k=5)
        result.append(int(results[0][0]))
    return orig, result


def convert(result):
    return ''.join([get_key(keys[i]) for i in result])

def convert_back(result):
    for ch in result:
        if not ch in keys_rus:
            return result
    return ''.join([keys[keys_rus.index(ch)] for ch in result])


if False:
    for (dirpath, dirnames, filenames) in os.walk(u'recognized'):
        for filename in filenames:
            path = u'recognized/%s' % (filename)
            path = os.path.abspath(path)
            orig, letters = parse_image(path)
            result = []
            imshow("original", orig)
            for i in xrange(len(letters)):
                roi = letters[i]
                imshow("letter", roi)
                w,h = roi.shape
                roi = cv2.resize(roi, (width, height))
                imshow("letter2", roi)
                print w,h
                wait()

                roi = roi.reshape((1, width * height))
                roi = np.float32(roi)
                retval, results, neigh_resp, dists = model.find_nearest(roi, k=5)
                result.append(int(results[0][0]))

            print convert(result)
