#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse as argp
import fileinput
import json
import random
import numpy as np
import shutil
import csv

# parse command-line args
parser = argp.ArgumentParser(
   description = 'This script creates input files for CCluster hierarchical cluster visualization tool.')

parser.add_argument(
   '-i',
   dest = 'graphFile',
   help = 'Input file containing a similarity graph in edge list format')

parser.add_argument(
   '-c',
   dest = 'clustFile',
   help = 'Input file containing hierarchical clusters')

parser.add_argument(
   '-m',
   dest = 'metaFile',
   help = 'Input file containing cluster meta data')

parser.add_argument(
   '-d',
   dest = 'baseDir',
   help = 'Base directory to store output files')


args = parser.parse_args()


class Embedding(object):

    #region Reading data

    #def ReadTestFile():
    #    with open('smalldata.json') as data_file:    
    #        data = json.load(data_file)
    #        return data

    @staticmethod
    def ReadMetaDataFile(filename):
        """File format: [id] [metadata] 
        metadata format: "first_line" "second_line" "third_line" """
        metaDataDict = dict()
        for line in fileinput.input([filename]):
            if line != "\n":   
                for items in csv.reader([line], delimiter=' ', quotechar='"'): 
                    id = items[0]     
                    items.pop(0)                             
                    metaDataDict[id] = items
        return metaDataDict

    @staticmethod
    def ReadPropertiesIntensitiesFile(filename):
        """File format: [id] [intensityOfProperty1] [intensityOfProperty2]... [intensityOfPropertyN]"""      
        intensitiesDict = dict()
        for line in fileinput.input([filename]):
            if line != "\n":   
                items = line.split()
                id = items[0]     
                items.pop(0)                             
                intensitiesDict[id] = items
        return intensitiesDict

    @staticmethod
    def ReadSimilarityGraph(filename):
        """Reads from simGraphFile, that has a format ' id1 id2 similarityScore '.
        Returns a dictionary with key = (id1, id2) and value = similarityScore."""
        similarityDict = dict()
        for line in fileinput.input([filename]):
            if line != "\n":   
                items = line.split()
                similarityDict[items[0], items[1]] = float(items[2])
        return similarityDict

    @staticmethod
    def readClusteringHierarchy(filename):
        """Reads file of format 'path id'. 
        Path has a format id1.id2.id3.id4 if there are 4 levels in clustering hierarchy.
        If idx is singleton after e.g. second level, path has a format id1.id2.idx.idx
        
        Returns a dictionary with key= id and value = [id1, id2, idr, id4] """
        paths = dict()
        for line in fileinput.input([filename]):
            if line != "\n":   
                items = line.split()
                paths[items[1]] = items[0].split('.')
        return paths

    #endregion 
    
    #region Analytics

    @staticmethod
    def ConvertSimilarityGraphToDistance(similarityDict):
        """Converts non-negative real-valued similary scores to distances between 0 and 1 """
        maxScore = max(similarityDict.values())
        if maxScore > 0:
            for key in similarityDict.keys():
                similarityDict[key] = 1 - similarityDict[key] / maxScore # the distance is between 0 and 1
        else:
            for key in similarityDict.keys():
                similarityDict[key] = 1   

    @staticmethod
    def FindChildren(parent, level, pathsDict): 
        """Returns a list of all direct children of parent at the given level. """               
        children = []       
        for key in pathsDict.keys():
            nivo = len(pathsDict[key])
            if nivo > level + 1 and pathsDict[key][level] == parent and pathsDict[key][level + 1] == key:
                children.append(key)
            else:
                if nivo == level + 1 and pathsDict[key][level] == parent:
                    children.append(key)                          
        return children

    @staticmethod
    def InitializePointsRandomly(keys, fixedCoordinate, coordinates):
        """All objects in keys whose coordinates are not fixed yet are assigned random coordinates with values in (0,1)"""
        for key in keys:
            if key not in fixedCoordinate.keys():
                coordinates[key] = np.array([random.random(), random.random(), random.random()])                  

    def FixCoordinates(self, keys, edgesDict, fixedCoordinate, coordinates):
        """Implements the Stochastic Proximity Embedding algorithm to determine and fix the coordinates of objects with ids in keys.
        See https://www.researchgate.net/publication/10696705_Stochastic_proximity_embedding"""
        lambd = 1.0           
        epsilon = 0.00001             
        self.InitializePointsRandomly(keys, fixedCoordinate, coordinates)#coordinates is a dictionary per parent id, value is a list of 3
        cycles = 100
        numberOfPoints = len(keys)
        steps = 10 * numberOfPoints
        delta = 1.0 / cycles
        while (lambd > 0):
            for count in range(0, steps):                
                i = random.choice(keys)
                j = random.choice(keys)
                if i != j and (i,j) in edgesDict.keys(): # -> keys() not needed 
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

    def RecursivelyEmbed(self, parents, level, pathsDict, edgesDict, fixedCoordinate, coordinates):
        """Embeds the hierarchicall data set in a hiearchical manner"""
        self.FixCoordinates(parents, edgesDict, fixedCoordinate, coordinates)
        for parent in parents:
            children = self.FindChildren(parent, level, pathsDict)
            if len(children) > 0:
                self.RecursivelyEmbed(children, level+1, pathsDict, edgesDict, fixedCoordinate, coordinates)     
    
    #endregion

    #region Write output

    @staticmethod
    def CreateDataJSONFile(allPoints, parentsKeys, baseDir):
        currentPoints= dict()
        for key in parentsKeys:
            currentPoints[key] = allPoints[key]
        string = json.dumps(currentPoints)
        fout = open(os.path.join(baseDir, "data.json"), "w")
        fout.write(string)
        fout.close()

    def RecursivelyCreateDataFileAndFolders(self, allPoints, parentsKeys, level, baseDir, pathsDict):#allPoints is a dict where keys are id's and values are Point objects    
        self.CreateDataJSONFile(allPoints, parentsKeys, baseDir)
        for parent in parentsKeys:
            childrenKeys = self.FindChildren(parent, level, pathsDict)
            if len(childrenKeys) > 0:
                parentDir = os.path.join(baseDir, parent)
                self.CreateDirIfDoesNotExist(parentDir)
                self.RecursivelyCreateDataFileAndFolders(allPoints, childrenKeys, level+1, parentDir, pathsDict)       
    
    @staticmethod
    def CreateSmallDataJSONFile(allPoints, baseDir):
        string = json.dumps(allPoints)
        fout = open(os.path.join(baseDir, "smalldata.json"), "w")
        fout.write(string)
        fout.close()

    @staticmethod
    def CreateMetaDataFileForBigDataMode(baseDir, bigdatamode):
        string = "var bigData =" + bigdatamode + ";"
        fout = open(os.path.join(baseDir, "MetaData.js"), "w")
        fout.write(string)
        fout.close()

    @staticmethod
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

    @staticmethod
    def CreateDirIfDoesNotExist(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    @staticmethod
    def RemoveDirTreeIfExists(dirname):
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

    #endregion 

    #region Workflow
    @staticmethod
    def ExtractRoots(pathsDict):
        roots = []
        for path in pathsDict.values():
            roots.append(path[0])
        roots = list(set(roots))
        return roots

    @staticmethod
    def ConvertCoordinatesToList(fixedCoordinate):
        for key in fixedCoordinate.keys():
            fixedCoordinate[key] = list(fixedCoordinate[key])
                       
    def Workflow(self, simGraphFile, clusteringHierarchyFile, metaDataFile, namesOfPropertiesFile, propertiesIntensitiesFile, baseDir, bigDataMode = "true"):
        """ Runs all functions to read, embed in 3D and write data.
        simGraphFile contains the sparse similarity matrix.  Format: [id1] [id2]  [similarityScore] 
        clusteringHierarchyFile contains path in tree for every id. Format: [parent1ID.parent2ID.parent3ID.....parentNID] [id]
        metaDataFile contains text that is displayed for every point. Format: [id] ["line1text"] ["line2text"] ... ["lineNtext"]
        namesOfPropertiesFile contains the names of the properties, the intensities of which are given in file propertiesIntensitiesFile. It must be a json file. Format : [ ["PropertyName1", "PropertyName2", ... "PropertyNameN"] ]. E.g. ["Age", "Size"]       
        propertiesIntensitiesFile contains the intensities of the properties per point. Format: [id] [intensityProperty1] [intensityProperty2] ... [intensityPropertyN]
        bigDataMode is "true" or "false", depending on the mode in which the application should run. If "false", then there is a slidebar for loading all points up to a level"""
        self.RemoveDirTreeIfExists(baseDir)
        metaDataDict = self.ReadMetaDataFile(metaDataFile)
        intensitiesDict = self.ReadPropertiesIntensitiesFile(propertiesIntensitiesFile)
        edgesDict = self.ReadSimilarityGraph(simGraphFile)
        self.ConvertSimilarityGraphToDistance(edgesDict)
        pathsDict = self.readClusteringHierarchy(clusteringHierarchyFile)
        fixedCoordinate = dict()
        coordinates = dict()
        roots = self.ExtractRoots(pathsDict)        
        self.RecursivelyEmbed(roots, 0, pathsDict, edgesDict, fixedCoordinate, coordinates)
        self.ConvertCoordinatesToList(fixedCoordinate)
        pointsDict = self.CreatePointsDictionary(fixedCoordinate, pathsDict, metaDataDict, intensitiesDict)        
        self.CreateDirIfDoesNotExist(baseDir)
        self.RecursivelyCreateDataFileAndFolders(pointsDict, roots, 0, baseDir, pathsDict)
 
        if bigDataMode == "false": 
            self.CreateSmallDataJSONFile(pointsDict, baseDir)
        shutil.copyfile(namesOfPropertiesFile, os.path.join(baseDir, namesOfPropertiesFile))
        self.CreateMetaDataFileForBigDataMode(baseDir, bigDataMode)
    #endregion
         
#region Main

spe = Embedding()
spe.Workflow(args.graphFile, args.clustFile, args.metaFile, "NamesOfProperties.json","testIntensitiesOfProperties.txt", args.baseDir, 'true')

#endregion
