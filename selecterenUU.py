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
    
def resultaat(pr_lijst,match_lijst):
    uitkomst = [1]*len(pr_lijst)
    for i in range(len(uitkomst)):
        uitkomst[i] = (pr_lijst[i]*match_lijst[i],i)
    uitkomst.sort()

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
            
temp = zoek('informatica', metadict)
for item in temp:
   # print(temp[temp.index(item)])
    temp2 = []
    for item2 in pagedict[item][0]:
        if item2 in temp:
            temp2.append(item2)
    #print(item + " " + str(temp2))

#f = open('LinksUU', 'r')
#links = f.read()
#f.close()
#links = links[1:-1].split(", ")
#print(links)

links = zoek('informatica', metadict)

def linksmaker(link, links):
    links_link = []
    for item in pagedict[link][0]:
        if item in links:
            links_link.append(item)
    return links_link

#print(linksmaker(links[0], links))
#print(links[0])

kolommen = []

rijen = []
   

def vuller(links):
    for i in links:
        kolommen.append(links.index(i))
        rijen.append(links.index(i))
    for i in links:
        for j in links:
            if j in linksmaker(i, links) and links.index(j) > links.index(i):
                kolommen.append(links.index(i))
                rijen.append(links.index(j))
                kolommen.append(links.index(j))
                rijen.append(links.index(i))
            elif j in linksmaker(i, links) and links.index(j) < links.index(i):
                if (i in linksmaker(j, links)) == False:
                    kolommen.append(links.index(i))
                    rijen.append(links.index(j))
                    kolommen.append(links.index(j))
                    rijen.append(links.index(i))

vuller(links)
print(kolommen)
print(rijen)

Enen = len(kolommen)*[1]
n = len(links)
vector = n*[1]
bogenmatrix = coo_matrix((Enen, (kolommen, rijen)), shape=(n,n)).toarray()
#print(np.linalg.det(bogenmatrix))
#print(np.linalg.norm(bogenmatrix))
norm_bogenmatrix = normalize(bogenmatrix)
#print(np.linalg.det(norm_bogenmatrix))
#print(np.linalg.norm(norm_bogenmatrix))
macht_bogenmatrix = np.linalg.matrix_power(norm_bogenmatrix, 100)
verhouding = macht_bogenmatrix.dot(vector)
uitkomst = normalize(verhouding)

#print(bogenmatrix)
#print(macht_bogenmatrix)
#print(uitkomst)

text = open('Pagerank', 'w')
text.write(str(uitkomst))

print(resultaat(links, uitkomst))
