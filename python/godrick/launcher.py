from godrick.workflow import Workflow
from godrick.task import TaskType, Task, MPIPlacementPolicy, Process
from godrick.communicator import CommunicatorTransportType
from typing import Tuple
from pathlib import Path

import os
import stat

class OpenMPILauncher():
    def __init__(self) -> None:
        self.folder = None
        self.hostfilePath = None
        self.rankfilePath = None
        self.commandfilePath = None

    def generateOutputFiles(self, workflow:Workflow, folder:Path = None):
        self.folder = folder

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
            if comm.getCommunicatorTransportType() != CommunicatorTransportType.MPI:
                continue
            
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
            self.hostfilePath = folder / hostfileName
            with open(self.hostfilePath, "w") as f:
                f.write(hostfileContent)
                f.close()

            # Write the rankfile
            self.rankfilePath = folder / rankfileName
            with open(self.rankfilePath, "w") as f:
                f.write(rankfileContent)
                f.close()

            # Write the command file
            self.commandfilePath = folder / commandfileName
            with open(self.commandfilePath, "w") as f:
                f.write("#! /bin/bash\n\n")
                f.write(mpirunCommand)
                f.close()

            # Making the file executable
            os.chmod(self.commandfilePath, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE | stat.S_IROTH | stat.S_IXOTH) 
        else:
            # Write the hostfile
            self.hostfilePath = Path(hostfileName)
            with open(self.hostfilePath, "w") as f:
                f.write(hostfileContent)
                f.close()

            # Write the rankfile
            self.rankfilePath = Path(rankfileName)
            with open(self.rankfilePath, "w") as f:
                f.write(rankfileContent)
                f.close()

            # Write the command file
            self.commandfilePath = Path(commandfileName)
            with open(self.commandfilePath, "w") as f:
                f.write("#! /bin/bash\n\n")
                f.write(mpirunCommand)
                f.close()

            # Making the file executable
            os.chmod(self.commandfilePath, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE | stat.S_IROTH | stat.S_IXOTH) 


            

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

            # Create the corresponding process 
            proc = Process(hostname=core['hostname'], task=task)
            task.addProcess(proc)
        
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

            # Create the corresponding process 
            proc = Process(hostname=core['hostname'], task=task)
            task.addProcess(proc)
        
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

            # Create the corresponding process 
            proc = Process(hostname=core['hostname'], task=task)
            task.addProcess(proc)
        
        commandline += f" -np {nbRanks} {task.getCommandLine()}"

        return hostfile, rankfile, commandline, rankOffset + nbRanks

    def removeFiles(self) -> None:
        
        if self.rankfilePath is not None and self.rankfilePath.is_file():
            self.rankfilePath.unlink()

        if self.hostfilePath is not None and self.hostfilePath.is_file():
            self.hostfilePath.unlink()

        if self.commandfilePath is not None and self.commandfilePath.is_file():
            self.commandfilePath.unlink()

class ZMQLauncher:
    def __init__(self) -> None:
        pass

    def processZMQCommunicator(self, workflow:Workflow):
        # Parse all the communicators, look for ZMQ types, and setup the addressses
        communicators = workflow.getCommunicators()

        for communicator in communicators:
            if communicator.getCommunicatorTransportType() == CommunicatorTransportType.ZMQ:
                # Search for the task sending data
                outTask = workflow.getTaskByName(communicator.getOutputTaskName())
                outProcesses = outTask.getProcessList()

                # Search for the task receiving data
                inTask = workflow.getTaskByName(communicator.getInputTaskName())
                inProcesses = inTask.getProcessList()

                # Assign the address to the port information
                communicator.configureSockets(outProcesses, inProcesses)

                # Mark the communicator
                communicator.markAsProcessed()

    def removeFiles(self) -> None:
        pass


class TaskSetup:
    def __init__(self) -> None:
        pass

    def assignProcesses(self, workflow:Workflow, folder:Path = None) -> None :
        raise NotImplementedError("Function assignProcesses() not implemented by a TaskSetup class.")

    def removeFiles(self) -> None:
        raise NotImplementedError("Function removeFiles() not implemented by a ProcessAssigner class.")


