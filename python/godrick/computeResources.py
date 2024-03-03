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

class ComputeNode(ComputeResources):
    def __init__(self) -> None:
        self.hostname = ""
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
            
class ComputeCluster(ComputeResources):
    def __init__(self, name:str="defaultCluster") -> None:
        self.nodes = []
        self.name = name

    def initFromHostFile(self, file:Path, addHT:bool=True) -> None:
        if len(self.nodes) > 0:
            raise RuntimeError(f"Cannot initialize the ComputeCluster {self.name} from a hostfile, the cluster already has nodes attached to it.")
        with open(file, "r") as f:
            lines = list(filter(None, f.read().splitlines())) # splitlines to remove the \n, filter to remove the empty lines
            machines = Counter(lines)
            for hostname, nbCores in machines.items():
                node = ComputeNode()
                node.initAutomatic(hostname=hostname, nbSockets=1, coresPerSocket=nbCores, useHT=addHT)
                self.nodes.append(node)
    
    def getNbNodes(self) -> int:
        return len(self.nodes)
    
    def getNodeByIndex(self, index:int) -> ComputeNode:
        if index >= len(self.nodes):
            raise IndexError(f"Queried node index {index} but the cluster only has {len(self.nodes)} nodes registered.")
        
        return self.nodes[index]
    
    def selectNodesByRange(self, ranges:List[int]) -> List[ComputeCluster]:
        totalNbNodes = sum(ranges)
        if totalNbNodes > len(self.nodes):
            raise ValueError(f"Requested {totalNbNodes} from the cluster {self.name}, but only {len(self.nodes)} are available.")
        
        result = []
        currentIndex = 0
        for interval in ranges:
            print(interval)
            cluster = ComputeCluster(name=f"{self.name}-{currentIndex}-{currentIndex+interval}")
            cluster.nodes = self.nodes[currentIndex:currentIndex+interval]
            result.append(cluster)
            currentIndex += interval 
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


    