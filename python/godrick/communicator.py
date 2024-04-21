from __future__ import annotations

from enum import Enum
from godrick.port import InputPort, OutputPort
from typing import List
from godrick.task import Process
import copy

class CommunicatorTransportType(Enum):
    MPI = 0,
    ZMQ = 1

class CommunicatorGateSideFlag(Enum):
    OPEN_SENDER = 0,
    OPEN_RECEIVER = 1

class MPICommunicatorProtocol(Enum):
    BROADCAST = 0,
    PARTIAL_BCAST_GATHER = 1

class ZMQCommunicatorProtocol(Enum):
    PUSH_PULL = 0,
    PUB_SUB = 1

class Communicator():
    def __init__(self, name:str, transport:CommunicatorTransportType) -> None:
        self.name = name
        self.transport = transport

        self.configured = False
        self.processedByLauncher = False    # Flag used when creating the command line
                                            # This will be switched when a launcher convert the Task to command line

    def getName(self) -> str:
        return self.name
    
    def getCommunicatorTransportType(self) -> CommunicatorTransportType:
        return self.transport

    def toDict(self) -> dict:
        result = {}
        result["name"] = self.name
        result["transport"] = self.transport.name
        result["configured"] = self.configured

        return result
    
    def fromDict(self, data:dict, version:int) -> None:

        self.name = data["name"]
        self.transport = CommunicatorTransportType[data["transport"]]
        self.configured = data["configured"]

    def isValid(self):
        #if self.openFlag == CommunicatorOpenFlag.CLOSED:
        #    return self.inputPortName != "" and self.inputTaskName != "" and self.outputPortName != "" and self.outputTaskName != ""
        #elif self.openFlag == CommunicatorOpenFlag.OPEN_INPUT:
        #    return self.inputPortName != "" and self.inputTaskName != ""
        #elif self.openFlag == CommunicatorOpenFlag.OPEN_OUTPUT:
        #    return self.outputPortName != "" and self.outputTaskName != ""
        #else:
        #    return False
        raise NotImplementedError("A Communicator class did not implement the isValid() function.")
    
    def hasBeenProcessed(self) -> bool:
        return self.processedByLauncher
    
    def markAsProcessed(self) -> None:
        if self.processedByLauncher:
            raise RuntimeError(f"Trying to mark the communicator {self.name} as processed but it was already processed. Called multiple time a launcher?")
        self.processedByLauncher = True

    def assignSenderProcesses(self, processes: List[Process]) -> None:
        raise NotImplementedError("AssignSenderProcesses() is not implemented by a Communicator.")
    
    def assignReceiverProcesses(self, processes: List[Process]) -> None:
        raise NotImplementedError("AssignReceiverProcesses() is not implemented by a Communicator.")
    
    def getInputTaskName(self) -> str:
        raise NotImplementedError("getInputTaskName() is not implemented by a Communicator.")
    
    def getOutputTaskName(self) -> str:
        raise NotImplementedError("getOutputTaskName() is not implemented by a Communicator.")
    
    def connectToInputPort(self, port:InputPort) -> None:
        raise NotImplementedError("connectToInputPort() is not implemented by a Communicator.")

    def connectToOutputPort(self, port:OutputPort) -> None:
        raise NotImplementedError("connectToOutputPort() is not implemented by a Communicator.")
    
    def isPairedCommunicator(self) -> bool:
        return False 
    
    def isSenderGate(self) -> bool:
        return False
    
    def isReceiverGate(self) -> bool:
        return False
    
    def isGate(self) -> bool:
        return False


