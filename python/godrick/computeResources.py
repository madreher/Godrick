from __future__ import annotations
from pathlib import Path
from collections import Counter
from typing import List


class ComputeResources():
    def __init__(self) -> None:
        pass

    def getListOfCores(self) -> List[dict]:
        raise NotImplementedError(f"Function not implemented by class {__class__}.")

class ComputeSocket(ComputeResources):
    def __init__(self) -> None:
        self.mainThreads = []
        self.hyperThreads = []
        self.hostname = ""
        self.hasHT = False
    
    def initAutomatic(self, hostname:str, nbCores:int = 1, offsetCore:int=0, useHT:bool=True, offsetHT:int=0):
        if nbCores < 1:
            raise ValueError("Number of cores in a socket must be greater than 0.")
        if offsetCore < 0:
            raise ValueError("Number of cores in a socket must be equal or greater than 0.")
        self.hostname = hostname
        self.mainThreads = list(range(offsetCore, offsetCore + nbCores))
        if useHT:
            if offsetHT <= self.mainThreads[-1]:
                raise ValueError("HT enable but the offset is inferior to the last regular core.")
            self.hyperThreads = list(range(offsetHT, offsetHT + nbCores))
            self.hasHT = True

    def initManual(self, hostname:str, mainThreads:list, ht:list = []):
        self.mainThreads = mainThreads
        self.hyperThreads = ht
        self.hostname = hostname
        if len(self.hyperThreads) > 0:
            self.hasHT = True

    def toDict(self) -> dict:
        result = {}
        result["mainthreads"] = self.mainThreads
        result["hyperthreads"] = self.hyperThreads
        result["hostname"] = self.hostname
        result["hasht"] = self.hasHT

        return result
    
    def hasHyperthreads(self) -> bool:
        return self.hasHT
    
    def getCoresIndexes(self) -> list:
        return self.mainThreads
    
    def getHTIndexes(self) -> list:
        return self.hyperThreads
    
    def getHostName(self) -> str:
        return self.hostname
    
    def getListOfCores(self) -> List[dict]:
        result = []
        for i in range(0, len(self.mainThreads)):
            core = {}
            core["hostname"] = self.hostname
            core["mainthread"] = self.mainThreads[i]
            if self.hasHT:
                core["hyperthread"] = self.hyperThreads[i]
            result.append(core)
        return result
    
    def selectCoresByIndexRange(self, startIndex:int, endIndex:int) -> List[ComputeSocket]:

        socket = ComputeSocket()
        socket.hasHT = self.hasHT
        socket.hostname = self.getHostName()
        for i, core in enumerate(self.mainThreads):
            if core >= startIndex and core <= endIndex:
                socket.mainThreads.append(self.mainThreads[i]) # == core
            if self.hasHT:
                socket.hyperThreads.append(self.hyperThreads[i])
        return socket

    def getNbCores(self) -> int:
        return len(self.mainThreads)

class ComputeNode(ComputeResources):
    def __init__(self, hostname:str="") -> None:
        self.hostname = hostname
        self.sockets = []

    def initAutomatic(self, hostname:str, nbSockets:int=1, coresPerSocket:int=1, useHT:bool=True):
        self.hostname = hostname
        for i in range(nbSockets):
            socket = ComputeSocket()
            htMultiplier = 1
            if useHT:
                htMultiplier = 2
            socket.initAutomatic(hostname=self.hostname,
                                 nbCores=coresPerSocket, 
                                 offsetCore=i*coresPerSocket*htMultiplier, 
                                 useHT=useHT, 
                                 offsetHT=i*coresPerSocket*htMultiplier + coresPerSocket)
            self.sockets.append(socket)
            
    def getNbSockets(self):
        return len(self.sockets)
    
    def getSocketByIndex(self, index:int) -> ComputeSocket:
        if index >= len(self.sockets):
            raise IndexError(f"Queried socket index {index} but the node only has {len(self.sockets)} sockets registered.")
        
        return self.sockets[index]
    
    def getHostName(self) -> str:
        return self.hostname
    
    def toDict(self) -> dict:
        result = {}
        result["hostname"] = self.hostname
        result["sockets"] = []
        for socket in self.sockets:
            result["sockets"].append(socket.toDict())
        return result
    
    def getListOfCores(self) -> List[dict]:
        result = []
        for socket in self.sockets:
            result.extend(socket.getListOfCores())
        return result
    
    def getListOfCoresPerSocket(self) -> List[dict]:
        result = []
        for socket in self.sockets:
            result.append(socket.getListOfCores())
        return result

    
    def getNbCores(self) -> int:
        result = 0
        for socket in self.sockets:
            result += socket.getNbCores()
        return result
    
    def selectCoresByIndexRange(self, startIndex:int, endIndex:int) -> ComputeNode:
        subNode = ComputeNode(self.hostname)
        for socket in self.sockets:
            subSocket = socket.selectCoresByIndexRange(startIndex=startIndex, endIndex=endIndex)
            if subSocket.getNbCores() > 0:
                subNode.sockets.append(subSocket)
        return subNode
            
