import urllib
url = "http://www.rechtsanwaltsregister.org/JPegImage.aspx"
for i in xrange(1000):
    urllib.urlretrieve (url, "images/%s.jpg" % i)
    print i
