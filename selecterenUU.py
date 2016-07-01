import random
import numpy as np
from scipy.sparse import coo_matrix
from collections import defaultdict

def zoek(woord,dictonary):
    match = []
    for item in dictonary:
        overeenkomst = item.lower().find(woord.lower())
        if overeenkomst != -1:
            match.append(item)
    return match

def normalize(v):
    norm=np.linalg.norm(v)
    if norm==0: 
       return v
    return v/norm
    
def resultaat(links,uitkomst):
    pr_lijst = [1]*len(uitkomst)
    for i in range(len(links)):
        pr_lijst[i] = (uitkomst[i],links[i])
    pr_lijst.sort(reverse = True)
    bestelinks = []
    for a,b in pr_lijst:
        bestelinks.append(b)
    return bestelinks

def linksmaker(link, links):
    links_link = []
    for item in pagedict[link][0]:
        if item in links:
            links_link.append(item)
    return links_link

def vuller(links, kolommen, rijen):
    maxl = 400
    if(len(links) > maxl):
        links.sort(key = len)
        links = links[0:maxl]
    for i in links:
        indi = links.index(i)
        linki = linksmaker(i, links)
        kolommen.append(indi)
        rijen.append(indi)
        for j in links:
            indj = links.index(j)
            if j in linki:
                if indj > indi:
                    kolommen.append(indi)
                    rijen.append(indj)
                    kolommen.append(indj)
                    rijen.append(indi)
                elif indj < indi:
                    if (i in linksmaker(j, links)) == False:
                        kolommen.append(indi)
                        rijen.append(indj)
                        kolommen.append(indj)
                        rijen.append(indi)
    return links

def pageranker(links):
    kolommen = []
    rijen = []
    links = vuller(links, kolommen, rijen)
    Enen = len(kolommen)*[1]
    n = len(links)
    vector = n*[1]
    bogenmatrix = coo_matrix((Enen, (kolommen, rijen)), shape=(n,n)).toarray()
    norm_bogenmatrix = normalize(bogenmatrix)
    macht_bogenmatrix = np.linalg.matrix_power(norm_bogenmatrix, 50)
    verhouding = macht_bogenmatrix.dot(vector)
    uitkomst = normalize(verhouding)
    
    return resultaat(links,uitkomst)

metadict = defaultdict(list)
pagedict = defaultdict(list)
with open("data/crawldata","r") as f:
    for line in f:
        #We willen de /n niet mee, die neemt die anders wel mee en we splitten op ','
        temp = line.split(",")[0:-1]
        ##De reden dat we pas vanaf de tweede kijken, is omdat eerst de link zelf komt, dan titel met metadata en dan pas de links
        metadict[temp[0]].append(temp[1])
        if(len(temp)>2):
            pagedict[temp[0]].append(temp[2:])
        else:
            pagedict[temp[0]].append({})
            
print("Welkom bij de SAZUUP (Super Awesome Zoekmachine van de UU Pagina)." )
while(True):
    print("Zoek wat je wilt en druk op [enter]. [Q]uit als je klaar bent met zoeken.")
    zoekwoord = input()
    if(zoekwoord.lower() in ["q","quit","exit","klaar"]):
        break
    links = zoek(zoekwoord, metadict)
    if(len(links) == 0):
        print("Helaas geen resultaten gevonden. :(")
    else:
        print("We hebben " + str(len(links)) + " resultaten gevonden.")
        if(len(links) > 400):
            print("We geven alleen de eerste 400 resultaten weer.")
        result = pageranker(links)
        i = 0
        for item in result:
            print(metadict[item][0])
            print("\t" + "http://www.uu.nl" + item)
            i += 1
            if(i%10 == 0):
                print("volgende 10 resultaten? [j]a/[n]ee")
                test = input().lower()
                if(test in ["j", "ja"]):
                    continue
                else:
                    break