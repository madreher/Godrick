from godrick.workflow import Workflow
from godrick.launcher import MainLauncher
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.computeResources import ComputeCollection
from godrick.communicator import ZMQCommunicator, ZMQCommunicatorProtocol

import os
from pathlib import Path
import json

def test_ZMQCommunicator():
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    workflow = Workflow("MPIBroadcastWorkflow")
    partitions = cluster.splitNodesByCoreRange([1, 1])

    task1 = MPITask(name="send", cmdline="bin/send --name send --config config.MPIBroadcastWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task1.setResources(partitions[0])
    task2 = MPITask(name="receive", cmdline="bin/receive --name receive --config config.MPIBroadcastWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")
    task2.setResources(partitions[1])

    comm1 = ZMQCommunicator(id="myComm", protocol=ZMQCommunicatorProtocol.PUB_SUB)
    comm1.connectInput(task2.getInputPort("in"))
    comm1.connectOutput(task1.getOutputPort("out"))

    workflow.declareTask(task1)
    workflow.declareTask(task2)
    workflow.declareCommunicator(comm1)

    launcher = MainLauncher()
    launcher.generateOutputFiles(workflow=workflow)

    configFile = Path(workflow.getConfigurationFile())
    assert configFile.is_file()
    with open(configFile) as f:
        doc = f.read()
        data = json.loads(doc)

        # Check the data for the communicator 
        assert "communicators" in data.keys()
        assert len(data["communicators"]) == 1

        
        commDict = data["communicators"][0]
        assert commDict["name"] == "myComm"
        assert commDict["type"] == "ZMQ"
        assert commDict["zmqprotocol"] == ZMQCommunicatorProtocol.PUB_SUB.name
        assert commDict["inputPortName"] == "in"
        assert commDict["inputTaskName"] == "receive"
        assert commDict["outputPortName"] == "out"
        assert commDict["outputTaskName"] == "send"
        assert commDict["protocolSettings"]["pubaddr"] == "machine1"
        assert commDict["protocolSettings"]["pubport"] == 50000

    launcher.removeFiles()
