from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import ZMQGateCommunicator, CommunicatorGateSideFlag, ZMQBindingSide, CommunicatorTransportType, ZMQCommunicatorProtocol

import os
from pathlib import Path
import json

def test_ZMQExternalGate():
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create the first workflow
    workflow1 = Workflow("ZMQGateWorkflow1")
    partitions = cluster.splitNodesByCoreRange([1, 1])

    task1 = MPITask(name="send", cmdline="bin/send --name send --config config.ZMQGateWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task1.setResources(partitions[0])

    gateSender = ZMQGateCommunicator(name="senderSide", side=CommunicatorGateSideFlag.OPEN_SENDER, bindingSide=ZMQBindingSide.ZMQ_BIND_SENDER)
    gateSender.connectToOutputPort(task1.getOutputPort("out"))

    workflow1.declareTask(task1)
    workflow1.declareCommunicator(gateSender)
    launcher1 = MainLauncher()
    launcher1.generateOutputFiles(workflow=workflow1)

    externalWorkflow = Workflow()
    externalWorkflow.initFromGatesConfigFile(Path(workflow1.getGatesFile()))

    # Load the first workflow as if it was defined somewhere else
    externalGates = externalWorkflow.getGateCommunicators()
    assert len(externalGates) == 1
    
    # Create the second workflow
    workflow2 = Workflow("ZMQGateWorkflow2")
    task2 = MPITask(name="receive", cmdline="bin/receive --name receive --config config.ZMQGateWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")
    task2.setResources(partitions[1])
    gateReceiver = ZMQGateCommunicator(name="receiverSide", side=CommunicatorGateSideFlag.OPEN_RECEIVER, bindingSide=ZMQBindingSide.ZMQ_BIND_SENDER)
    gateReceiver.connectToInputPort(task2.getInputPort("in"))

    gateReceiver.connectToGate(externalGates[0])
    workflow2.declareTask(task2)
    workflow2.declareCommunicator(gateReceiver)
    
    launcher2 = MainLauncher()
    launcher2.generateOutputFiles(workflow=workflow2)

    configFile = Path(workflow2.getConfigurationFile())
    assert configFile.is_file()

    with open(configFile) as f:
        data = json.load(f)

        assert "communicators" in data.keys()
        assert "tasks" in data.keys()

        assert len(data["communicators"]) == 1

        commDict = data["communicators"][0]
        assert commDict["name"] == "receiverSide"
        assert commDict["transport"] == CommunicatorTransportType.ZMQ.name
        assert commDict["configured"] == True
        assert commDict["gateSide"] == CommunicatorGateSideFlag.OPEN_RECEIVER.name
        assert commDict["portName"] == "in"
        assert commDict["taskName"] == "receive"
        assert commDict["class"] == ZMQGateCommunicator.__name__
        assert commDict["zmqprotocol"] == ZMQCommunicatorProtocol.PUB_SUB.name
        assert commDict["protocolSettings"]["addr"] == 'machine1'
        assert commDict["protocolSettings"]["port"] == 50000
        assert commDict["protocolSettings"]["bindingside"] == ZMQBindingSide.ZMQ_BIND_SENDER.name

    launcher1.removeFiles()
    launcher2.removeFiles()

    