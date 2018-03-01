# -*- coding: utf-8 -*-
"""
datatools.py
regrouping the tools for the symuvia outputs.
Presented tools :
    - toDataSet : make a pandas dataset from Symuvia output XML
    - toCSV : make a CSV from a Symuvia output XML
    - ProbeData Generation
    - LoopData Generation
TODO:
-------------------------------------------------------------------------------
Usage :
    import tools
    And use the fonctions wanted

Created on Wed Feb 21 17:19:31 2018

@author: clairais
"""
from lxml import etree
import pandas as pd
import numpy as np
import random

# Make a data set from an XML file


def toDataSet(inputFile):
    """"
    Import the raw data from a XML Symuvia output file
    Input:
        The path to the XML file (string)
    Output:
        The dataFrame (pandas' dataFrame)
    """
    # Load the xml
    tree = etree.parse(inputFile)

    # Initialisation of the variables
    ID = []
    ABS = []
    ORD = []
    TRON = []
    DST = []
    VIT = []
    T = []

    # Navigation in xml to find the "INST" and loop through all
    for instant in tree.xpath("/OUT/SIMULATION/INSTANTS/INST"):
        # loop through all trajectories
        for point in instant.xpath("TRAJS/TRAJ"):
            ID.append(int(point.get("id")))
            T.append(float(instant.get("val")))
            ABS.append(float(point.get("abs")))
            ORD.append(float(point.get("ord")))
            TRON.append(point.get("tron"))
            VIT.append(float(point.get("vit")))
            DST.append(float(point.get("dst")))

    # Creation DataFrame
    df = pd.DataFrame(
        {"id": ID,
         "t": T,
         "X": ABS,
         "Y": ORD,
         "vit": VIT,
         "dst": DST,
         "tron": TRON})

    # Rearrange
    df = df[["id", "t", "X", "Y", "vit", "tron", "dst"]]

    return df

# Make a csv from an xml file


def toCSV(inputFile, outputFile='out.csv', separator='\t'):
    """
    Import a Symuvia raw data XML and export the dataset as a .csv file
    Inputs:
        Path to the XML (string)
        Path to the output CSV file (string with '.csv')
        separator of the output csv (string)
    """
    # Create df
    df = toDataSet(inputFile)

    # To CSV
    df.to_csv(outputFile, sep=separator)


# Prob data generation
def generateProbeData(inputDf, tau, freq, scale='both'):
    """
    Extract GPS-style data from a dataFrame
    Inputs:
        inputDF : dataFrame with columns ['id', 't', 'X', 'Y', 'tron', 'dst', 'vit']
        tau : Proportion of vehicles with GPS gear
        freq : period of information output
        scale : 'relative' -> relative to the troncons / 'global' -> coordinate in Lambert 93 / 'both'
    Outputs:
        pandas' dataFrame with columns ['id', 't', 'tron', 'dst', 'vit'] if scale = 'relative'
        pandas' dataFrame with columns ['id', 't', 'X', 'Y', 'vit'] if scale = 'global'
        pandas' dataFrame with columns ['id', 't', 'X', 'Y', 'tron', 'dst', 'vit'] is scale = 'both'
    """
    # On choisit un échantillon de véhicule parmis l'ensemble des véhicules présents
    indices = random.sample(set(pd.unique(inputDf.id)), int(
        tau * np.size(pd.unique(inputDf.id))))
    newDf = inputDf[inputDf.id.isin(indices)]

    # On supprime les colonnes correspondantes
    if scale == 'global':
        # keep only the global scale columns
        newDf = newDf.loc[:, ['id', 't', 'X', 'Y', 'vit']]
    elif scale == 'relative':
        # keep only the relative scale columns
        newDf = newDf.loc[:, ['id', 't', 'tron', 'dst', 'vit']]
    elif scale != 'both':
        # raise an error if the scale argument do not correspond to what it should be
        raise TypeError(
            'the argument \'scale\' has to be one of \'both\', \'global\' or \'relative\' ')

    # Frequence de remontée
    for id in pd.unique(newDf.id):
        firstPoint = int(min(newDf[newDf.id == id].t)
                         ) + random.randint(0, freq - 1)
        times = list(range(firstPoint, int(
            max(newDf[newDf.id == id].t)), freq))
        # On récupère les lignes correspondantes, on range par t puis id et on réinitialise les index.
        newDf = newDf[(newDf['t'].isin(times)) | (newDf['id'] != id)].sort_values(
            by=['t', 'id']).reset_index(drop=True)

    return newDf

# Loop Datageneration
# For One loop


def generateOneLoopData(df, tron, dst, agg):
    """
    Generate Loop data for One loop
    Inputs:
        df : dataFrame with columns ['id', 't', 'X', 'Y', 'tron', 'dst', 'vit']
        tron : ID of the troncon
        dst : distance of the loop from the entry of the troncon
        agg : aggregation period
    Outputs:
        outputTimes : list of times
        outputFlow : list of flow corresponding to the times
    """
    # On filtre la dataframe par rapport au tronçon considéré
    df = df[df.tron == tron]

    # On génère les données de temps de passage à la boucle
    times = []
    # boucle sur les différents véhicules
    for id in pd.unique(df.id):
        # Interpolation linéaire ?? pour trouver l'instant de passage de la boucle
        times.append(np.interp(dst, df[df.id == id].dst, df[df.id == id].t))

    times = np.array(times)
    # Partie aggrégation
    outputTimes = list(np.arange(agg, max(df.t), agg))
    outputFlow = []
    for time in outputTimes:
        outputFlow.append(np.size(
            times[list(np.where((times < time) & (times > (time - agg)))[0])]) / agg)

    return (outputTimes, outputFlow)

# For all loops in a DataSet


def generateLoopData(trajsDf, loopsDf, agg):
    """
        Generate loop data for multiple loops
        Inputs:
            trajsDf : pandas' dataFrame with columns ['id', 't', 'X', 'Y', 'tron', 'dst', 'vit']
            loopsDf : pandas' dataFrame with columns ['tron', 'dst']
            agg : aggregation period
        Output:
            pandas' dataFrame with columns ['id', 't', 'flow']
    """
    # On créer une nouvelle data frame
    output = pd.DataFrame(columns=['id', 't', 'flow'])
    # On boucle sur les boucles
    for i in range(len(loopsDf.index)):
        times, flows = generateOneLoopData(
            trajsDf, tron=loopsDf.iloc[i]['tron'], dst=int(loopsDf.iloc[i]['dst']), agg=agg)
        # Génération de la nouvelle dataFrame
        newDf = pd.DataFrame(
            {"id": [loopsDf.iloc[i]['id']] * len(times),
             "t": times,
             "flow": flows})
        # Concaténation
        output = pd.concat([output, newDf])

        output = output[['id', 't', 'flow']].sort_values(
            by='t').reset_index(drop=True)
    return output
