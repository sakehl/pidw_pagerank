from collections import defaultdict

def zoek(woord,dictonary):
    match = []
    for item in dictonary:
        overeenkomst = item.lower().find(woord.lower())
        if overeenkomst != -1:
            match.append(item)
    return match
            
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
            
while(True):
    print("Zoek wat je wilt en druk op [enter]. [Q]uit als je klaar bent met zoeken.")
    zoekwoord = input()
    if(zoekwoord.lower() in ["q","quit","exit","klaar"]):
        break
    result = zoek(zoekwoord, metadict)
    if(len(result) == 0):
        print("Helaas geen resulten")
    else:
        i = 0
        for item in result:
            print(item)
            i += 1
            if(i%10 == 0):
                print("volgende 10 resultaten? [j]a/[n]ee")
                test = input().lower()
                if(test in ["j", "ja"]):
                    continue
                else:
                    break
    
    