class ComputeCollection(ComputeResources):
    def __init__(self, name:str="defaultCluster") -> None:
        self.nodes = []
        self.name = name

    def initFromHostFile(self, file:Path, addHT:bool=True) -> None:
        if len(self.nodes) > 0:
            raise RuntimeError(f"Cannot initialize the ComputeCollection {self.name} from a hostfile, the collection already has nodes attached to it.")
        with open(file, "r") as f:
            lines = list(filter(None, f.read().splitlines())) # splitlines to remove the \n, filter to remove the empty lines
            machines = Counter(lines)
            for hostname, nbCores in machines.items():
                node = ComputeNode()
                node.initAutomatic(hostname=hostname, nbSockets=1, coresPerSocket=nbCores, useHT=addHT)
                self.nodes.append(node)
    
    def initFromLocalhost(self, useHT:bool=True) -> None:
        if len(self.nodes) > 0:
            raise RuntimeError(f"Cannot initialize the ComputeCollection {self.name} from a hostfile, the collection already has nodes attached to it.")
        node = ComputeNode()

        import psutil
        nbPhysicalCores = psutil.cpu_count(logical=False)
        nbLogicalCores = psutil.cpu_count(logical=True)
        hasHt = nbLogicalCores != nbPhysicalCores
        node.initAutomatic(hostname="localhost", nbSockets=1, coresPerSocket=nbPhysicalCores, useHT=(useHT and hasHt))
        self.nodes.append(node)
        
    def getNbNodes(self) -> int:
        return len(self.nodes)
    
    def getNodeByIndex(self, index:int) -> ComputeNode:
        if index >= len(self.nodes):
            raise IndexError(f"Queried node index {index} but the cluster only has {len(self.nodes)} nodes registered.")
        
        return self.nodes[index]
    
    def selectNodesByRange(self, ranges:List[int]) -> List[ComputeCollection]:
        totalNbNodes = sum(ranges)
        if totalNbNodes > len(self.nodes):
            raise ValueError(f"Requested {totalNbNodes} from the cluster {self.name}, but only {len(self.nodes)} are available.")
        
        result = []
        currentIndex = 0
        for interval in ranges:
            cluster = ComputeCollection(name=f"{self.name}-{currentIndex}-{currentIndex+interval}")
            cluster.nodes = self.nodes[currentIndex:currentIndex+interval]
            result.append(cluster)
            currentIndex += interval 
        return result
    
    def splitNodesByCoreRange(self, ranges:List[int]) -> List[ComputeCollection]:
        if len(ranges) == 0:
            raise ValueError("List of core ranges is empty.")

        if len(self.nodes) == 0:
            raise ValueError("Requesting nodes split, but the collection does not currently contain nodes.")
        
        # Create the list of indexes
        startIndex = 0
        intervals = []
        for size in ranges:
            if size < 1:
                raise ValueError("Core range has to be equal or greater than 1.")
            intervals.append([startIndex, startIndex+size-1]) # -1 because we are considering indexes
            startIndex += size

        result = []
        for interval in intervals:
            cluster = ComputeCollection(name=f"{self.name}-c{interval[0]}-c{interval[1]}")
            nodes = []
            for node in self.nodes:
                subNode = node.selectCoresByIndexRange(interval[0], interval[1])
                if subNode.getNbCores() == 0:
                    raise RuntimeError(f"Request cores from {interval[0]} to {interval[1]} on node {subNode.getName()}, but no cores found for these indexes.")
                nodes.append(subNode)
            cluster.nodes = nodes
            result.append(cluster)
        return result

    def toDict(self) -> dict:
        result = {}
        result["name"] = self.name
        result["nodes"] = []
        for node in self.nodes:
            result["nodes"].append(node.toDict())

        return result
    
    def getListOfCores(self) -> List[dict]:
        result = []
        for node in self.nodes:
            result.extend(node.getListOfCores())
        return result
    
    def getListOfCoresPerSocket(self) -> List[List[dict]]:
        result = []
        for node in self.nodes:
            result.extend(node.getListOfCoresPerSocket())
        return result
    
    def getListOfCoresPerNode(self) -> List[List[dict]]:
        result = []
        for node in self.nodes:
            result.append(node.getListOfCores())
        return result


    