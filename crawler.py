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
webpage = "http://www.uu.nl/"
#De basis url, eigenlijk de map waar we zitten.
#De standaard is dat het niet op een '/' eindigd en ook niet op .htm(l)
if(webpage.endswith(".html" or ".htm") ):
    basepage = (webpage.split("uu.nl")[-1]).split("/")[:-1]
elif(webpage.endswith("/")):
    basepage = (webpage.split("uu.nl")[-1]).split("/")[:-1]
else:
    basepage = (webpage.split("uu.nl")[-1]).split("/")


# maak een object aan die links kan herkennen
parser = URLParser()

# download de webpagina, en stop de inhoud in een string
page_content= urllib.request.urlopen(webpage).read()

# voordat je de parser hergebruikt dien je hem eerst te legen
parser.empty()

# 'parse' de webpagina die we hebben gedownload
parser.feed(str(page_content))

# de gelinkte pagina's zijn opgeslagen in een lijst binnen in het parser object
#print(parser.urls)

urls = []

for item in parser.urls:
    #We halen de links naar op de pagina weg (bijv. uu.nl/index.html#main)    
    temp = item
    temp = temp.split('#')[0]
    
    #De pagina moet op het uu.nl domein zijn, juist niet op students.uu.nl of iets dergelijks
    if(temp.startswith("http://www.uu.nl") or temp.startswith("uu.nl")
       or temp.startswith("http://uu.nl") or temp.startswith("www.uu.nl") ):
        temp = temp[7:]
        #We willen alleen het gedeelte zien na de uu.nl, dus het is een relatieve URL
        temp = temp.split('uu.nl')
        urls.append(temp[-1])
    
    #Hier krijgen we alle relatieve urls mee te pakken
    elif(not (temp.startswith("http://") or temp.startswith("https://")) ):
        #We don't want // urls, they link to other webpages
        if(temp.startswith("//")):
            pass
        #Dit format is geweldig!
        elif(temp.startswith("/")):
            urls.append(temp)
        #Hier maken we relatieve urls correct met veel "../" erin
        elif(temp.startswith("../")):
            i = 0
            while(temp.startswith("../")):
                i -= 1
                temp = temp[3:]
            temp2 = (basepage[:i])
            temp2.append(temp)
            temp = "/".join(temp2)
            urls.append(temp)
        #Hier zorgen we dat urls beginnend met "./" goed komen
        elif(temp.startswith("./") ):
            temp = temp[2:]
            temp = "/".join(basepage) +'/' + temp
            urls.append(temp)
        #Er zijn nu alleen nog maar relatieve urls over, die in dezelfde basis zitten
        else:
            temp = "/".join(basepage) +'/' + temp
            urls.append(temp)

finalurls = []
#We willen nu nog duplicaten eruit halen
for item in urls:
    temp = item
    if(temp.endswith("/")):
        temp = temp[:-1]
    if(temp.endswith("index.html")):
        temp = temp[:-11]
    if(temp.endswith("index.htm")):
        temp = temp[:-10]
    if(temp == ''):
        continue
    print(temp)
    finalurls.append(temp)

#print(finalurls)