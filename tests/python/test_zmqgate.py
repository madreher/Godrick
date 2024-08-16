from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import ZMQGateCommunicator, CommunicatorGateSideFlag, ZMQBindingSide, CommunicatorTransportType, ZMQCommunicatorProtocol

import os
from pathlib import Path
import json

def test_ZMQGateCommunicator():
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    workflow = Workflow("ZMQGateWorkflow")
    partitions = cluster.splitNodesByCoreRange([1, 1])

    task1 = MPITask(name="send", cmdline="bin/send --name send --config config.ZMQGateWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task1.setResources(partitions[0])
    task2 = MPITask(name="receive", cmdline="bin/receive --name receive --config config.ZMQGateWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")
    task2.setResources(partitions[1])

    gateSender = ZMQGateCommunicator(name="senderSide", side=CommunicatorGateSideFlag.OPEN_SENDER, bindingSide=ZMQBindingSide.ZMQ_BIND_SENDER)
    gateSender.connectToOutputPort(task1.getOutputPort("out"))
    gateReceiver = ZMQGateCommunicator(name="receiverSide", side=CommunicatorGateSideFlag.OPEN_RECEIVER, bindingSide=ZMQBindingSide.ZMQ_BIND_SENDER, nonblocking=True)
    gateReceiver.connectToInputPort(task2.getInputPort("in"))

    gateSender.connectToGate(gateReceiver)

    workflow.declareTask(task1)
    workflow.declareTask(task2)
    workflow.declareCommunicator(gateSender)
    workflow.declareCommunicator(gateReceiver)

    launcher = MainLauncher()
    launcher.generateOutputFiles(workflow=workflow)

    configFile = Path(workflow.getConfigurationFile())
    assert configFile.is_file()

    with open(configFile) as f:
        doc = f.read()
        data = json.loads(doc)

        # Check the data for the communicator 
        assert "communicators" in data.keys()
        assert len(data["communicators"]) == 2

        for commDict in data["communicators"]:
            assert commDict["name"] == "senderSide" or commDict["name"] == "receiverSide"
            assert commDict["transport"] == CommunicatorTransportType.ZMQ.name
            assert commDict["class"] == ZMQGateCommunicator.__name__
            assert commDict["configured"] == True
            assert commDict["zmqprotocol"] == ZMQCommunicatorProtocol.PUB_SUB.name
            assert commDict["protocolSettings"]["addr"] == "machine1"
            assert commDict["protocolSettings"]["port"] == 50000
            assert commDict["protocolSettings"]["bindingside"] == ZMQBindingSide.ZMQ_BIND_SENDER.name
            if commDict["name"] == "senderSide":
                assert commDict["nonblocking"] == False
            else:
                assert commDict["nonblocking"] == True

    gateFile = Path(workflow.getGatesFile())
    assert gateFile.is_file()
    with open(gateFile) as f:
        doc = f.read()
        data = json.loads(doc)

        assert "gates" in data.keys()
        assert len(data["gates"]) == 2

        for commDict in data["gates"]:
            assert commDict["name"] == "senderSide" or commDict["name"] == "receiverSide"
            assert commDict["transport"] == CommunicatorTransportType.ZMQ.name
            assert commDict["class"] == ZMQGateCommunicator.__name__
            assert commDict["configured"] == True
            assert commDict["zmqprotocol"] == ZMQCommunicatorProtocol.PUB_SUB.name
            assert commDict["protocolSettings"]["addr"] == "machine1"
            assert commDict["protocolSettings"]["port"] == 50000
            assert commDict["protocolSettings"]["bindingside"] == ZMQBindingSide.ZMQ_BIND_SENDER.name
            if commDict["name"] == "senderSide":
                assert commDict["nonblocking"] == False
            else:
                assert commDict["nonblocking"] == True
    launcher.removeFiles()