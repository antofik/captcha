import sys
from filter_image import parse_image, recognize, convert
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


if True:
    for i in xrange(500,600):
        orig, result = recognize('images/%s.jpg' % i)
        value = convert(result)
        cv2.imshow("orig", orig)
        print value
        key = cv2.waitKey(0)
        if key==27:
            sys.exit(0)
