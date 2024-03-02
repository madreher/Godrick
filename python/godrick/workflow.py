from godrick.task import Task

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
