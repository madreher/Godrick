import os
from pathlib import Path
import uuid

from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import MPIPairedCommunicator, MPICommunicatorProtocol

def test_singleTaskSingleHostWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow1")

    # Create a task and assign resources to it
    task = MPITask(name="testTask", cmdline="myExecutable --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task.setResources(cluster)

    # Add the task to the workflow
    workflow.declareTask(task=task)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    # Check that the files exist
    rankfilePath = Path("rankfile.MyWorkflow1.txt")
    assert rankfilePath.is_file()
    with open(rankfilePath, "r") as f:
        content = f.read()
        assert content == """rank 0=machine1 slots=0
rank 1=machine1 slots=1
rank 2=machine1 slots=2
rank 3=machine1 slots=3
"""
    hostfilePath = Path("hostfile.MyWorkflow1.txt")
    assert hostfilePath.is_file()
    with open(hostfilePath, "r") as f:
        content = f.read()
        assert content == """machine1
machine1
machine1
machine1
"""
    commandfilePath = Path("launch.MyWorkflow1.sh")
    assert commandfilePath.is_file()
    with open(commandfilePath, "r") as f:
        content = f.read()
        assert content == """#! /bin/bash

mpirun --hostfile hostfile.MyWorkflow1.txt --rankfile rankfile.MyWorkflow1.txt  -np 4 myExecutable --args 1"""

    # Cleanup the files after testing
    launcher.removeFiles()

def test_singleTaskMultipleHostWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow2")

    # Create a task and assign resources to it
    task = MPITask(name="testTask", cmdline="myExecutable --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task.setResources(cluster)

    # Add the task to the workflow
    workflow.declareTask(task=task)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    # Check that the files exist
    rankfilePath = Path("rankfile.MyWorkflow2.txt")
    assert rankfilePath.is_file()
    with open(rankfilePath, "r") as f:
        content = f.read()
        assert content == """rank 0=machine1 slots=0
rank 1=machine1 slots=1
rank 2=machine1 slots=2
rank 3=machine1 slots=3
rank 4=machine2 slots=0
rank 5=machine2 slots=1
rank 6=machine2 slots=2
rank 7=machine2 slots=3
rank 8=machine3 slots=0
rank 9=machine3 slots=1
rank 10=machine3 slots=2
rank 11=machine3 slots=3
"""
    hostfilePath = Path("hostfile.MyWorkflow2.txt")
    assert hostfilePath.is_file()
    with open(hostfilePath, "r") as f:
        content = f.read()
        assert content == """machine1
machine1
machine1
machine1
machine2
machine2
machine2
machine2
machine3
machine3
machine3
machine3
"""
    commandfilePath = Path("launch.MyWorkflow2.sh")
    assert commandfilePath.is_file()
    with open(commandfilePath, "r") as f:
        content = f.read()
        assert content == """#! /bin/bash

mpirun --hostfile hostfile.MyWorkflow2.txt --rankfile rankfile.MyWorkflow2.txt  -np 12 myExecutable --args 1"""

    # Cleanup the files after testing
    launcher.removeFiles()

def test_multipleTaskMultipleHostWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow3")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    
    # Split the cluster 
    partitions = cluster.selectNodesByRange([1, 2])

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.declareTask(task=task1)
    workflow.declareTask(task=task2)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    # Check that the files exist
    rankfilePath = Path("rankfile.MyWorkflow3.txt")
    assert rankfilePath.is_file()
    with open(rankfilePath, "r") as f:
        content = f.read()
        assert content == """rank 0=machine1 slots=0
rank 1=machine1 slots=1
rank 2=machine1 slots=2
rank 3=machine1 slots=3
rank 4=machine2 slots=0
rank 5=machine2 slots=1
rank 6=machine2 slots=2
rank 7=machine2 slots=3
rank 8=machine3 slots=0
rank 9=machine3 slots=1
rank 10=machine3 slots=2
rank 11=machine3 slots=3
"""
    hostfilePath = Path("hostfile.MyWorkflow3.txt")
    assert hostfilePath.is_file()
    with open(hostfilePath, "r") as f:
        content = f.read()
        assert content == """machine1
machine1
machine1
machine1
machine2
machine2
machine2
machine2
machine3
machine3
machine3
machine3
"""
    commandfilePath = Path("launch.MyWorkflow3.sh")
    assert commandfilePath.is_file()
    with open(commandfilePath, "r") as f:
        content = f.read()
        assert content == """#! /bin/bash

mpirun --hostfile hostfile.MyWorkflow3.txt --rankfile rankfile.MyWorkflow3.txt  -np 4 myExecutable1 --args 1 : -np 8 myExecutable2 --args 2"""

    # Cleanup the files after testing
    launcher.removeFiles()

def test_multipleTaskMultipleHostSplitCoresWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow4")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    
    # Split the cluster 
    partitions = cluster.splitNodesByCoreRange([1,3]) # assign 1 core per node for task1, and 3 cores per node for task2

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.declareTask(task=task1)
    workflow.declareTask(task=task2)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    # Check that the files exist
    rankfilePath = Path("rankfile.MyWorkflow4.txt")
    assert rankfilePath.is_file()
    with open(rankfilePath, "r") as f:
        content = f.read()
        assert content == """rank 0=machine1 slots=0
rank 1=machine2 slots=0
rank 2=machine3 slots=0
rank 3=machine1 slots=1
rank 4=machine1 slots=2
rank 5=machine1 slots=3
rank 6=machine2 slots=1
rank 7=machine2 slots=2
rank 8=machine2 slots=3
rank 9=machine3 slots=1
rank 10=machine3 slots=2
rank 11=machine3 slots=3
"""
    hostfilePath = Path("hostfile.MyWorkflow4.txt")
    assert hostfilePath.is_file()
    with open(hostfilePath, "r") as f:
        content = f.read()
        assert content == """machine1
machine2
machine3
machine1
machine1
machine1
machine2
machine2
machine2
machine3
machine3
machine3
"""
    commandfilePath = Path("launch.MyWorkflow4.sh")
    assert commandfilePath.is_file()
    with open(commandfilePath, "r") as f:
        content = f.read()
        assert content == """#! /bin/bash

mpirun --hostfile hostfile.MyWorkflow4.txt --rankfile rankfile.MyWorkflow4.txt  -np 3 myExecutable1 --args 1 : -np 9 myExecutable2 --args 2"""

    # Cleanup the files after testing
    launcher.removeFiles()

def test_multipleTaskMultipleHostPerSocketWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow5")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERSOCKET)
    
    # Split the cluster 
    partitions = cluster.splitNodesByCoreRange([1,3]) # assign 1 core per node for task1, and 3 cores per node for task2

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.declareTask(task=task1)
    workflow.declareTask(task=task2)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    # Check that the files exist
    rankfilePath = Path("rankfile.MyWorkflow5.txt")
    assert rankfilePath.is_file()
    with open(rankfilePath, "r") as f:
        content = f.read()
        assert content == """rank 0=machine1 slots=0
rank 1=machine2 slots=0
rank 2=machine3 slots=0
rank 3=machine1 slots=1,2,3
rank 4=machine2 slots=1,2,3
rank 5=machine3 slots=1,2,3
"""
    hostfilePath = Path("hostfile.MyWorkflow5.txt")
    assert hostfilePath.is_file()
    with open(hostfilePath, "r") as f:
        content = f.read()
        assert content == """machine1
machine2
machine3
machine1
machine1
machine1
machine2
machine2
machine2
machine3
machine3
machine3
"""
    commandfilePath = Path("launch.MyWorkflow5.sh")
    assert commandfilePath.is_file()
    with open(commandfilePath, "r") as f:
        content = f.read()
        assert content == """#! /bin/bash

mpirun --hostfile hostfile.MyWorkflow5.txt --rankfile rankfile.MyWorkflow5.txt  -np 3 myExecutable1 --args 1 : -np 3 myExecutable2 --args 2"""

    # Cleanup the files after testing
    launcher.removeFiles()

def test_multipleTaskMultipleHostPerNodeWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow6")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERNODE)
    
    # Split the cluster 
    partitions = cluster.splitNodesByCoreRange([1,3]) # assign 1 core per node for task1, and 3 cores per node for task2

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.declareTask(task=task1)
    workflow.declareTask(task=task2)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    # Check that the files exist
    rankfilePath = Path("rankfile.MyWorkflow6.txt")
    assert rankfilePath.is_file()
    with open(rankfilePath, "r") as f:
        content = f.read()
        assert content == """rank 0=machine1 slots=0
rank 1=machine2 slots=0
rank 2=machine3 slots=0
rank 3=machine1 slots=1,2,3
rank 4=machine2 slots=1,2,3
rank 5=machine3 slots=1,2,3
"""
    hostfilePath = Path("hostfile.MyWorkflow6.txt")
    assert hostfilePath.is_file()
    with open(hostfilePath, "r") as f:
        content = f.read()
        assert content == """machine1
machine2
machine3
machine1
machine1
machine1
machine2
machine2
machine2
machine3
machine3
machine3
"""
    commandfilePath = Path("launch.MyWorkflow6.sh")
    assert commandfilePath.is_file()
    with open(commandfilePath, "r") as f:
        content = f.read()
        assert content == """#! /bin/bash

mpirun --hostfile hostfile.MyWorkflow6.txt --rankfile rankfile.MyWorkflow6.txt  -np 3 myExecutable1 --args 1 : -np 3 myExecutable2 --args 2"""

    # Cleanup the files after testing
    launcher.removeFiles()

def test_differentFolderWorkflow():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create a temperaryFolder 
    folder = Path("/tmp") / str(uuid.uuid4())
    folder.mkdir()

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow7")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERNODE)
    
    # Split the cluster 
    partitions = cluster.splitNodesByCoreRange([1,3]) # assign 1 core per node for task1, and 3 cores per node for task2

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.declareTask(task=task1)
    workflow.declareTask(task=task2)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow, folder=folder)

    # Check that the files exist
    rankfilePath = folder / Path("rankfile.MyWorkflow7.txt")
    assert rankfilePath.is_file()
    with open(rankfilePath, "r") as f:
        content = f.read()
        assert content == """rank 0=machine1 slots=0
rank 1=machine2 slots=0
rank 2=machine3 slots=0
rank 3=machine1 slots=1,2,3
rank 4=machine2 slots=1,2,3
rank 5=machine3 slots=1,2,3
"""
    hostfilePath = folder / Path("hostfile.MyWorkflow7.txt")
    assert hostfilePath.is_file()
    with open(hostfilePath, "r") as f:
        content = f.read()
        assert content == """machine1
machine2
machine3
machine1
machine1
machine1
machine2
machine2
machine2
machine3
machine3
machine3
"""
    commandfilePath = folder / Path("launch.MyWorkflow7.sh")
    assert commandfilePath.is_file()
    with open(commandfilePath, "r") as f:
        content = f.read()
        assert content == """#! /bin/bash

mpirun --hostfile hostfile.MyWorkflow7.txt --rankfile rankfile.MyWorkflow7.txt  -np 3 myExecutable1 --args 1 : -np 3 myExecutable2 --args 2"""

    # Cleanup the files after testing
    launcher.removeFiles()

def test_multipleTaskMultipleHostWorkflowReload():
    # Create resources
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/triplehost.txt")
    cluster = ComputeCollection(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    # Create an empty workflow
    workflow = Workflow(name="MyWorkflow8")

    # Create two tasks 
    task1 = MPITask(name="testTask1", cmdline="myExecutable1 --args 1", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task1.addOutputPort("out")
    task2 = MPITask(name="testTask2", cmdline="myExecutable2 --args 2", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
    task2.addInputPort("in")

    myComm = MPIPairedCommunicator(id="mycomm", protocol=MPICommunicatorProtocol.PARTIAL_BCAST_GATHER)
    myComm.connectToInputPort(task2.getInputPort("in"))
    myComm.connectToOutputPort(task1.getOutputPort("out"))
    
    # Split the cluster 
    partitions = cluster.selectNodesByRange([1, 2])

    # Assign the resources to the tasks
    task1.setResources(partitions[0])
    task2.setResources(partitions[1])


    # Add the task to the workflow
    workflow.declareTask(task=task1)
    workflow.declareTask(task=task2)
    workflow.declareCommunicator(myComm)

    # Create a launcher
    launcher = MainLauncher()

    # Generate the outputs for the workflow
    launcher.generateOutputFiles(workflow=workflow)

    # Create a new empty workflow and load the previous configuration
    workflow2 = Workflow()
    workflow2.initFromWorkflowConfigFile(Path(workflow.getConfigurationFile()))

    communicators = workflow2.getCommunicators()
    assert len(communicators) == 1

    assert communicators[0].toDict() == myComm.toDict()
    tasks = workflow2.getTasks()
    assert len(tasks) == 2
    assert tasks[0].toDict() == task1.toDict()
    assert tasks[1].toDict() == task2.toDict()


    # Cleanup the files after testing
    launcher.removeFiles()