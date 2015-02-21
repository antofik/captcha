from library import *
import numpy as np
import os

samples = np.empty((0, width*height))
responses = []

for key in keys:
    print chr(key)
    for (dirpath, dirnames, filenames) in os.walk('letters/%s/' % chr(key)):
        for filename in filenames:
            if filename.endswith(".png"):
                roi = cv2.imread('letters/%s/%s' % (chr(key), filename))
                roi,g,b = cv2.split(roi)
                roi = roi.reshape((1, width * height))
                samples = np.append(samples, roi, 0)
                responses.append(key)


responses = np.array(responses, np.float32)
responses = responses.reshape((responses.size, 1))

np.savetxt('generalsamples.data', samples)
np.savetxt('generalresponses.data', responses)
