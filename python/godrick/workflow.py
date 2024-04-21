from godrick.task import Task, TaskFactory
from godrick.communicator import Communicator, CommunicatorFactory
import json
from pathlib import Path
from enum import Enum

class WorkflowConfigFileType(Enum):
    WORKFLOW_CONFIG_FULL = 0,
    WORKFLOW_CONFIG_GATES_ONLY = 1

class Workflow:
    def __init__(self, name:str="defaultworkflow") -> None:
        self.tasks = {}
        self.name = name
        self.communicators = {}

    def declareTask(self, task:Task) -> None:
        if task.getName() in self.tasks.keys():
            raise ValueError(f"A task with the name {task.getName()} has already been registered.")
        self.tasks[task.getName()] = task

    def declareCommunicator(self, communicator:Communicator) -> None:
        # Check that both the input and outputs are connected
        if not communicator.isValid():
            raise ValueError("The communicator is not valid. Forgot to connect the input or output ports?")
        
        if communicator.isPairedCommunicator():
            # Check that the input and output tasks are declared
            if communicator.getInputTaskName() not in self.tasks.keys():
                raise ValueError(f"The input task {communicator.getInputTaskName()} is not declared in the workflow but is used by the communicator {communicator.getName()}.")
            if communicator.getOutputTaskName() not in self.tasks.keys():
                raise ValueError(f"The output task {communicator.getOutputTaskName()} is not declared in the workflow but is used by the communicator {communicator.getName()}.")
        elif communicator.isSenderGate():
            if communicator.getOutputTaskName() not in self.tasks.keys():
                raise ValueError(f"The output task {communicator.getOutputTaskName()} is not declared in the workflow but is used by the communicator {communicator.getName()}.")
        elif communicator.isReceiverGate():
            if communicator.getInputTaskName() not in self.tasks.keys():
                raise ValueError(f"The input task {communicator.getInputTaskName()} is not declared in the workflow but is used by the communicator {communicator.getName()}.")
        else:
            raise NotImplementedError("Trying to declared a type of communicator not currently supported by the Workflow class.")
        
        self.communicators[communicator.getName()] = communicator

    def getTasks(self) -> list[Task]:
        return list(self.tasks.values())

    def hasTask(self, name:str) -> bool:
        return name in self.tasks.keys()
    
    def getTaskByName(self, name:str) -> Task:
        if name not in self.tasks.keys():
            raise ValueError(f"Task {name} not found in the workflow {self.name}.")
        return self.tasks[name]
    
    def getCommunicators(self) -> list[Communicator]:
        return list(self.communicators.values())
    
    def getGateCommunicators(self) -> list[Communicator]:
        result = []
        for comm in self.communicators.values():
            if comm.isGate():
                result.append(comm)
        return result
    
    def getName(self) -> str:
        return self.name
    
    def getConfigurationFile(self) -> str:
        return f"config.{self.name}.json"
    
    def getGatesFile(self) -> str:
        return f"gates.{self.name}.json"
    
    def generateWorkflowConfiguration(self, folder:Path = None):
        config = {}
        config["format"] = WorkflowConfigFileType.WORKFLOW_CONFIG_FULL.name
        config["name"] = self.name
        config["header"] = {}
        config["header"]["version"] = 0
        config["header"]["generator"] = "generateWorkflowConfiguration"
        config["tasks"] = []
        for task in self.tasks.values():
            if not task.hasBeenProcessed():
                raise RuntimeError(f"The task {task.getName()} has not be processed by a launcher. Make sure to call a launcher first.")
            config["tasks"].append(task.toDict())
        
        config["communicators"] = []
        for comm in self.communicators.values():
            if not comm.hasBeenProcessed():
                raise RuntimeError(f"The communicator {comm.getName()} has not be processed by a launcher. Make sure to call a launcher first.")
            config["communicators"].append(comm.toDict())
        
        configFileName = f"config.{self.name}.json"
        if folder is not None:
            configPath = folder / configFileName
        else:
            configPath = Path(configFileName)
        with open(configPath, "w") as f:
            json.dump(config, f, indent=4)
            f.close()

        gates = self.getGateCommunicators()
        if len(gates) > 0:
            gateConfig = {}
            gateConfig["name"] = self.name
            gateConfig["format"] = WorkflowConfigFileType.WORKFLOW_CONFIG_GATES_ONLY.name
            gateConfig["header"] = {}
            gateConfig["header"]["version"] = 0
            gateConfig["header"]["generator"] = "generateWorkflowConfiguration"
            gateConfig["gates"] = []
            for gate in gates:
                gateConfig["gates"].append(gate.toDict())

            gateFileName = f"gates.{self.name}.json"
            if folder is not None:
                gatePath = folder / gateFileName
            else:
                gatePath = Path(gateFileName)
            with open(gatePath, "w") as f:
                json.dump(gateConfig, f, indent=4)
                f.close()

    def removeFiles(self) -> None:
        configFile = Path(self.getConfigurationFile())
        if configFile.is_file():
            configFile.unlink()

        gateFile = Path(self.getGatesFile())
        if gateFile.is_file():
            gateFile.unlink()

    def initFromWorkflowConfigFile(self, configFilePath:Path) -> None:
        if not configFilePath.is_file():
            raise FileNotFoundError(f"Unable to find the configuration file {configFilePath}")
        
        with open(configFilePath) as f:
            doc = f.read()
            data = json.loads(doc)
            
            if "format" not in data.keys():
                raise RuntimeError(f"Unable to determine the the format in the configuration file {configFilePath}.")
            if data["format"] != WorkflowConfigFileType.WORKFLOW_CONFIG_FULL.name:
                raise RuntimeError(f"Called initFromConfigFile() with the configuration file {configFilePath}, but the given configuration file has not the format {WorkflowConfigFileType.WORKFLOW_CONFIG_FULL.name}.")
            if "name" not in data.keys():
                raise RuntimeError(f"Unable to find the name of the workflow in the configuration file {configFilePath}.")
            if "tasks" not in data.keys():
                raise RuntimeError(f"Unable to find the list of tasks in the configuration file {configFilePath}.")
            if "communicators" not in data.keys():
                raise RuntimeError(f"Unable to find the list of communicators in the configuration file {configFilePath}.")

            self.name = data["name"]
            version = data["header"]["version"]
            
            self.tasks.clear()
            self.communicators.clear()

            taskFactory = TaskFactory()
            for taskDict in data["tasks"]:
                task = taskFactory.jsonToTask(taskDict, version)
                self.tasks[task.getName()] = task

            commFactory = CommunicatorFactory()
            for commDict in data["communicators"]:
                comm = commFactory.jsonToCommunicator(commDict, version)
                self.communicators[comm.getName()] = comm

    def initFromGatesConfigFile(self, configFilePath:Path) -> None:
        if not configFilePath.is_file():
            raise FileNotFoundError(f"Unable to find the configuration file {configFilePath}")
        
        with open(configFilePath) as f:
            doc = f.read()
            data = json.loads(doc)

            if "format" not in data.keys():
                raise RuntimeError(f"Unable to determine the the format in the configuration file {configFilePath}.")
            if data["format"] != WorkflowConfigFileType.WORKFLOW_CONFIG_GATES_ONLY.name:
                raise RuntimeError(f"Called initFromConfigFile() with the configuration file {configFilePath}, but the given configuration file has not the format {WorkflowConfigFileType.WORKFLOW_CONFIG_GATES_ONLY.name}.")
            if "gates" not in data.keys():
                raise RuntimeError(f"Unable to find gates in the configuration file {configFilePath}.")
            version = data["header"]["version"]
            self.tasks.clear()
            self.communicators.clear()

            # In the gate format, we only read gates and insert them in the communicators.
            factory = CommunicatorFactory()
            for gateDict in data["gates"]:
                gate = factory.jsonToCommunicator(gateDict, version)
                self.communicators[gate.getName()] = gate
