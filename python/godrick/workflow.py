from godrick.task import Task
import json
from pathlib import Path

class Workflow:
    def __init__(self, name:str="defaultworkflow") -> None:
        self.tasks = []
        self.name = name

    def addTask(self, task:Task) -> None:
        self.tasks.append(task)

    def getTasks(self) -> list[Task]:
        return self.tasks
    
    def getName(self) -> str:
        return self.name
    
    def generateWorkflowConfiguration(self, folder:Path = None):
        config = {}
        config["tasks"] = []
        for task in self.tasks:
            if not task.hasBeenProcessed():
                raise RuntimeError(f"The task {task.getName()} has not be processed by a launcher. Make sure to call a launcher first.")
            config["tasks"].append(task.toDict())

        configfileName = f"config.{self.name}.json"
        if folder is not None:
            configPath = folder / configfileName
        else:
            configPath = Path(configfileName)
        with open(configPath, "w") as f:
            json.dump(config, f, indent=4)
            f.close()