class OpenMPITaskSetup(TaskSetup):
    def __init__(self) -> None:
        super().__init__()
        self.folder = None
        self.hostfilePath = None
        self.rankfilePath = None
        self.commandfilePath = None

    def assignProcesses(self, workflow:Workflow, folder:Path = None) -> None :
        self.folder = folder

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

        if folder is not None:
            # Create the folder if it doesn't exist
            folder.mkdir(parents=True, exist_ok=True)

            # Write the hostfile
            self.hostfilePath = folder / hostfileName
            with open(self.hostfilePath, "w") as f:
                f.write(hostfileContent)
                f.close()

            # Write the rankfile
            self.rankfilePath = folder / rankfileName
            with open(self.rankfilePath, "w") as f:
                f.write(rankfileContent)
                f.close()

            # Write the command file
            self.commandfilePath = folder / commandfileName
            with open(self.commandfilePath, "w") as f:
                f.write("#! /bin/bash\n\n")
                f.write(mpirunCommand)
                f.close()

            # Making the file executable
            os.chmod(self.commandfilePath, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE | stat.S_IROTH | stat.S_IXOTH) 
        else:
            # Write the hostfile
            self.hostfilePath = Path(hostfileName)
            with open(self.hostfilePath, "w") as f:
                f.write(hostfileContent)
                f.close()

            # Write the rankfile
            self.rankfilePath = Path(rankfileName)
            with open(self.rankfilePath, "w") as f:
                f.write(rankfileContent)
                f.close()

            # Write the command file
            self.commandfilePath = Path(commandfileName)
            with open(self.commandfilePath, "w") as f:
                f.write("#! /bin/bash\n\n")
                f.write(mpirunCommand)
                f.close()

            # Making the file executable
            os.chmod(self.commandfilePath, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE | stat.S_IROTH | stat.S_IXOTH) 

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

            # Create the corresponding process 
            proc = Process(hostname=core['hostname'], task=task)
            task.addProcess(proc)
        
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

            # Create the corresponding process 
            proc = Process(hostname=core['hostname'], task=task)
            task.addProcess(proc)
        
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

            # Create the corresponding process 
            proc = Process(hostname=core['hostname'], task=task)
            task.addProcess(proc)
        
        commandline += f" -np {nbRanks} {task.getCommandLine()}"

        return hostfile, rankfile, commandline, rankOffset + nbRanks
    
    def removeFiles(self) -> None:
        
        if self.rankfilePath is not None and self.rankfilePath.is_file():
            self.rankfilePath.unlink()

        if self.hostfilePath is not None and self.hostfilePath.is_file():
            self.hostfilePath.unlink()

        if self.commandfilePath is not None and self.commandfilePath.is_file():
            self.commandfilePath.unlink()

class CommunicatorSetup:
    def __init__(self) -> None:
        pass

    def configureCommunicator(self, workflow:Workflow, folder:Path = None) -> None :
        raise NotImplementedError("Function configureCommunicator() not implemented by a CommunicatorSetup class.")
    
    def removeFiles(self) -> None:
        pass

class MPICommunicatorSetup(CommunicatorSetup):
    def __init__(self) -> None:
        super().__init__()

    def configureCommunicator(self, workflow:Workflow, folder:Path = None) -> None :
        for i, comm in enumerate(workflow.getCommunicators()):
            if comm.getCommunicatorTransportType() != CommunicatorTransportType.MPI:
                continue
            
            inputTask = workflow.getTaskByName(comm.getInputTaskName())
            comm.setInputMPIRanks(inputTask.getGlobalStartRank(), inputTask.getGlobalNbRank())

            outputTask = workflow.getTaskByName(comm.getOutputTaskName())
            comm.setOutputMPIRanks(outputTask.getGlobalStartRank(), outputTask.getGlobalNbRank())

            # Done setting up the comm, marking it as processed
            comm.markAsProcessed()
    
    def removeFiles(self) -> None:
        pass