class PairedCommunicator(Communicator):
    def __init__(self, name: str, transport: CommunicatorTransportType) -> None:
        super().__init__(name, transport)

        self.inputPortName = ""
        self.inputTaskName = ""
        self.outputPortName = ""
        self.outputTaskName = ""

        self.senderProcesses = []
        self.receiverProcesses = []

    def getInputTaskName(self) -> str:
        return self.inputTaskName
    
    def getOutputTaskName(self) -> str:
        return self.outputTaskName

    def connectToInputPort(self, port:InputPort) -> None:
        self.inputPortName = port.getPortName()
        self.inputTaskName = port.getTaskName()

    def connectToOutputPort(self, port:OutputPort) -> None:
        self.outputPortName = port.getPortName()
        self.outputTaskName = port.getTaskName()

    def isValid(self):
        return self.inputPortName != "" and self.inputTaskName != "" and self.outputPortName != "" and self.outputTaskName != ""
    
    def assignSenderProcesses(self, processes: List[Process]) -> None:
        self.senderProcesses = processes
    
    def assignReceiverProcesses(self, processes: List[Process]) -> None:
        self.receiverProcesses = processes

    def markAsProcessed(self) -> None:
        if self.processedByLauncher:
            raise RuntimeError(f"Trying to mark the communicator {self.name} as processed but it was already processed. Called multiple time a launcher?")
        
        if len(self.senderProcesses) == 0:
            raise RuntimeError(f"Trying to mark the communicator {self.name} as processed but the sender side doesn't have processes assigned.")
        
        if len(self.receiverProcesses) == 0:
            raise RuntimeError(f"Trying to mark the communicator {self.name} as processed but the receiver side doesn't have processes assigned.")

        self.processedByLauncher = True

    #def connectOpenInput(self, comm:Communicator) -> None:
    #    if self.getCommunicatorType() != comm.getCommunicatorType():
    #        raise RuntimeError(f"Tring to connect a communicator type {self.getCommunicatorType().name} with a communicator type {comm.getCommunicatorType().name}. Communicators must be of the same type.")
    #    if self.openFlag != CommunicatorOpenFlag.OPEN_OUTPUT:
    #        raise RuntimeError(f"Trying to connect the communicator {self.name} with an open input, but the current communicator has the flag {self.openFlag.name} instead of {CommunicatorOpenFlag.OPEN_OUTPUT.name}", )
    #    if comm.getCommunicatorOpenFlag() != CommunicatorOpenFlag.OPEN_INPUT:
    #        raise RuntimeError(f"Trying to connect the communicator {self.name} to {comm.getName()}, but the communicator {comm.getName()} is not an open input communicator.")
    #    self.inputPortName = comm.inputPortName
    #    self.inputTaskName = comm.inputTaskName

    #def connectOpenOutput(self, comm:Communicator) -> None:
    #    if self.getCommunicatorType() != comm.getCommunicatorType():
    #        raise RuntimeError(f"Tring to connect a communicator type {self.getCommunicatorType().name} with a communicator type {comm.getCommunicatorType().name}. Communicators must be of the same type.")
    #    if self.openFlag != CommunicatorOpenFlag.OPEN_INPUT:
    #        raise RuntimeError(f"Trying to connect the communicator {self.name} with an open output, but the current communicator has the flag {self.openFlag.name} instead of {CommunicatorOpenFlag.OPEN_INPUT.name}", )
    #    if comm.getCommunicatorOpenFlag() != CommunicatorOpenFlag.OPEN_OUTPUT:
    #        raise RuntimeError(f"Trying to connect the communicator {self.name} to {comm.getName()}, but the communicator {comm.getName()} is not an open output communicator.")
    #    self.outputPortName = comm.outputPortName
    #    self.outputTaskName = comm.outputTaskName

    def toDict(self) -> dict:
        result = super().toDict()
        result["inputPortName"] = self.inputPortName
        result["inputTaskName"] = self.inputTaskName
        result["outputPortName"] = self.outputPortName
        result["outputTaskName"] = self.outputTaskName

        return result
    
    def fromDict(self, data:dict, version:int) -> None:
        super().fromDict(data, version)

        self.inputPortName = data["inputPortName"]
        self.inputTaskName = data["inputTaskName"]
        self.outputPortName = data["outputPortName"]
        self.outputTaskName = data["outputTaskName"]
    
    def isPairedCommunicator(self) -> bool:
        return True 

