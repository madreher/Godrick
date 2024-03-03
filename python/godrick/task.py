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

class SingletonTask(Task):
    def __init__(self, name:str, cmdline:str, resources:ComputeCollection = None) -> None:
        super().__init__(TaskType.SINGLETON, name, cmdline, resources)  

class MPIPlacementPolicy(Enum):
    ONETASKPERCORE = 0,
    ONETASKPERSOCKET = 1,
    ONETESTPERNODE = 2,
    USERDEFINED = 3

class MPITask(Task):
    def __init__(self, name:str, cmdline:str, resources:ComputeCollection = None, placementPolicy:MPIPlacementPolicy = MPIPlacementPolicy.ONETASKPERCORE) -> None:
        super().__init__(TaskType.MPI, name, cmdline, resources)
        self.placementPolicy = placementPolicy

    def getPlacementPolicy(self) -> MPIPlacementPolicy:
        return self.placementPolicy