class ZMQCommunicatorSetup(CommunicatorSetup):
    def __init__(self) -> None:
        super().__init__()
    
    def configureCommunicator(self, workflow: Workflow, folder: Path = None) -> None:
        # Parse all the communicators, look for ZMQ types, and setup the addressses
        communicators = workflow.getCommunicators()

        for communicator in communicators:
            if communicator.getCommunicatorTransportType() == CommunicatorTransportType.ZMQ:
                
                if not communicator.isConfigurable():
                    raise RuntimeError(f"The ZMQ Communicator {communicator.getName()} cannnot be configured.")
                communicator.configure()

                # Mark the communicator
                communicator.markAsProcessed()

    def removeFiles(self) -> None:
        pass

class MainLauncher:
    def __init__(self) -> None:
        self.launchers = []
        self.workflow = None
        
    def generateOutputFiles(self, workflow:Workflow, folder:Path = None):
        
        # Process the tasks 
        #mpiLauncher = OpenMPILauncher()
        #mpiLauncher.generateOutputFiles(workflow=workflow, folder=folder)
        self.processTasks(workflow, folder)

        # Forward the processes from the tasks to their respective 
        self.forwardProcessesToCommunicators(workflow)

        # Process the communicators when necessary
        #zmqLauncher = ZMQLauncher()
        #zmqLauncher.processZMQCommunicator(workflow=workflow)
        #mpiCommLauncher = MPICommunicatorSetup()
        #mpiCommLauncher.configureCommunicator(workflow=workflow, folder=folder)
        #zmqCommLauncher = ZMQCommunicatorSetup()
        #zmqCommLauncher.configureCommunicator(workflow=workflow, folder=folder)
        self.processCommunicators(workflow, folder)

        # Now that all the tasks have been processed, all the information required has been
        # associated with the relevant component. We can now generate the configuration for the
        # workflow
        workflow.generateWorkflowConfiguration()


        self.workflow = workflow

    def processTasks(self, workflow:Workflow, folder:Path = None) -> None:
        mpiLauncher = OpenMPITaskSetup()
        mpiLauncher.assignProcesses(workflow=workflow, folder=folder)

        self.launchers.append(mpiLauncher)

    def forwardProcessesToCommunicators(self, workflow:Workflow) -> None:
        communicators = workflow.getCommunicators()

        for comm in communicators:
            # If the communicator has a receiver side, forward the processes of the task to the communicator
            inputTaskName = comm.getInputTaskName()
            if inputTaskName != "":
                if not workflow.hasTask(inputTaskName):
                    raise RuntimeError(f"The communicator {comm.getName()} is connected to the task {inputTaskName} but the task is not declared in the workflow.")
                task = workflow.getTaskByName(inputTaskName)
                comm.assignReceiverProcesses(task.getProcessList())

            # If the communicator has a receiver side, forward the processes of the task to the communicator
            outputTaskName = comm.getOutputTaskName()
            if outputTaskName != "":
                if not workflow.hasTask(outputTaskName):
                    raise RuntimeError(f"The communicator {comm.getName()} is connected to the task {outputTaskName} but the task is not declared in the workflow.")
                task = workflow.getTaskByName(outputTaskName)
                comm.assignSenderProcesses(task.getProcessList())

    def processCommunicators(self, workflow:Workflow, folder:Path = None) -> None:
        mpiCommLauncher = MPICommunicatorSetup()
        mpiCommLauncher.configureCommunicator(workflow=workflow, folder=folder)
        zmqCommLauncher = ZMQCommunicatorSetup()
        zmqCommLauncher.configureCommunicator(workflow=workflow, folder=folder)

        self.launchers.append(mpiCommLauncher)
        self.launchers.append(zmqCommLauncher)

    def removeFiles(self) -> None:
        for launcher in self.launchers:
            launcher.removeFiles()
        if self.workflow is not None:
            self.workflow.removeFiles()

