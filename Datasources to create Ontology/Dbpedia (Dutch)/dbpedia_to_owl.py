__author__ = "alexander kellmann"
__license__ = "LGPL-3.0 License"
__date__ = "05/06/2020"

# Description:
#
# This programm reads the file dbpedia_corrected.tsv abd creates two files:
# 1) The file dbpedia_rainbowtable.tsv contains the URI of each drug and it's related ATC code
# 2) The file dbpedia.ttl contains a representation of the data in turtle. 
#    Parts of this program code have been used to encode other data, therefore not all of the code is used.
#    E.g. the namespace n_UMCG is not defined. It has been used to autogenerate URIs for other input.

from rdflib import *
import hashlib
#File öffnen
fo = open("dbpedia_corrected.tsv")
#Zeilenweise einlesen:
with fo as f:
    contents = f.readlines()
fo.close()


g=Graph()
n_dbpedia = Namespace("http://nl.dbpedia.org/resource/")
rdf =Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs=Namespace("http://www.w3.org/2000/01/rdf-schema#")
#owl=Namespace("http://www.w3.org/2000/01/rdf-schema#")


def exportToGraphLiteral(s, p, o):
    subj= URIRef(n_UMCG+str(s))
    pred= URIRef(n_UMCG+str(p))
    obj = Literal(str(o))
    g.add( (subj, pred, obj) )
    return
  
def exportToGraph(s, p, o):
    subj= URIRef(n_UMCG+str(s))
    pred= URIRef(p)
    obj = URIRef(o)
    g.add( (subj, pred, obj) )
    return

def exportToGraphDirekt(s, p, o):
    subj= URIRef(s)
    pred= URIRef(p)
    obj = URIRef(o)
    g.add( (subj, pred, obj) )
    return

def exportToGraphLiteralDirekt(s, p, o):
    subj= URIRef(str(s))
    pred= URIRef(str(p))
    if (len(str(o)) and str(o)!="\n"):
        obj = Literal(str(o))
        g.add( (subj, pred, obj) )
    return
    
def createMD5Hash(substance):
    valueToHash = (substance).lower() 
    return hashlib.md5(valueToHash).hexdigest()

#print("Die erste Zeile ist:\n"+contents[1])
#Aufsplitten in Spalten
for i in range(len(contents)):
    contents[i] = contents[i].split("\t")

#Aufsplitten der einzelnen Spalten in Listen bzw Listen von Listen
resource = []
substance = []
atccode = []
URI = []
label = [] # never used
list = []

for i in range(1,len(contents)):
    resource.append(contents[i][0].strip('\"'))
    substance.append(contents[i][1].strip('\"'))
    atccode.append(contents[i][2].strip('\"'))
    URI.append((contents[i][3]).strip('\"'))
    label.append(contents[i][4].strip('\"').strip("\n")) # never used

for entry in xrange(1,len(contents)-1):
    list.append([resource[entry], atccode[entry]])
    exportToGraphLiteralDirekt(resource[entry], rdfs+"label", substance[entry])# <http://www.UMCG.nl/0015ddfaedc0e2b1794de183a954a110> rdfs:label "Carmustine" .
    exportToGraphDirekt(resource[entry], rdfs+"subClassOf",  URI[entry]) # # <http://www.UMCG.nl/0015ddfaedc0e2b1794de183a954a110> rdfs:subclassof <http://purl.bioontology.org/ontology/UATC/L01AD01> .        

with open('./dbpedia_rainbowtable.tsv', 'w') as outfile:
    for element in list:
        outfile.write(element[0]+ "\t" + element[1] + "\n")

with open('./dbpedia.ttl', 'w') as outfile:
    outfile.write(g.serialize(format='turtle'))