class MPIPairedCommunicator(PairedCommunicator):
    def __init__(self, id: str = "defaultMPIPairedCommunicator", protocol: MPICommunicatorProtocol = MPICommunicatorProtocol.BROADCAST) -> None:
        super().__init__(id, CommunicatorTransportType.MPI)
        self.inStartRank = -1
        self.inSize = -1
        self.outStartRank = -1
        self.outSize = -1
        self.protocol = protocol

    def toDict(self) -> dict:
        result =  super().toDict()
        result["class"] = MPIPairedCommunicator.__name__
        result["inStartRank"] = self.inStartRank
        result["inSize"] = self.inSize
        result["outStartRank"] = self.outStartRank
        result["outSize"] = self.outSize
        result["mpiprotocol"] = self.protocol.name
        return result
    
    def fromDict(self, data:dict, version:int) -> None:
        if data["class"] != MPIPairedCommunicator.__name__:
            raise RuntimeError(f"Trying to parse a json class {data['class']} from the class {MPIPairedCommunicator.__name__}.")
        super().fromDict(data, version)

        self.inStartRank = data["inStartRank"]
        self.inSize = data["inSize"]
        self.outStartRank = data["outStartRank"]
        self.outSize = data["outSize"]
        self.protocol = MPICommunicatorProtocol[data["mpiprotocol"]]
    
    def setInputMPIRanks(self, start:int, size:int) -> None:
        self.inStartRank = start
        self.inSize = size

    def setOutputMPIRanks(self, start:int, size:int) -> None:
        self.outStartRank = start
        self.outSize = size

    def setMPIProtocol(self, protocol:MPICommunicatorProtocol) -> None:
        self.protocol = protocol

class GateCommunicator(Communicator):
    def __init__(self, name: str, transport: CommunicatorTransportType, side: CommunicatorGateSideFlag) -> None:
        super().__init__(name, transport)
        self.gateSide = side
        self.connectedGate = None
        self.processes = []
        self.portName = ""
        self.taskName = ""
      
    def getCommunicatorGateSide(self) -> CommunicatorGateSideFlag:
        return self.gateSide
    
    def setCommunicatorGateSide(self, side: CommunicatorGateSideFlag) -> None:
        self.gateSide = side

    def connectToGate(self, gate:GateCommunicator) -> None:
        if gate.gateSide == self.gateSide:
            raise ValueError(f"Error while trying to connect the gate {self.name} to the gate {gate.name}: cannot connect two gate with the same side.")
        if self.connectedGate is not None:
            raise ValueError(f"Trying to connect the gate {self.name} but the gate is already connected.")
        if gate.connectedGate is not None:
            raise ValueError(f"Trying to connect the gate {gate.name} but the gate is already connected.")
        self.connectedGate = gate
        gate.connectedGate = self
        
    def isConfigurable(self) -> bool:
        raise NotImplementedError("isConfigurable() function not implemented.")
    
    def isConfigured(self) -> bool:
        return self.configured
    
    def assignSenderProcesses(self, processes: List[Process]) -> None:
        if self.gateSide == CommunicatorGateSideFlag.OPEN_SENDER:
            self.processes = processes
    
    def assignReceiverProcesses(self, processes: List[Process]) -> None:
        if self.gateSide == CommunicatorGateSideFlag.OPEN_RECEIVER:
            self.processes = processes

    def getInputTaskName(self) -> str:
        if self.gateSide == CommunicatorGateSideFlag.OPEN_RECEIVER:
            return self.taskName
        else:
            return ""
    
    def getOutputTaskName(self) -> str:
        if self.gateSide == CommunicatorGateSideFlag.OPEN_SENDER:
            return self.taskName
        else:
            return ""
    
    def connectToInputPort(self, port:InputPort) -> None:
        if self.gateSide == CommunicatorGateSideFlag.OPEN_SENDER:
            raise RuntimeError(f"Trying to connect the gate {self.name} to an input port but the gate has the side OPEN_SENDER. This gate should be connected to an output port.")
        self.portName = port.getPortName()
        self.taskName = port.getTaskName()

    def connectToOutputPort(self, port:OutputPort) -> None:
        if self.gateSide == CommunicatorGateSideFlag.OPEN_RECEIVER:
            raise RuntimeError(f"Trying to connect the gate {self.name} to an output port but the gate has the side OPEN_RECEIVER. This gate should be connected to an input port.")
        self.portName = port.getPortName()
        self.taskName = port.getTaskName()

    def isSenderGate(self) -> bool:
        return self.gateSide == CommunicatorGateSideFlag.OPEN_SENDER
    
    def isReceiverGate(self) -> bool:
        return self.gateSide == CommunicatorGateSideFlag.OPEN_RECEIVER

    def isGate(self) -> bool:
        return True

    def configure(self):
        raise NotImplementedError("configure() function not implemented.")
    
    def toDict(self) -> dict:
        result =  super().toDict()
        result["gateSide"] = self.gateSide.name
        result["portName"] = self.portName
        result["taskName"] = self.taskName
        return result
    
    def fromDict(self, data:dict, version:int) -> None:
        super().fromDict(data, version)

        self.gateSide = CommunicatorGateSideFlag[data["gateSide"]]
        self.portName = data["portName"]
        self.taskName = data["taskName"]
    

