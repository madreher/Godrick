import os
from pathlib import Path

from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection

def test_singleTaskSingleHostWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCollection(name="myCluster")
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

def test_singleTaskMultipleHostWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
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

    raise RuntimeError("TEST2")

def test_multipleTaskMultipleHostWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    
    # Split the cluster 
    partitions = cluster.selectNodesByRange([1, 2])

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.addTask(task=task1)
    workflow.addTask(task=task2)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    raise RuntimeError("TEST3")

def test_multipleTaskMultipleHostSplitCoresWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    
    # Split the cluster 
    partitions = cluster.splitNodesByCoreRange([1,3]) # assign 1 core per node for task1, and 3 cores per node for task2

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.addTask(task=task1)
    workflow.addTask(task=task2)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    raise RuntimeError("TEST3")