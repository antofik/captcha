from filter_image import recognize, parse_image
from library import *
import numpy as np
import os

samples = np.empty((0, width*height))
responses = []

for (dirpath, dirnames, filenames) in os.walk(u'recognized'):
    for filename in filenames:
        print filename
        result = filename[:-4]
        path = os.path.abspath(u'recognized/%s' % (filename))
        orig, letters = parse_image(path)
        if letters is None:
            print "Failed to parse %s" % filename
            continue
        for i in xrange(5):
            roi = letters[i]
            ch = result[i]
            #roi = cv2.imread(path)
            roi = cv2.resize(roi, (width, height))
            #roi,g,b = cv2.split(roi)
            roi = roi.reshape((1, width * height))
            samples = np.append(samples, roi, 0)
            responses.append(keys.index(ch))


responses = np.array(responses, np.float32)
responses = responses.reshape((responses.size, 1))

np.savetxt('generalsamples.data', samples)
np.savetxt('generalresponses.data', responses)