class ZMQBindingSide(Enum):
    ZMQ_BIND_RECEIVER = 0,
    ZMQ_BIND_SENDER = 1

class ZMQPairedCommunicator(PairedCommunicator):
    def __init__(self, id: str = "defaultZMQPairedCommunicator", protocol: ZMQCommunicatorProtocol = ZMQCommunicatorProtocol.PUB_SUB, bindingSide: ZMQBindingSide = ZMQBindingSide.ZMQ_BIND_SENDER) -> None:
        super().__init__(name=id, transport=CommunicatorTransportType.ZMQ)
        self.protocol = protocol
        self.protocolSettings = {}
        self.bindingSide = bindingSide

    def toDict(self) -> dict:
        result =  super().toDict()
        result["class"] = ZMQPairedCommunicator.__name__
        result["zmqprotocol"] = self.protocol.name
        result["protocolSettings"] = self.protocolSettings
        return result
    
    #def connectOpenInput(self, comm:Communicator) -> None:
    #    super().connectOpenInput(comm)

    #    if self.protocol != comm.protocol:
    #        raise RuntimeError(f"Trying to connect a ZMQCommunicator protocol {self.protocol.name} with a ZMQCommunicator protocol {comm.protocol.name}. Protocols must be identical")
    #    
    #    if self.bindingSide != comm.bindingSide:
    #        raise RuntimeError(f"ZMQ communicators {self.getName()} and {comm.getName()} are not consistent on which one should bind its socket. Make sure that both communicators use the same binding side.")

    #def connectOpenOutput(self, comm:Communicator) -> None:
    #    if self.openFlag != CommunicatorOpenFlag.OPEN_INPUT:
    #        raise RuntimeError(f"Trying to connect the communicator {self.name} with an open output, but the current communicator has the flag {self.openFlag.name} instead of {CommunicatorOpenFlag.OPEN_INPUT.name}", )
    #    if comm.getCommunicatorOpenFlag() != CommunicatorOpenFlag.OPEN_OUTPUT:
    #        raise RuntimeError(f"Trying to connect the communicator {self.name} to {comm.getName()}, but the communicator {comm.getName()} is not an open output communicator.")
    #    self.outputPortName = comm.outputPortName
    #    self.outputTaskName = comm.outputTaskName

    def setZMQProtocol(self, protocol:MPICommunicatorProtocol) -> None:
        self.protocol = protocol

    def isConfigurable(self) -> bool:

        # That gate is already configured, nothing else to check
        if self.configured:
            return True
        
        if (self.protocol == ZMQCommunicatorProtocol.PUB_SUB or self.protocol == ZMQCommunicatorProtocol.PUSH_PULL):

            if len(self.senderProcesses) == 1 and len(self.receiverProcesses) == 1:
                return True
            
        return False

    def configure(self):
        ##if (self.openFlag == CommunicatorOpenFlag.OPEN_OUTPUT or  self.openFlag == CommunicatorOpenFlag.CLOSED ) and len(outputProcesses) != 1:
        ##    raise RuntimeError("The ZMQ communicator {} has an output but only 1 process output is supported ({} detected.)", self.name, len(outputProcesses))

        ##if (self.openFlag == CommunicatorOpenFlag.OPEN_INPUT or  self.openFlag == CommunicatorOpenFlag.CLOSED ) and len(inputProcesses) != 1:
        ##    raise RuntimeError("The ZMQ communicator {} has an input but only 1 process input is supported ({} detected.)", self.name, len(outputProcesses))
        if len(self.receiverProcesses) != 1:
            raise RuntimeError("The ZMQ communicator {} has an input but only 1 process input is supported ({} detected.)", self.name, len(self.receiverProcesses))
            
        if len(self.senderProcesses) != 1:
            raise RuntimeError("The ZMQ communicator {} has an output but only 1 process output is supported ({} detected.)", self.name, len(self.senderProcesses))

        if self.protocol == ZMQCommunicatorProtocol.PUB_SUB:
            self.protocolSettings["port"] = 50000
            self.protocolSettings["bindingside"] = self.bindingSide.name
            if self.bindingSide == ZMQBindingSide.ZMQ_BIND_SENDER:
                self.protocolSettings["addr"] = self.senderProcesses[0].hostname
            else:
                self.protocolSettings["addr"] = self.receiverProcesses[0].hostname
        elif self.protocol == ZMQCommunicatorProtocol.PUSH_PULL:
            self.protocolSettings["port"] = 50000
            self.protocolSettings["bindingside"] = self.bindingSide.name
            if self.bindingSide == ZMQBindingSide.ZMQ_BIND_SENDER:
                self.protocolSettings["addr"] = self.senderProcesses[0].hostname
            else:
                self.protocolSettings["addr"] = self.receiverProcesses[0].hostname
        else:
            raise NotImplementedError("The requested ZMQ protocol is currently not supported.")
    
