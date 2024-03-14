from godrick.task import Task
from godrick.communicator import Communicator
import json
from pathlib import Path
import os 
import stat

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
        
        # Check that the input and output tasks are declared
        if communicator.getInputTaskName() not in self.tasks.keys():
            raise ValueError(f"The input task {communicator.getInputTaskName()} is not declared in the workflow but is used by the communicator {communicator.getName()}.")
        if communicator.getOutputTaskName() not in self.tasks.keys():
            raise ValueError(f"The output task {communicator.getOutputTaskName()} is not declared in the workflow but is used by the communicator {communicator.getName()}.")
        
        self.communicators[communicator.getName()] = communicator

    def getTasks(self) -> list[Task]:
        return list(self.tasks.values())
    
    def getTaskByName(self, name:str) -> Task:
        if name not in self.tasks.keys():
            raise ValueError(f"Task {name} not found in the workflow {self.name}.")
        return self.tasks[name]
    
    def getCommunicators(self) -> list[Communicator]:
        return list(self.communicators.values())
    
    def getName(self) -> str:
        return self.name
    
    def getConfigurationFile(self) -> str:
        return f"config.{self.name}.json"
    
    def generateWorkflowConfiguration(self, folder:Path = None):
        config = {}
        
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
        
        configfileName = f"config.{self.name}.json"
        if folder is not None:
            configPath = folder / configfileName
        else:
            configPath = Path(configfileName)
        with open(configPath, "w") as f:
            json.dump(config, f, indent=4)
            f.close()
