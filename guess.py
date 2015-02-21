import sys
import numpy as np
from library import *
import cv2
import json

#######   training part    ###############
samples = np.loadtxt('generalsamples.data',np.float32)
responses = np.loadtxt('generalresponses.data',np.float32)
responses = responses.reshape((responses.size,1))

model = cv2.KNearest()
model.train(samples,responses)

try:
    with open('cache.txt', 'r') as f:
        cache = json.loads(f.read()) or {}
except Exception,e:
    cache = {}

############################# testing part  #########################

def recognize(image):
    im, t = filter_image(image)
    b = find_letters(t.copy())
    out = np.zeros(im.shape,np.uint8)
    rois = get_roi(t, b)
    print b
    display_bounds(im.copy(), b)

    x = 10
    for roi in rois:
        roi = np.float32(roi)
        retval, results, neigh_resp, dists = model.find_nearest(roi, k=5)
        value = str(chr(int(results[0][0])))
        cv2.putText(out,value,(x,30),0,1,(0,255,0))
        x += 20

    cv2.imshow('im',im)
    cv2.imshow('out',out)
    key = cv2.waitKey(0)
    if key==27:
        sys.exit(0)


for i in xrange(410,460):
    recognize('images/%s.jpg' % i)
