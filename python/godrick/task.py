from godrick.computeResources import ComputeCollection
from enum import Enum

class TaskType(Enum):
    SINGLETON = 0,
    MPI = 0

class Task():
    def __init__(self, type:TaskType, name:str, cmdline:str, resources:ComputeCollection = None) -> None:
        super().__init__()
        self.name = name
        self.type = type
        self.cmdline = cmdline
        self.resources = resources
        self.inputPort = []
        self.outputPort = []

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
        result["inputPorts"] = []
        result["outputPorts"] = []
        return result
    
    def hasBeenProcessed(self) -> bool:
        return self.processedByLauncher
    
    def markAsProcessed(self) -> None:
        if self.processedByLauncher:
            raise RuntimeError(f"Trying to mark the task {self.name} as processed but it was already processed. Called multiple time a launcher?")
        self.processedByLauncher = True

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

    def getPlacementPolicy(self) -> MPIPlacementPolicy:
        return self.placementPolicy
    
    def setGlobalRanks(self, start:int, size:int) -> None:
        self.startRank = start
        self.nbRanks = size
    
    def toDict(self) -> dict:
        result =  super().toDict()
        result["startRank"] = self.startRank
        result["nbRanks"] = self.nbRanks

        return result
