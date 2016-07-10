# encoding=utf8
import cv2
import numpy as np
import operator

width = 20
height = 24
keys_rus = [u'а', u'б', u'в', u'г', u'д', u'е', u'ж', u'и', u'к', u'м', u'н', u'п', u'р', u'с', u'т', u'у', u'э', u'ю', u'я', u'2', u'4', u'5', u'6', u'7', u'8', u'9']
keys = [u'a', u'b', u'v', u'g', u'd', u'e', u'z', u'i', u'k', u'm', u'n', u'p', u'r', u's', u't', u'u', u'q', u'w', u'y', u'2', u'4', u'5', u'6', u'7', u'8', u'9']

def get_key(en_key):
    return keys_rus[keys.index(en_key)]

cHigh = [ord(c) for c in ['q', 't', 'y', 'p', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'b']] # 20x28
cWide = [ord(c) for c in ['w', 'm']] # 26x22
cOthers = [c for c in keys if not (c in cHigh) and not (c in cWide)] # 20x22

categories = ['high', 'wide', 'normal']
sizes = {
    'high': (20, 28),
    'wide': (26, 22),
    'normal': (20, 22)
}


def filter2(file):
    im = cv2.imread(file)
    b, g, r = cv2.split(im)
    _, t = cv2.threshold(b, 140, 255, cv2.THRESH_BINARY)  #r-g, b-g
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    #_, t = cv2.threshold(t, 80, 255, cv2.THRESH_BINARY)
    t = cv2.GaussianBlur(t, (7, 7), 0)
    _, t = cv2.threshold(t, 230, 255, cv2.THRESH_BINARY)
    return b, t


def filter(file):
    im = cv2.imread(file)
    t = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    t = cv2.GaussianBlur(t, (5, 5), 0)
    t = cv2.adaptiveThreshold(t, 255, 1, 1, 11, 2)
    return im, t


def filter3(filename):
    def remove_small_bounds(im, size=0):
        contours, _ = cv2.findContours(im.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #[cv2.boundingRect(c) for c in contours if cv2.contourArea(c) < 10]
        for i in xrange(len(contours)):
            if cv2.contourArea(contours[i]) > size:
                continue
            black = (0,0,0)
            cv2.drawContours(im, contours, i, black, 3)
        return im

    im = cv2.imread(filename)

    t = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    t = -t
    _, t = cv2.threshold(t, 45, 255, cv2.THRESH_BINARY)

    tx = remove_small_bounds(t.copy())

    k_vertical = np.array([[0,1,0],[0,0,0],[0,1,0]], np.uint8)
    k_horizontal = np.array([[0,0,0],[1,0,1],[0,0,0]], np.uint8)

    r,g,b = cv2.split(im)
    t2 = cv2.bitwise_xor(b,g)

    def transform(im):
        _, t2 = cv2.threshold(im, 50, 255, cv2.THRESH_BINARY)
        t21 = cv2.morphologyEx(t2, cv2.MORPH_OPEN, k_vertical, iterations=1)
        t22 = cv2.morphologyEx(t2, cv2.MORPH_OPEN, k_horizontal, iterations=1)
        return cv2.bitwise_or(t21,t22)
    t2 = transform(tx)

    t2 = cv2.GaussianBlur(t2, (7, 7), 0)
    _, t2 = cv2.threshold(t2, 30, 255, cv2.THRESH_BINARY)
    t2 = cv2.bitwise_and(t2, tx)

    mask = remove_small_bounds(t2.copy(), 5)
    mask = cv2.GaussianBlur(mask, (7,7), 0)
    _,t3 = cv2.threshold(mask, 10, 255, 0)
    t3 = cv2.bitwise_and(t3, t2)

    return im, t3



filter_image = filter3


def find_letters(im):
    contours, _ = cv2.findContours(im, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 50]  # and cv2.contourArea(c) < 300]
    bounds = [b for b in contours if b[3] > 15]

    ############### sort bounds by X coordinate
    bounds.sort()
#    print bounds

    ############### remove embedded bounds
    remove = []
    for i in xrange(1, len(bounds)):
        x, y, w, h = bounds[i]
        if x + w < bounds[i - 1][0] + bounds[i - 1][2]:
            remove.append(i)
    remove.reverse()
    for i in remove:
#        print 'remove embedded bound'
        bounds.remove(bounds[i])

    ############## merge extra small bounds into bigger ones
    small = []
    for i in xrange(len(bounds)):
        x, y, w, h = bounds[i]
        if w * h < 230:
#            print 'bound %s should me merged' % i
            small.append(i)
    small.reverse()
    for i in small:
        prev = bounds[i - 1] if i > 0 else (0, 0, 0, 0)
        next = bounds[i + 1] if i < len(bounds) - 1 else (0, 0, 0, 0)
        x0, y0, w0, h0 = bounds[i]
        if prev[2] > 0 and prev[2] * prev[3] < next[2] * next[3]:
            ## merge into prev
#            print '  ..merge into prev'
            x, y, w, h = prev
            bounds[i - 1] = (x, min(y, y0), x0 + w0 - x, max(h, h0))
        elif next[2] > 0:
            ## merge into next
#            print '  ..merge into next'
            x, y, w, h = next
            bounds[i + 1] = (x0, min(y, y0), x + w - x0, max(h, h0))
        bounds.remove(bounds[i])

    if len(bounds) == 0:
        return []

    ############## fill gaps
    add = []
    prev = bounds[0]
    for i in xrange(1, len(bounds)):
        this = bounds[i]
        gap = this[0] - prev[0] - prev[2]  #this.x - (prev.x + prev.w)
        if gap > 10:
#            print 'filling gap', gap,
            add.append((prev[0] + prev[2], min(prev[1], this[1]), gap, max(prev[3], this[3])))
        prev = this
    for bound in add:
        bounds.append(bound)
    bounds.sort()

    while len(bounds) > 5:
#        print "too many bounds, we should merge some of them"
        ### get two bounds, which merged together will give smallest square, and merge them
        h = [(i, bounds[i][2] * bounds[i][3] + bounds[i + 1][2] * bounds[i + 1][3]) for i in xrange(len(bounds) - 1)]
        i, _ = min(h, key=operator.itemgetter(1))
        ### merge i and i+1 bounds
        x1, y1, w1, h1 = bounds[i]
        x2, y2, w2, h2 = bounds[i + 1]
        bounds.remove(bounds[i + 1])
        bounds[i] = (x1, min(y1, y2), x2 + w2 - x1, max(h1, h2))

    if len(bounds) == 0:
        return bounds

    ############ split maximal bound on two
    while len(bounds) < 5:
        m = max(bounds, key=operator.itemgetter(2))
        bounds.remove(m)
        x, y, w, h = m
#        print 'split gap'
        bounds.append((x, y, w / 2, h))
        bounds.append((x + w / 2, y, w / 2, h))

    bounds.sort()

    return bounds


def get_roi(im, bounds):
    rois = []
    for x, y, w, h in bounds:
        rois.append(cv2.resize(im[y:y + h, x:x + w], (width, height)).reshape((1, width * height)))
    return rois


def display_bounds(im, bounds):
    for x, y, w, h in bounds:
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 1)
    cv2.imshow("bounds", im)