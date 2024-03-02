from godrick.workflow import Workflow
from godrick.task import TaskType, Task, MPIPlacementPolicy
from typing import Tuple

class OpenMPILauncher():
    def __init__(self) -> None:
        pass

    def generateOutputFiles(self, workflow:Workflow):
        tasks = workflow.getTasks()
        if len(tasks) == 0:
            raise RuntimeError("Attempting to generate commands from an empty worklow. Abording.")

        mpirunCommand = f"mpirun --hostfile hostfile.{workflow.getName()}.txt --rankfile rankfile.{workflow.getName()}.txt "
        rankfileContent = ""
        hostfileContent = ""
        rankOffset = 0
        for task in tasks:
            resource = task.getResources()
            if resource is None:
                raise ValueError(f"The task {task.getName()} does have resources assigned to it.")

            if task.getTaskType() != TaskType.MPI:
                raise RuntimeError(f"Trying to launch a non-mpi task with the mpi launcher.")
            
            (hostfile, rankfile, cmd, newOffset) = self.appendMPITask(task, rankOffset)
            hostfileContent += hostfile
            rankfileContent += rankfile
            mpirunCommand += cmd
            rankOffset = newOffset

        print("Hostfile content:")
        print(hostfileContent)
        print("Rankfile content:")
        print(rankfileContent)
        print("Command line:")
        print(mpirunCommand)

            

    def appendMPITask(self, task:Task, rankOffset:int) -> Tuple[str, str, str, int]:
        # Return expected: output hostfile, output rankfile, output cmdline, new rankoffset
        placementPolicy = task.getPlacementPolicy()
        if placementPolicy == MPIPlacementPolicy.ONETASKPERCORE:
            return self.appendMPITaskPerCore(task=task, rankOffset=rankOffset)
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
        
        commandline += f"-np {nbCores} {task.getCommandLine()}"

        return hostfile, rankfile, commandline, rankOffset + nbCores



class MainLauncher:
    def __init__(self) -> None:
        pass
        
    def generateOutputFiles(self, workflow:Workflow):
        mpiLauncher = OpenMPILauncher()
        mpiLauncher.generateOutputFiles(workflow=workflow)