from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import MPICommunicator

import os
from pathlib import Path

def main():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/localhost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    workflow = Workflow("MPIBroadcastWorkflow")

    partitions = cluster.splitNodesByCoreRange([1, 3])

    task1 = MPITask(name="send", cmdline="bin/send --name send --config config.MPIBroadcastWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task1.setResources(partitions[0])
    task2 = MPITask(name="receive", cmdline="bin/receive --name receive --config config.MPIBroadcastWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")
    task2.setResources(partitions[1])

    comm1 = MPICommunicator("myComm")
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