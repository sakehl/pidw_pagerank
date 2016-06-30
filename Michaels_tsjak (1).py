#Zet de sourcecode om in een string
d = str(urllib.request.urlopen(webpage).read())
#Neem deel van de sourcecode dat alles vanaf de omschrijving en de titel hebben.
deel_omschrijving = d.partition('<meta name="description" content="')[2]
deel_titel = d.partition('"og:title" content="')[2]
#Neem alleen de omschrijving en de titel
omschrijving = deel_omschrijving.partition('"')[0]
titel = deel_titel.partition('"')[0]
print(omschrijving, titel)

def zoek(woord,dictonary):
    match = []
    for item in dictonary:
        overeenkomst = item.find(woord)
        if overeenkomst != -1:
            match.append(1)
        else:
            match.append(0)
    return match
            
def resultaat(pr_lijst,match_lijst):
    uitkomst = [1]*len(pr_lijst)
    for i in range(len(uitkomst)):
        uitkomst[i] = (pr_lijst[i]*match_lijst[i],i)
    uitkomst.sort()
    
