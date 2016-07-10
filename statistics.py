import os
import json
from guess import recognize


try:
    with open('cache.txt', 'r') as f:
        cache = json.loads(f.read()) or {}
except Exception,e:
    cache = {}


def check(image, index):
    global cache

    orig, result = recognize(image)
    if len(result) != 5:
        return

    if not (index in cache):
        return

    answers = cache[index]

    for i in xrange(len(result)):
        if result[i] != answers[i]:
            return False
    return True


for i in xrange(0,100):
    ok = check('images/%s.jpg' % i, str(i))
    print "#%s - %s" % (i, "OK" if ok else "FAIL")
