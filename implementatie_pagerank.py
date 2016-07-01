vimport random
import numpy as np
from scipy.sparse import coo_matrix

def normalize(v):
    norm=np.linalg.norm(v)
    if norm==0: 
       return v
    return v/norm

f = open('LinksUU', 'r')
links = f.read()
f.close()

links = links[1:-1].split(", ")
#print(links)

def linksmaker(link):
    f = open(str(links.index(link)), 'r')
    links_link = f.read()
    f.close()
    return links_link

kolommen = []

rijen = []
   

def vuller(links):
    for i in links:
        kolommen.append(links.index(i))
        rijen.append(links.index(i))
    for i in links:
        for j in links:
            if j in linksmaker(i) and links.index(j) > links.index(i):
                kolommen.append(links.index(i))
                rijen.append(links.index(j))
                kolommen.append(links.index(j))
                rijen.append(links.index(i))
            elif j in linksmaker(i) and links.index(j) < links.index(i):
                if (i in linksmaker(j)) == False:
                    kolommen.append(links.index(i))
                    rijen.append(links.index(j))
                    kolommen.append(links.index(j))
                    rijen.append(links.index(i))

vuller(links)
#print(kolommen)
#print(rijen)

Enen = len(kolommen)*[1]
n = len(links)
vector = n*[1]
bogenmatrix = coo_matrix((Enen, (kolommen, rijen)), shape=(n,n)).toarray()
print(np.linalg.det(bogenmatrix))
print(np.linalg.norm(bogenmatrix))
norm_bogenmatrix = normalize(bogenmatrix)
print(np.linalg.det(norm_bogenmatrix))
print(np.linalg.norm(norm_bogenmatrix))
macht_bogenmatrix = np.linalg.matrix_power(norm_bogenmatrix, 100)
verhouding = macht_bogenmatrix.dot(vector)
uitkomst = verhouding

#print(macht_bogenmatrix)
print(macht_bogenmatrix)
print(verhouding)

text = open('Pagerank', 'w')
text.write(str(uitkomst))
