from godrick.workflow import Workflow
from godrick.task import TaskType, Task, MPIPlacementPolicy
from godrick.communicator import CommunicatorType
from typing import Tuple
from pathlib import Path

class OpenMPILauncher():
    def __init__(self) -> None:
        pass

    def generateOutputFiles(self, workflow:Workflow, folder:Path = None):
        tasks = workflow.getTasks()
        if len(tasks) == 0:
            raise RuntimeError("Attempting to generate commands from an empty worklow. Abording.")
        
        rankfileName = f"rankfile.{workflow.getName()}.txt"
        hostfileName = f"hostfile.{workflow.getName()}.txt"
        commandfileName = f"launch.{workflow.getName()}.sh"

        mpirunCommand = f"mpirun --hostfile {hostfileName} --rankfile {rankfileName} "
        rankfileContent = ""
        hostfileContent = ""
        rankOffset = 0

        # Process the tasks
        for i, task in enumerate(tasks):
            if task.getTaskType() != TaskType.MPI:
                raise NotImplementedError("Only MPI tasks are supported for now.")
            resource = task.getResources()
            if resource is None:
                raise ValueError(f"The task {task.getName()} does have resources assigned to it.")

            if task.getTaskType() != TaskType.MPI:
                raise RuntimeError(f"Trying to launch a non-mpi task with the mpi launcher.")
            
            # Variables to tracks the MPI ranks of the task
            startRank = rankOffset

            (hostfile, rankfile, cmd, newOffset) = self.appendMPITask(task, rankOffset)
            hostfileContent += hostfile
            rankfileContent += rankfile
            if i == 0:
                mpirunCommand += cmd
            else:
                mpirunCommand += f" :{cmd}"
            rankOffset = newOffset
            sizeRank = newOffset - startRank
            
            # Flag the task as been processed
            task.setGlobalRanks(startRank, sizeRank)
            task.markAsProcessed()

        # Process the communicators
        for i, comm in enumerate(workflow.getCommunicators()):
            if comm.getCommunicatorType() != CommunicatorType.MPI:
                raise NotImplementedError("Only MPI communicators are supported for now.")
            
            inputTask = workflow.getTaskByName(comm.getInputTaskName())
            comm.setInputMPIRanks(inputTask.getGlobalStartRank(), inputTask.getGlobalNbRank())

            outputTask = workflow.getTaskByName(comm.getOutputTaskName())
            comm.setOutputMPIRanks(outputTask.getGlobalStartRank(), outputTask.getGlobalNbRank())

            # Done setting up the comm, marking it as processed
            comm.markAsProcessed()

        if folder is not None:
            # Create the folder if it doesn't exist
            folder.mkdir(parents=True, exist_ok=True)

            # Write the hostfile
            hostfilePath = folder / hostfileName
            with open(hostfilePath, "w") as f:
                f.write(hostfileContent)
                f.close()

            # Write the rankfile
            rankfilePath = folder / rankfileName
            with open(rankfilePath, "w") as f:
                f.write(rankfileContent)
                f.close()

            # Write the command file
            commandfilePath = folder / commandfileName
            with open(commandfilePath, "w") as f:
                f.write("#! /bin/bash\n\n")
                f.write(mpirunCommand)
                f.close()
        else:
            # Write the hostfile
            hostfilePath = Path(hostfileName)
            with open(hostfilePath, "w") as f:
                f.write(hostfileContent)
                f.close()

            # Write the rankfile
            rankfilePath = Path(rankfileName)
            with open(rankfilePath, "w") as f:
                f.write(rankfileContent)
                f.close()

            # Write the command file
            commandfilePath = Path(commandfileName)
            with open(commandfilePath, "w") as f:
                f.write("#! /bin/bash\n\n")
                f.write(mpirunCommand)
                f.close()

        # Now that all the tasks have been processed, all the information required has been
        # associated with the relevant component. We can now generate the configuration for the
        # workflow
        workflow.generateWorkflowConfiguration()

            

    def appendMPITask(self, task:Task, rankOffset:int) -> Tuple[str, str, str, int]:
        # Return expected: output hostfile, output rankfile, output cmdline, new rankoffset
        placementPolicy = task.getPlacementPolicy()
        if placementPolicy == MPIPlacementPolicy.ONETASKPERCORE:
            return self.appendMPITaskPerCore(task=task, rankOffset=rankOffset)
        elif placementPolicy == MPIPlacementPolicy.ONETASKPERSOCKET:
            return self.appendMPITaskPerSocket(task=task, rankOffset=rankOffset)
        elif placementPolicy == MPIPlacementPolicy.ONETASKPERNODE:
            return self.appendMPITaskPerNode(task=task, rankOffset=rankOffset)
        else:
            raise NotImplementedError("Placement policy not implemented yet.")

    def appendMPITaskPerCore(self, task:Task, rankOffset:int) -> Tuple[str, str, str, int]:
        # Return expected: output hostfile, output rankfile, output cmdline, new rankoffset
        resources = task.getResources()
        coreList = resources.getListOfCores()

        hostfile = ""
        rankfile = ""
        commandline = ""
        nbCores = len(coreList)

        if nbCores == 0:
            raise ValueError(f"No cores found in the resources assigned to the task {task.getName()}.")
        
        for i, core in enumerate(coreList):
            hostfile += f"{core['hostname']}\n"
            rankfile += f"rank {rankOffset+i}={core['hostname']} slots={core['mainthread']}\n"
        
        commandline += f" -np {nbCores} {task.getCommandLine()}"

        return hostfile, rankfile, commandline, rankOffset + nbCores
    
    def appendMPITaskPerSocket(self, task:Task, rankOffset:int) -> Tuple[str, str, str, int]:
        # Return expected: output hostfile, output rankfile, output cmdline, new rankoffset
        resources = task.getResources()
        corePerSocketList = resources.getListOfCoresPerSocket()

        hostfile = ""
        rankfile = ""
        commandline = ""
        nbRanks = len(corePerSocketList)
        
        for i, socket in enumerate(corePerSocketList):
            slots = ""
            if len(socket) == 0:
                raise ValueError(f"No cores found in a socket assigned to the task {task.getName()}.")
            for core in socket:
                hostfile += f"{core['hostname']}\n"
                slots += f"{core['mainthread']},"
            slots = slots.rstrip(",")
            rankfile += f"rank {rankOffset+i}={core['hostname']} slots={slots}\n"
        
        commandline += f" -np {nbRanks} {task.getCommandLine()}"

        return hostfile, rankfile, commandline, rankOffset + nbRanks
    
    def appendMPITaskPerNode(self, task:Task, rankOffset:int) -> Tuple[str, str, str, int]:
        # Return expected: output hostfile, output rankfile, output cmdline, new rankoffset
        resources = task.getResources()
        corePerNodeList = resources.getListOfCoresPerNode()

        hostfile = ""
        rankfile = ""
        commandline = ""
        nbRanks = len(corePerNodeList)
        
        for i, node in enumerate(corePerNodeList):
            slots = ""
            if len(node) == 0:
                raise ValueError(f"No cores found in a socket assigned to the task {task.getName()}.")
            for core in node:
                hostfile += f"{core['hostname']}\n"
                slots += f"{core['mainthread']},"
            slots = slots.rstrip(",")
            rankfile += f"rank {rankOffset+i}={core['hostname']} slots={slots}\n"
        
        commandline += f" -np {nbRanks} {task.getCommandLine()}"

        return hostfile, rankfile, commandline, rankOffset + nbRanks



class MainLauncher:
    def __init__(self) -> None:
        pass
        
    def generateOutputFiles(self, workflow:Workflow):
        mpiLauncher = OpenMPILauncher()
        mpiLauncher.generateOutputFiles(workflow=workflow)