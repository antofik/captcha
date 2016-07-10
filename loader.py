import urllib
url = "https://xn--b1ab2a0a.xn--b1aew.xn--p1ai/captcha/"
for i in xrange(1000):
    urllib.urlretrieve (url, "images/%s.jpg" % i)
    print i
