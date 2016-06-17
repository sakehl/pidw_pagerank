#!/usr/bin/python3

# Author: Jan-Willem Buurlage <janwillembuurlage@gmail.com>
#
# Dit script maakt een lijst van webpagina's waarnaar gelinkt wordt vanaf een
# gegeven webpagina, de website van de UU.

import urllib.request
from html.parser import HTMLParser


# deze parser objecten zijn in staat om uit een HTML bestand alle
# links te herkennen van het type <a href="{link}">text</a>
class URLParser(HTMLParser):
    urls = []

    def handle_starttag(self, tag, attrs):
        href = [v for k, v in attrs if k == 'href']
        if href and tag == 'a':
            self.urls.extend(href)

    def empty(self):
        self.urls = []

# zoek in het www.uu.nl domein
webpage = "http://www.uu.nl"

# maak een object aan die links kan herkennen
parser = URLParser()

# download de webpagina, en stop de inhoud in een string
page_content= urllib.request.urlopen(webpage).read()

# voordat je de parser hergebruikt dien je hem eerst te legen
parser.empty()

# 'parse' de webpagina die we hebben gedownload
parser.feed(str(page_content))

# de gelinkte pagina's zijn opgeslagen in een lijst binnen in het parser object
print(parser.urls)
