import os
import json

from library import *


try:
    with open('cache.txt', 'r') as f:
        cache = json.loads(f.read()) or {}
except Exception,e:
    cache = {}
if not os.path.exists("letters"):
    os.makedirs("letters")

s = {}

def check(image, index):
    global cache
    global s

    im, t = filter_image(image)
    b = find_letters(t.copy())
    if len(b) != 5:
        return

    if not (index in cache):
        return

    answers = cache[index]
    for i in xrange(len(answers)):
        letter = chr(answers[i])
        if not (letter in s):
            s[letter] = {'width':0, 'height':0, 'count':0}
        x,y,w,h = b[i]
        s[letter]['width'] += w
        s[letter]['height'] += h
        s[letter]['count'] += 1

for i in xrange(0,100):
    check('images/%s.jpg' % i, str(i))

sizes = [(letter, s[letter]['width']/s[letter]['count'], s[letter]['height']/s[letter]['count']) for letter in s]
sizes.sort()

print '\n--- High ---'
for l,w,h in sizes:
    if ord(l) in cHigh:
        print l,w,h

print '\n--- Wide ---'
for l,w,h in sizes:
    if ord(l) in cWide:
        print l,w,h

print '\n--- Others ---'
for l,w,h in sizes:
    if ord(l) in cHigh:
        pass
    elif ord(l) in cWide:
        pass
    else:
        print l,w,h

