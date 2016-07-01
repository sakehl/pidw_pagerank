#!/usr/bin/python3

# Author: Lars van den Haak, Michael van den Hoogenband en Nijs van Tuijl
# Gebasseerd op versie van Jan-Willem Buurlage <janwillembuurlage@gmail.com>
#
# Dit script crawlt de uu pagina en zijn subpagina's. Ook slaat deze alles op.
# Hiermee kun je een zoekmachine implementeren

import urllib.request
from html.parser import HTMLParser
import queue
from collections import defaultdict

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

def pagecrawler(base, name, queue, crawled, wholequeue):
    # zoek in het www.uu.nl domein
    webpage = base + name
    #De basis url, eigenlijk de map waar we zitten. Nodig voor relatieve urls
    #De standaard is dat het niet op een '/' eindigd en ook niet op .htm(l)
    if(webpage.endswith(".html" or ".htm") ):
        basepage = (webpage.split(base)[-1]).split("/")[:-1]
    elif(webpage.endswith("/")):
        basepage = (webpage.split(base)[-1]).split("/")[:-1]
    else:
        basepage = (webpage.split(base)[-1]).split("/")
    
    # maak een object aan die links kan herkennen
    parser = URLParser()
    
    # download de webpagina, en stop de inhoud in een string
    try:
        page_content= urllib.request.urlopen(webpage).read()
    except:
        print("Ging iets mis met "+webpage)
        with open("data/exceptions","a") as f:
            f.write(name+"\n")
        return None
    
    #We kijken of deze link al is gezien is, wellicht onder een andere naam
    #Bij we webpagina staat vaak de canonlink en shortlink, die zeggen op welke link de pagina te vinden is
    try:
        canonlink = str(page_content).split('<link rel="canonical" href="')[-1].split('"')[0]
        shortlink = str(page_content).split('<link rel="shortlink" href="')[-1].split('"')[0]   
        canonlink = canonlink.split(base)[1]
        shortlink = shortlink.split(base)[1]
        if(canonlink in crawled or shortlink in crawled):
            print(name + "is a duplicate")
            with open("data/exceptions","a") as f:
                f.write(name+"\n")
        
        
        #We willen als we crawlen meteen even de titel en omschrijving bekijken, zodat we hier sneller op kunnen zoeken.
        #Deze zijn vaak geoptimallisseerd voor search engines 
        deel_omschrijving = str(page_content).partition('<meta name="description" content="')[2]
        deel_titel = str(page_content).partition('"og:title" content="')[2]
        #Neem alleen de omschrijving en de titel en mogen geen komma's in, anders gaat fout met opslaan
        omschrijving = deel_omschrijving.partition('"')[0]
        omschrijving = omschrijving.replace(',',' ')
        titel = deel_titel.partition('"')[0]
        titel = titel.replace(',',' ')
    except:
        print(name + "gaf een error, is moeilijker om op te zoeken. We slaan alleen de link op als op te zoeken")
        titel = ""
        omschrijving = ""

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
        #De base moet beginnen met http://www. we gaan dan 4 combinaties af met of zonder www of http://
        #base[11:] = uu.nl
        if(temp.startswith(base) or temp.startswith(base[11:])
           or temp.startswith(base[7:]) or temp.startswith(base[:7]+base[11:]) ):
            #We willen alleen het gedeelte zien na de uu.nl, dus het is een relatieve URL
            temp = temp.split(base[11:])
            urls.append(temp[-1])
        
        #Hier krijgen we alle relatieve urls mee te pakken
        elif(not (temp.startswith("http://") or temp.startswith("https://")) ):
            #We willen geen // urls, die linken naar andere webpagina's
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
    #We willen nu nog duplicaten eruit halen en op ongeldige links filteren
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
        if(temp.find("mailto:") != -1):
            continue
        if(temp.find("javascript:") != -1):
            continue
        if(temp.find(".") != -1):
            if(temp.find(".htm") == -1):
                print("Skipping " + temp)
                continue
        if(temp.find("?") != -1):
            print("Skipping " + temp +" because of ?")
            continue
        if(temp.find("%") != -1):
            print("Skipping " + temp +" because of %")
            continue
        finalurls.append(temp)
    #Door het als een set te doen, komt het helemaal goed
    finalurls = set(finalurls)
    
    
    
    crawled[name].append(finalurls)
    #We schrijven onze data weg, eerst komt de site, dan komt de titel met omschrijving en dan alle links
    with open("data/crawldata","a") as f:
        f.write(name + ",")
        f.write(titel + " " + omschrijving + ",")
        for item in finalurls:
            f.write(item+",")
        f.write("\n")
    
    f2 = open("data/wholequeue","a")
    for item in finalurls:
        if(item not in wholequeue):
            q.put(item)
            wholequeue.add(item)
            f2.write(item + "\n")
    f2.close()
    
    with open("data/finishcrawl","a") as f:
        f.write(name +"\n")

    
base = "http://www.uu.nl"

crawled = defaultdict(list)
q = queue.Queue()
wq = set([])

#We lezen alles in wat al is gecrawled is
try:
    with open("data/crawldata","r") as f:
        for line in f:
            #We willen de /n niet mee, die neemt die anders wel mee en we splitten op ','
            temp = line.split(",")[0:-1]
            ##De reden dat we pas vanaf de tweede kijken, is omdat eerst de link zelf komt, dan titel met metadata en dan pas de links
            if(len(temp)>2):
                crawled[temp[0]].append(temp[2:])
            else:
                crawled[temp[0]].append({})
except FileNotFoundError:
    print("We don't have all the files yet, no worries")

#we lezen alles in wat in de queue staat om nog gecrawled te worden, behalve als die al in crawldata stond
try:
    with open("data/wholequeue","r") as f:
        for line in f:
            temp = line.split("\n")[0]
            #voegen hem toe aan de wholequeue
            wq.add(temp)
            #voegen hem alleen toe aan de queue als die er nog niet was
            if(temp not in crawled):
                q.put(temp)
except FileNotFoundError:
    print("Jup, not all files")
    
if(q.empty() and len(crawled)<1):
    q.put("/")
    init = q.get()
    pagecrawler(base, init, q, crawled, wq)
    while(not q.empty()):
        nextitem = q.get()
        print("Crawling " + base + nextitem)
        pagecrawler(base, nextitem, q, crawled, wq)
elif(q.empty()):
    print("Done! Crawled everything")
else:
    while(not q.empty()):
        nextitem = q.get()
        print("Crawling " + base + nextitem)
        pagecrawler(base, nextitem, q, crawled, wq)

print("Done! Crawled everything")