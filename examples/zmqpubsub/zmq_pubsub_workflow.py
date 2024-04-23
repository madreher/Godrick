from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import ZMQPairedCommunicator, ZMQCommunicatorProtocol

import os
from pathlib import Path

def main():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/localhost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    workflow = Workflow("ZMQPubSubWorkflow")

    partitions = cluster.splitNodesByCoreRange([1, 1])

    task1 = MPITask(name="sendpubsub", cmdline="bin/sendpubsub --name sendpubsub --config config.ZMQPubSubWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task1.setResources(partitions[0])
    task2 = MPITask(name="receivepubsub", cmdline="bin/receivepubsub --name receivepubsub --config config.ZMQPubSubWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")
    task2.setResources(partitions[1])

    comm1 = ZMQPairedCommunicator("myComm", protocol=ZMQCommunicatorProtocol.PUB_SUB)
    comm1.connectToInputPort(task2.getInputPort("in"))
    comm1.connectToOutputPort(task1.getOutputPort("out"))

    workflow.declareTask(task1)
    workflow.declareTask(task2)
    workflow.declareCommunicator(comm1)

    launcher = MainLauncher()
    launcher.generateOutputFiles(workflow=workflow)


# Boilerplate name guard
if __name__ == "__main__":
    main()