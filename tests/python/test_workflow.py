import os
from pathlib import Path

from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCluster

def test_singleTaskWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCluster(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow")

    # Create a task and assign resources to it
    task = MPITask(name="testTask", cmdline="myExecutable --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task.setResources(cluster)

    # Add the task to the workflow
    workflow.addTask(task=task)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    raise RuntimeError("TEST")