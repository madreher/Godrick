from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import ZMQCommunicator, ZMQCommunicatorProtocol

import os
from pathlib import Path

def main():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/localhost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    workflow = Workflow("ZMQPushPullWorkflow")

    partitions = cluster.splitNodesByCoreRange([1, 1])

    task1 = MPITask(name="sendpushpull", cmdline="bin/sendpushpull --name sendpushpull --config config.ZMQPushPullWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task1.setResources(partitions[0])
    task2 = MPITask(name="receivepushpull", cmdline="bin/receivepushpull --name receivepushpull --config config.ZMQPushPullWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")
    task2.setResources(partitions[1])

    comm1 = ZMQCommunicator("myComm", protocol=ZMQCommunicatorProtocol.PUSH_PULL)
    comm1.connectInput(task2.getInputPort("in"))
    comm1.connectOutput(task1.getOutputPort("out"))

    workflow.declareTask(task1)
    workflow.declareTask(task2)
    workflow.declareCommunicator(comm1)

    launcher = MainLauncher()
    launcher.generateOutputFiles(workflow=workflow)


# Boilerplate name guard
if __name__ == "__main__":
    main()