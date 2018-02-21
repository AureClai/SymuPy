"""


Script by Aurelien Clairais - 21/02/2018
"""
from lxml import etree
import pandas as pd

# Load the XML
filename = 'Init_070000_120000_traf.xml';
tree = etree.parse(filename);

# Initialisation des variables
ID = [];
ABS = [];
ORD = [];
TRON = [];
DST = [];
VIT = [];
T = [];

# Navigation dans le xml à la recherche des instansts et boucle sur les instants
for instant in tree.xpath("/OUT/SIMULATION/INSTANTS/INST"):
    #on boucle sur les trajectoires
    for point in instant.xpath("TRAJS/TRAJ"):
        ID.append(int(point.get("id")));
        T.append(float(instant.get("val")));
        ABS.append(float(point.get("abs")));
        ORD.append(float(point.get("ord")));
        TRON.append(point.get("tron"));
        VIT.append(float(point.get("vit")));
        DST.append(float(point.get("dst")));

# Création DataFrame
df = pd.DataFrame(
        {"id" : ID,
         "t": T,
         "X" : ABS,
         "Y" : ORD,
         "vit" : VIT,
         "dst" : DST,
         "tron" : TRON})

# Rearrange
df = df[["id", "t", "X", "Y", "vit","tron", "dst"]];
    
# Création du CSV
df.to_csv("out.csv", sep='\t');
