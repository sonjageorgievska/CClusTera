import fileinput #for reading large files
import json
import random
import numpy as np
import os
import shutil
import csv 
           
class Embedding:

    #region Reading data

    def ReadTestFile():
        with open('smalldata.json') as data_file:    
            data = json.load(data_file)
            return data

    def ReadMetaDataFile(metaDataFile):
        """File format: [id] [metadata] 
        metadata format: "first_line" "second_line" "third_line" """
        metaDataDict = dict()
        for line in fileinput.input([metaDataFile]):
            if line != "\n":   
                for items in csv.reader([line], delimiter=' ', quotechar='"'): 
                    id = items[0]     
                    items.pop(0)                             
                    metaDataDict[id] = items
        return metaDataDict

    def ReadPropertiesIntensitiesFile(propertiesIntensitiesFile):
        """File format: [id] [intensityOfProperty1] [intensityOfProperty2]... [intensityOfPropertyN]"""      
        intensitiesDict = dict()
        for line in fileinput.input([propertiesIntensitiesFile]):
            if line != "\n":   
                items = line.split()
                id = items[0]     
                items.pop(0)                             
                intensitiesDict[id] = items
        return intensitiesDict

    def ReadSimilarityGraph(simGraphFile):
        """Reads from simGraphFile, that has a format ' id1 id2 similarityScore '.
        Returns a dictionary with key = (id1, id2) and value = similarityScore."""
        similarityDict = dict()
        for line in fileinput.input([simGraphFile]):
            if line != "\n":   
                items = line.split()
                similarityDict[items[0], items[1]] = float(items[2])                
        return similarityDict

    def readClusteringHierarchy(clusteringHierarchyFile):
        """Reads file of format 'path id'. 
        Path has a format id1.id2.id3.id4 if there are 4 levels in clustering hierarchy.
        If idx is singleton after e.g. second level, path has a format id1.id2.idx.idx
        
        Returns a dictionary with key= id and value = [id1, id2, idr, id4] """
        paths = dict()
        for line in fileinput.input([clusteringHierarchyFile]):
            if line != "\n":   
                items = line.split()
                paths[items[1]] = items[0].split('.')
        return paths
    
    #endregion 
    
    #region Analytics

    def MakeChildrenListPerParentPerLevel(pathsDict):
        dictionary = dict()
        for key in pathsDict.keys():
            level = 0
            for parent in pathsDict[key]:                
                nivo = len(pathsDict[key]) 
                toPut = 0
                if nivo > level + 1 and pathsDict[key][level] == parent and pathsDict[key][level + 1] == key:
                    toPut = 1
                else:
                    if nivo == level + 1 and pathsDict[key][level] == parent:
                        toPut = 1
                if toPut == 1:
                    if parent not in dictionary.keys():
                        dictionary[parent] = []
                    while len(dictionary[parent]) <= level:
                        dictionary[parent].append([])
                    dictionary[parent][level].append(key)
                level +=1
        return dictionary     

    def ConvertSimilarityGraphToDistance(similarityDict):
        """Converts non-negative real-valued similary scores to distances between 0 and 1 """
        maxScore = max(similarityDict.values())
        if maxScore > 0:
            for key in similarityDict.keys():
                similarityDict[key] = 1- similarityDict[key]/maxScore # the distance is between 0 and 1
        else:
            for key in similarityDict.keys():
                similarityDict[key] = 1   

    def FindChildren(parent, level, childrenDict): 
        """Returns a list of all direct children of parent at the given level. """     
        if parent in childrenDict.keys() and len(childrenDict[parent]) > level:
            return  childrenDict[parent][level]   
        else:
            return []
       
    def InitializePointsRandomly(keys, fixedCoordinate, coordinates):
        """All objects in keys whose coordinates are not fixed yet are assigned random coordinates with values in (0,1)"""
        for key in keys:
            if key not in fixedCoordinate.keys():
                coordinates[key] = np.array([random.random(), random.random(), random.random()])                  

    def FixCoordinates(keys, edgesDict, fixedCoordinate, coordinates):
        """Implements the Stochastic Proximity Embedding algorithm to determine and fix the coordinates of objects with ids in keys.
        See https://www.researchgate.net/publication/10696705_Stochastic_proximity_embedding"""
        lambd = 1.0           
        epsilon = 0.00001             
        Embedding.InitializePointsRandomly(keys, fixedCoordinate, coordinates)#coordinates is a dictionary per parent id, value is a list of 3
        cycles = 100
        numberOfPoints = len(keys)
        steps = 10 * numberOfPoints
        delta = 1.0 / cycles
        while (lambd > 0):
            for count in range(0, steps):                
                i = random.choice(keys)
                j = random.choice(keys)
                if i != j and (i,j) in edgesDict.keys(): 
                    dist = np.linalg.norm(coordinates[i] - coordinates[j])
                    rd = edgesDict[i,j]
                    if dist != rd:                        
                        vec = coordinates[i] - coordinates[j]
                        incr = lambd * 0.5 * (rd - dist) * vec / (dist + epsilon)
                        if i not in fixedCoordinate.keys():
                            coordinates[i] += incr
                        if j not in fixedCoordinate.keys():
                            coordinates[j] += (-1) * incr                                                           
            lambd -= delta      
        for key in keys:
            fixedCoordinate[key] = coordinates[key]      

    def RecursivelyEmbed(parents, level, edgesDict, fixedCoordinate, coordinates, childrenDict):
        """Embeds the hierarchicall data set in a hiearchical manner"""
        Embedding.FixCoordinates(parents, edgesDict, fixedCoordinate, coordinates)
        for parent in parents:
            children = Embedding.FindChildren(parent, level, childrenDict)
            if len(children) > 0:
                Embedding.RecursivelyEmbed(children, level+1,  edgesDict, fixedCoordinate, coordinates, childrenDict)     
    
    #endregion

    #region Write output

    def CreateDataJSONFile(allPoints, parentsKeys, startingFolder):
        currentPoints= dict()
        for key in parentsKeys:
            currentPoints[key] = allPoints[key]
        string = json.dumps(currentPoints)
        file = open(startingFolder + "/data.json", "w")
        file.write(string)
        file.close()

    def RecursivelyCreateDataFileAndFolders(allPoints, parentsKeys, level, startingFolder, childrenDict):#allPoints is a dict where keys are id's and values are Point objects    
        Embedding.CreateDataJSONFile(allPoints, parentsKeys, startingFolder)
        for parent in parentsKeys:
            childrenKeys = Embedding.FindChildren(parent, level, childrenDict)
            if len(childrenKeys) > 0:
                Embedding.CreateDirIfDoesNotExist(startingFolder + "/" + parent)
                Embedding.RecursivelyCreateDataFileAndFolders(allPoints, childrenKeys, level+1, startingFolder + "/" + parent, childrenDict)       
    
    def CreateSmallDataJSONFile(allPoints, startingFolder):
        string = json.dumps(allPoints)
        file = open(startingFolder + "/smalldata.json", "w")
        file.write(string)
        file.close()
   
    def CreateMetaDataFileForBigDataMode(startingFolder, bigdatamode):
        string = "var bigData =" + bigdatamode + ";"
        file = open(startingFolder + "/MetaData.js", "w")
        file.write(string)
        file.close()

    def CreatePointsDictionary(fixedCoordinates, pathsDict, metaDataDict, intensitiesOfPropertiesDict):
        pointsDict = dict()
        for key in pathsDict.keys():
            point = dict()
            point["Path"] = pathsDict[key]
            point["Coordinates"] = fixedCoordinates[key]
            point["Categories"] = metaDataDict[key]
            point["Properties"] = intensitiesOfPropertiesDict[key]
            pointsDict[key] = point
        return pointsDict

    def CreateDirIfDoesNotExist(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def RemoveDirTreeIfExists(dirname):
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

    #endregion 

    #region Workflow
    def ExtractRoots(pathsDict):
        roots = []
        for path in pathsDict.values():
            roots.append(path[0])
        roots = list(set(roots))
        return roots

    def ConvertCoordinatesToList(fixedCoordinate):
        for key in fixedCoordinate.keys():
            fixedCoordinate[key] = list(fixedCoordinate[key])
                       
    def Workflow(simGraphFile, clusteringHierarchyFile, metaDataFile, namesOfPropertiesFile, propertiesIntensitiesFile, bigDataMode = "true"):
        """ Runs all functions to read, embed in 3D and write data.
        simGraphFile contains the sparse similarity matrix.  Format: [id1] [id2]  [similarityScore] 
        clusteringHierarchyFile contains path in tree for every id. Format: [parent1ID.parent2ID.parent3ID.....parentNID] [id]
        metaDataFile contains text that is displayed for every point. Format: [id] ["line1text"] ["line2text"] ... ["lineNtext"]
        namesOfPropertiesFile contains the names of the properties, the intensities of which are given in file propertiesIntensitiesFile. It must be a json file. Format : [ ["PropertyName1", "PropertyName2", ... "PropertyNameN"] ]. E.g. ["Age", "Size"]       
        propertiesIntensitiesFile contains the intensities of the properties per point. Format: [id] [intensityProperty1] [intensityProperty2] ... [intensityPropertyN]
        bigDataMode is "true" or "false", depending on the mode in which the application should run. If "false", then there is a slidebar for loading all points up to a level"""
        Embedding.RemoveDirTreeIfExists("data")
        metaDataDict = Embedding.ReadMetaDataFile(metaDataFile)
        intensitiesDict = Embedding.ReadPropertiesIntensitiesFile(propertiesIntensitiesFile)
        edgesDict = Embedding.ReadSimilarityGraph(simGraphFile)
        Embedding.ConvertSimilarityGraphToDistance(edgesDict)
        pathsDict = Embedding.readClusteringHierarchy(clusteringHierarchyFile)
        childrenDict = Embedding.MakeChildrenListPerParentPerLevel(pathsDict)
        fixedCoordinate = dict()
        coordinates = dict()
        roots = Embedding.ExtractRoots(pathsDict)        
        Embedding.RecursivelyEmbed(roots, 0, edgesDict, fixedCoordinate, coordinates, childrenDict)
        Embedding.ConvertCoordinatesToList(fixedCoordinate)
        pointsDict = Embedding.CreatePointsDictionary(fixedCoordinate, pathsDict, metaDataDict, intensitiesDict)        
        Embedding.CreateDirIfDoesNotExist("data")
        Embedding.RecursivelyCreateDataFileAndFolders(pointsDict, roots, 0, "data", childrenDict)
        if bigDataMode == "false": 
            Embedding.CreateSmallDataJSONFile(pointsDict, "data")
        shutil.copyfile(namesOfPropertiesFile, "data/NamesOfProperties.json")
        Embedding.CreateMetaDataFileForBigDataMode("data", bigDataMode)
    #endregion
         
#region Main

Embedding.Workflow("testFile.txt", "testClust.txt", "testMetaData.txt", "NamesOfProperties.json","testIntensitiesOfProperties.txt", "false")

#endregion

