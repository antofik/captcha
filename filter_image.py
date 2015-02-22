import cv2
from cv2 import *
import sys
import numpy as np


def remove_small_bounds(im, size=0):
    contours, _ = cv2.findContours(im.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #[cv2.boundingRect(c) for c in contours if cv2.contourArea(c) < 10]
    for i in xrange(len(contours)):
        if cv2.contourArea(contours[i]) > size:
            continue
        black = (0,0,0)
        cv2.drawContours(im, contours, i, black, 3)
    return im




def filter_image(filename):
    im = imread(filename)

    t = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    t = -t
    _, t = cv2.threshold(t, 45, 255, cv2.THRESH_BINARY)

    tx = remove_small_bounds(t.copy())

    k_crest = np.array([[0,1,0],[1,1,1],[0,1,0]], np.uint8)
    k_diagonal_crest = np.array([[1,0,1],[0,1,0],[1,0,1]], np.uint8)
    k_square = np.array([[1,1,1],[1,0,1],[1,1,1]], np.uint8)
    k_vertical = np.array([[0,1,0],[0,0,0],[0,1,0]], np.uint8)
    k_horizontal = np.array([[0,0,0],[1,0,1],[0,0,0]], np.uint8)
    k_lr = np.array([[0,0,1],[0,0,0],[1,0,0]], np.uint8)

    r,g,b = split(im)
    t2 = bitwise_xor(b,g)

    def transform(im):
        _, t2 = cv2.threshold(im, 50, 255, cv2.THRESH_BINARY)
        t21 = morphologyEx(t2, cv2.MORPH_OPEN, k_vertical, iterations=1)
        t22 = morphologyEx(t2, cv2.MORPH_OPEN, k_horizontal, iterations=1)
        return bitwise_or(t21,t22)
    t2 = transform(tx)

    t2 = cv2.GaussianBlur(t2, (7, 7), 0)

    #t2 = dilate(t2, k_lr)
    _, t2 = cv2.threshold(t2, 30, 255, cv2.THRESH_BINARY)
    t2 = bitwise_and(t2, tx)

    mask = remove_small_bounds(t2.copy(), 5)
    mask = GaussianBlur(mask, (7,7), 0)
    _,t3 = threshold(mask, 10, 255, 0)
    t3 = bitwise_and(t3, t2)


    #t2 = cv2.erode(t, kernel2, iterations=1)
    #t3 = dilate(bitwise_or(cv2.erode(t, kernel3, iterations=1), t2), kernel = np.array([[1,0,1],[0,1,0],[0,0,0]], np.uint8))
    #t3 = erode(t3, k_crest)
    #t3 = dilate(t3, k_diagonal_crest)
    #t2 = cv2.dilate(t2, kernel, iterations=1)

    #imshow("im", im)
    imshow("t", t)
    imshow("t2", t2)
    imshow("t3", t3)
    imshow("tx", tx)
    #imshow("t3", t3)
    if waitKey(0) == 27:
        sys.exit(0)


for i in xrange(159,1000):
    filter_image('images/%s.jpg' % (i))
