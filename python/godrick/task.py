from __future__ import annotations

from godrick.computeResources import ComputeCollection
from godrick.port import InputPort, OutputPort
from enum import Enum
from typing import List

class TaskType(Enum):
    SINGLETON = 0,
    MPI = 0

class Process():
    def __init__(self, hostname:str, task:Task) -> None:
        self.hostname = hostname
        self.task = task

class Task():
    def __init__(self, type:TaskType, name:str, cmdline:str, resources:ComputeCollection = None) -> None:
        super().__init__()
        self.name = name
        self.type = type
        self.cmdline = cmdline
        self.resources = resources
        self.inputPort = {}
        self.outputPort = {}

        self.processedByLauncher = False    # Flag used when creating the command line
                                            # This will be switched when a launcher convert the Task to command line

    def setResources(self, resources:ComputeCollection) -> None:
        self.resources = resources  

    def getResources(self) -> ComputeCollection:
        return self.resources
    
    def getName(self) -> str:
        return self.name
    
    def getTaskType(self) -> TaskType:
        return self.type

    def getCommandLine(self) -> str:
        return self.cmdline
    
    def toDict(self) -> dict:
        result = {}
        result["name"] = self.name
        result["type"] = self.type.name
        result["inputPorts"] = list(self.inputPort.keys())
        result["outputPorts"] = list(self.outputPort.keys())
        return result
    
    def hasBeenProcessed(self) -> bool:
        return self.processedByLauncher
    
    def markAsProcessed(self) -> None:
        if self.processedByLauncher:
            raise RuntimeError(f"Trying to mark the task {self.name} as processed but it was already processed. Called multiple time a launcher?")
        self.processedByLauncher = True

    def addInputPort(self, portName:str) -> None:
        if portName in self.inputPort.keys():
            raise ValueError(f"The input port {portName} is already declared for the task {self.name}.")
        self.inputPort[portName] = InputPort(name=portName, task=self)

    def addOutputPort(self, portName:str) -> None:
        if portName in self.outputPort.keys():
            raise ValueError(f"The output port {portName} is already declared for the task {self.name}.")
        self.outputPort[portName] = OutputPort(name=portName, task=self)

    def getInputPort(self, portName:str) -> InputPort:
        if portName not in self.inputPort.keys():
            raise ValueError(f"The input port {portName} is not declared in the task {self.name}.")
        return self.inputPort[portName]
    
    def getOutputPort(self, portName:str) -> InputPort:
        if portName not in self.outputPort.keys():
            raise ValueError(f"The output port {portName} is not declared in the task {self.name}.")
        return self.outputPort[portName]
    
    def getProcessList(self) -> List[Process]:
        raise NotImplementedError("Function getProcessList not implemented by a task type")
    
class SingletonTask(Task):
    def __init__(self, name:str, cmdline:str, resources:ComputeCollection = None) -> None:
        super().__init__(TaskType.SINGLETON, name, cmdline, resources)  

class MPIPlacementPolicy(Enum):
    ONETASKPERCORE = 0,
    ONETASKPERSOCKET = 1,
    ONETASKPERNODE = 2,
    USERDEFINED = 3

class MPITask(Task):
    def __init__(self, name:str, cmdline:str, resources:ComputeCollection = None, placementPolicy:MPIPlacementPolicy = MPIPlacementPolicy.ONETASKPERCORE) -> None:
        super().__init__(TaskType.MPI, name, cmdline, resources)
        self.placementPolicy = placementPolicy

        # Values which will be used to map the ranks of the global MPI application
        # as defined by the MPILauncher to the local ranks for the task
        self.startRank = -1
        self.nbRanks = -1

        self.processes = []

    def getPlacementPolicy(self) -> MPIPlacementPolicy:
        return self.placementPolicy
    
    def setGlobalRanks(self, start:int, size:int) -> None:
        self.startRank = start
        self.nbRanks = size

    def getGlobalStartRank(self) -> int:
        return self.startRank
    
    def getGlobalNbRank(self) -> int:
        return self.nbRanks
    
    def toDict(self) -> dict:
        result =  super().toDict()
        result["startRank"] = self.startRank
        result["nbRanks"] = self.nbRanks

        return result
    
    def addProcess(self, process:Process) -> None:
        self.processes.append(process)
    
    def getProcessList(self) -> List[Process]:
        if not self.processedByLauncher:
            raise RuntimeError(f"The Task {self.name} has not being processed yet, unable to determine the process list.")
        return self.processes
        

