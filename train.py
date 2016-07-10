from library import *
import numpy as np
import os

samples = np.empty((0, width*height))
responses = []

for i in xrange(len(keys)):
    key = keys[i]
    print key
    for (dirpath, dirnames, filenames) in os.walk(u'letters/%s/' % key):
        for filename in filenames:
            if filename.endswith(".png"):
                path = os.path.abspath(u'letters/%s/%s' % (key, filename))
                #path = u'letters/%s/%s' % (key, filename)
                roi = cv2.imread(path)
                roi = cv2.resize(roi, (width, height))
                roi,g,b = cv2.split(roi)
                roi = roi.reshape((1, width * height))
                samples = np.append(samples, roi, 0)
                responses.append(i)


responses = np.array(responses, np.float32)
responses = responses.reshape((responses.size, 1))

np.savetxt('generalsamples.data', samples)
np.savetxt('generalresponses.data', responses)
