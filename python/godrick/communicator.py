from enum import Enum
from godrick.port import InputPort, OutputPort

class CommunicatorType(Enum):
    MPI = 0,
    ZMQ = 1

class MPICommunicatorProtocol(Enum):
    BROADCAST = 0,
    PARTIAL_BCAST_GATHER = 1

class Communicator():
    def __init__(self, name:str, type:CommunicatorType) -> None:
        self.name = name
        self.type = type
        self.inputPortName = ""
        self.inputTaskName = ""
        self.outputPortName = ""
        self.outputTaskName = ""

        self.processedByLauncher = False    # Flag used when creating the command line
                                            # This will be switched when a launcher convert the Task to command line

    def getName(self) -> str:
        return self.name
    
    def getCommunicatorType(self) -> CommunicatorType:
        return self.type

    def getInputTaskName(self) -> str:
        return self.inputTaskName
    
    def getOutputTaskName(self) -> str:
        return self.outputTaskName

    def connectInput(self, port:InputPort) -> None:
        self.inputPortName = port.getPortName()
        self.inputTaskName = port.getTaskName()

    def connectOutput(self, port:OutputPort) -> None:
        self.outputPortName = port.getPortName()
        self.outputTaskName = port.getTaskName()

    def toDict(self) -> dict:
        result = {}
        result["name"] = self.name
        result["type"] = self.type.name
        result["inputPortName"] = self.inputPortName
        result["inputTaskName"] = self.inputTaskName
        result["outputPortName"] = self.outputPortName
        result["outputTaskName"] = self.outputTaskName

        return result

    def isValid(self):
        return self.inputPortName != "" and self.inputTaskName != "" and self.outputPortName != "" and self.outputTaskName != ""
    
    def hasBeenProcessed(self) -> bool:
        return self.processedByLauncher
    
    def markAsProcessed(self) -> None:
        if self.processedByLauncher:
            raise RuntimeError(f"Trying to mark the communicator {self.name} as processed but it was already processed. Called multiple time a launcher?")
        self.processedByLauncher = True

class MPICommunicator(Communicator):
    def __init__(self, id: str, protocol: MPICommunicatorProtocol = MPICommunicatorProtocol.BROADCAST) -> None:
        super().__init__(id, CommunicatorType.MPI)
        self.inStartRank = -1
        self.inSize = -1
        self.outStartRank = -1
        self.outSize = -1
        self.protocol = protocol

    def toDict(self) -> dict:
        result =  super().toDict()
        result["inStartRank"] = self.inStartRank
        result["inSize"] = self.inSize
        result["outStartRank"] = self.outStartRank
        result["outSize"] = self.outSize
        result["mpiprotocol"] = self.protocol.name
        return result
    
    def setInputMPIRanks(self, start:int, size:int) -> None:
        self.inStartRank = start
        self.inSize = size

    def setOutputMPIRanks(self, start:int, size:int) -> None:
        self.outStartRank = start
        self.outSize = size

    def setMPIProtocol(self, protocol:MPICommunicatorProtocol) -> None:
        self.protocol = protocol

    

    