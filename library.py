import cv2
import operator

width = 20
height = 24
keys = [i for i in xrange(97, 123)]

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


filter_image = filter


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