#!/usr/bin/python3

# Author: Jan-Willem Buurlage <janwillembuurlage@gmail.com>
#
# Dit script maakt een lijst van webpagina's waarnaar gelinkt wordt vanaf een
# gegeven webpagina, de website van de UU.

import urllib.request
from html.parser import HTMLParser
import os.path
import queue
#from multiprocessing import Queue
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
    try:
        page_content= urllib.request.urlopen(webpage).read()
    except:
        print("Ging iets mis met "+webpage)
        with open("exceptions","a") as f:
            f.write(name+"\n")
        return None

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
        if(temp.find(".") != -1):
            if(temp.find(".htm") == -1):
                print("Skipping " + temp)
                continue
        if(temp.find("?") != -1):
            print("Skipping " + temp +" because of ?")
            continue
        if(temp.find("#") != -1):
            print("Skipping " + temp +" because of #")
            continue
        if(temp.find("%") != -1):
            print("Skipping " + temp +" because of %")
            continue
        finalurls.append(temp)
    #Door het als een set te doen, komt het helemaal goed
    finalurls = set(finalurls)
    
    
    
    crawled[name].append(finalurls)
    with open("crawldata","a") as f:
        f.write(name+",")
        for item in finalurls:
            f.write(item+",")
        f.write("\n")
    
    f2 = open("wholequeue","a")
    for item in finalurls:
        if(item not in wholequeue):
            q.put(item)
            wholequeue.add(item)
            f2.write(item + "\n")
    f2.close()
    
    with open("finishcrawl","a") as f:
        f.write(name +"\n")
    
    # dataout = "data/"+ name.replace("/",">")+".txt"
    
    # if(not os.path.isfile(dataout)):
    #     with open(dataout, 'w') as f:
    #         for item in finalurls:
    #             print(item, file=f)
    
    # for item in finalurls:
    #     datatest = "data/"+ item.replace("/",">")+".txt"
    #     if(not os.path.isfile(datatest)):
    #         print("Crawling " + base + item)
    #         pagecrawler(base, item)
    
    
base = "http://www.uu.nl"

crawled = defaultdict(list)
q = queue.Queue()
wq = set([])

#We lezen alles in wat al is gecrawled is
try:
    with open("crawldata","r") as f:
        for line in f:
            #We willen de /n niet mee, die neemt die anders wel mee en we splitten op ','
            temp = line.split(",")[0:-1]
            if(len(temp)>1):
                crawled[temp[0]].append(temp[1:])
            else:
                crawled[temp[0]].append({})
except FileNotFoundError:
    print("We don't have all the files yet, no worries")

#we lezen alles in wat in de queue staat om nog gecrawled te worden, behalve als die al in crawldata stond
try:
    with open("wholequeue","r") as f:
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
# while(not q.empty() ):
#     print(q.get())
# print("-----")
# for item in crawled:
#     print(crawled[item])

#with open("queue","w") as f:
#    f.write(str(q))


# print("Done")