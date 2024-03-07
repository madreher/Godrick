from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection

import os
from pathlib import Path

def main():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/localhost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    workflow = Workflow("SimpleMPIWorkflow")

    partitions = cluster.splitNodesByCoreRange([1, 3])

    task1 = MPITask(name="task1", cmdline="bin/task --name task1 --config config.SimpleMPIWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.setResources(partitions[0])
    task2 = MPITask(name="task2", cmdline="bin/task --name task2 --config config.SimpleMPIWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.setResources(partitions[1])

    workflow.addTask(task1)
    workflow.addTask(task2)

    launcher = MainLauncher()
    launcher.generateOutputFiles(workflow=workflow)


# Boilerplate name guard
if __name__ == "__main__":
    main()