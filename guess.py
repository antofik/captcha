import sys
from filter_image import parse_image
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


if False:
    for i in xrange(500,600):
        orig, result = recognize('images/%s.jpg' % i)
        value = convert(result)
        cv2.imshow("orig", orig)
        print value
        key = cv2.waitKey(0)
        if key==27:
            sys.exit(0)
