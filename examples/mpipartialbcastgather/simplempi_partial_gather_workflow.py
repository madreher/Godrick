from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import MPICommunicator, MPICommunicatorProtocol

import os
from pathlib import Path

def main():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/localhost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    workflow = Workflow("MPIPartialGatherWorkflow")

    partitions = cluster.splitNodesByCoreRange([3, 1])

    task1 = MPITask(name="sendPartial", cmdline=f"bin/sendPartial --name sendPartial --config {workflow.getConfigurationFile()}", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task1.setResources(partitions[0])
    task2 = MPITask(name="receivePartial", cmdline=f"bin/receivePartial --name receivePartial --config {workflow.getConfigurationFile()}", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")
    task2.setResources(partitions[1])

    comm1 = MPICommunicator(id="myComm", protocol=MPICommunicatorProtocol.PARTIAL_BCAST_GATHER)
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