class ZMQGateCommunicator(GateCommunicator):
    def __init__(self, name: str = "defaultZMQGateCommunicator", side: CommunicatorGateSideFlag = CommunicatorGateSideFlag.OPEN_SENDER, protocol: ZMQCommunicatorProtocol = ZMQCommunicatorProtocol.PUB_SUB, bindingSide: ZMQBindingSide = ZMQBindingSide.ZMQ_BIND_SENDER) -> None:
        super().__init__(name, transport = CommunicatorTransportType.ZMQ, side = side)
        self.protocol = protocol
        self.protocolSettings = {}
        self.bindingSide = bindingSide

    def toDict(self) -> dict:
        result =  super().toDict()
        result["class"] = ZMQGateCommunicator.__name__
        result["zmqprotocol"] = self.protocol.name
        result["protocolSettings"] = self.protocolSettings
        return result
    
    def fromDict(self, data:dict, version:int) -> None:
        super().fromDict(data, version)

        self.protocol = ZMQCommunicatorProtocol[data["zmqprotocol"]]
        self.protocolSettings = data["protocolSettings"]
        self.bindingSide = ZMQBindingSide[data["protocolSettings"]["bindingside"]]

    
    def setZMQProtocol(self, protocol:MPICommunicatorProtocol) -> None:
        if self.configured:
            raise RuntimeError("Chanding the ZMQ protocol is not allowed once the ZMQGateCommunicator is configured.")
        self.protocol = protocol

    def connectToGate(self, gate:GateCommunicator) -> None:
        # Will check that the directions are compatible
        super().connectToGate(gate)
        if not isinstance(gate, ZMQGateCommunicator):
            raise ValueError(f"Trying to connect the gate {self.getName()} and {gate.getName()} but they are not of the same type.")
        
        if self.protocol != gate.protocol:
            raise ValueError(f"Trying to connect the ZMQ gate {self.getName()} and {gate.getName()} but they do not have the same protocol.")
        
        if self.bindingSide != gate.bindingSide:
            raise ValueError(f"Trying to connect the ZMQ gate {self.getName()} and {gate.getName()} but they do not agree on which side should bind the socket.")
        
    def isConfigurable(self) -> bool:

        # That gate is already configured, nothing else to check
        if self.configured:
            return True
        
        if (self.protocol == ZMQCommunicatorProtocol.PUB_SUB or self.protocol == ZMQCommunicatorProtocol.PUSH_PULL):

            # Check if this gate is the binding side and the list of processes is available. If yes, then it can always be configured. 
            # The list of processes is necessary to determine the address of the socket to bind.
            # If no, it is configurable only if the other gate is configurable.
            if len(self.processes) != 1:
                print(f"The ZMQ comm {self.name} has processes attached to it. Not configurable.")
                return False
            if self.isBindingSide():
                print(f"The ZMQ comm {self.name} is the sending side. Configurable.")
                return True
            else:
                print(f"The ZMQ comm {self.name} is NOT the sending side.")
            
            # At this point, this gate is not the binding side, so the address will come from the other gate. 
            # Checking that the other gate is configured
            if self.connectedGate is not None and self.connectedGate.isConfigurable():
                return True
            
            return False
        
        # 

        return False
    
    def isConfigured(self) -> bool:
        return self.configured

    def configure(self):
        if self.configured:
            return
        if (self.protocol == ZMQCommunicatorProtocol.PUB_SUB or self.protocol == ZMQCommunicatorProtocol.PUSH_PULL):
            if len(self.processes) != 1:
                raise RuntimeError(f"Unable to configure the {self.name} ZMQGateCommunicator because the number of processes assigned to the task {self.taskName} is different than 1.")

            # Check if this gate is the binding side and the list of processes is available. If yes, then it can always be configured by itself. 
            # The list of processes is necessary to determine the address of the socket to bind.
            # If no, it is configurable only if the other gate is configurable. This is because the binding side controls the address used by the communicator.
            if self.isBindingSide():
                self.protocolSettings["addr"] = self.processes[0].hostname
                self.protocolSettings["port"] = 50000
                self.protocolSettings["bindingside"] = self.bindingSide.name
            else:
                # Can't configure from this side, the other side needs to be configured first
                if self.connectedGate is None:
                    raise RuntimeError(f"Trying to configure the {self.name} ZMQGateCommunicator but it can't be configured without another gate connected to it.")
                if not self.connectedGate.isConfigurable():
                    raise RuntimeError(f"Trying to configure the {self.name} ZMQGateCommunicator because the connected gate {self.connectedGate.getName()} cannot be configured either.")
                
                if not self.connectedGate.isConfigured():
                    self.connectedGate.configure()

                # At this point, the other side is configured, we can get the address for the communicator.
                self.protocolSettings = self.connectedGate.protocolSettings

        else:
            raise NotImplementedError(f"The configuration for the protocol {self.protocol.name} is not currently supported.")
        
        # Flag the communicator as configured now that the socket settings are set
        self.configured = True
        
    def isValid(self):
        return self.portName != "" and self.taskName != ""
    
    def isBindingSide(self):
        return (self.bindingSide == ZMQBindingSide.ZMQ_BIND_RECEIVER and self.gateSide == CommunicatorGateSideFlag.OPEN_RECEIVER) or (self.bindingSide == ZMQBindingSide.ZMQ_BIND_SENDER and self.gateSide == CommunicatorGateSideFlag.OPEN_SENDER)
    
        

class CommunicatorFactory():
    def __init__(self) -> None:
            pass

    def jsonToCommunicator(self, data:dict, version:int=0):
        commConversion = {}
        commConversion[MPIPairedCommunicator.__name__] = MPIPairedCommunicator()
        commConversion[ZMQPairedCommunicator.__name__] = ZMQPairedCommunicator()
        commConversion[ZMQGateCommunicator.__name__] = ZMQGateCommunicator()
        

        if "class" not in data.keys():
            raise RuntimeError("Unable to find class in dictionary while attempting to parse a Communicator.")
        commClass = data["class"]
        if commClass not in commConversion.keys():
            raise RuntimeError(f"Unknown Communicator class {commClass}. Available classes: {commConversion}")
        commObject = copy.deepcopy(commConversion[commClass])
        print(f"Importing an object of class {commClass} from the factory.")
        commObject.fromDict(data, version)

        return commObject