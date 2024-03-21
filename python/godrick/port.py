from __future__ import annotations


class Port():
    def __init__(self, name:str, task) -> None:
        self.name = name
        self.communicators = []
        self.task = task

    def toDict(self) -> dict:
        result = {}
        result["name"] = self.name

    def getPortName(self) -> str:
        return self.name
    
    def getTaskName(self) -> str:
        return self.task.getName()
    
    def getTask(self):
        return self.task

class InputPort(Port):
    def __init__(self, name: str, task) -> None:
        super().__init__(name, task)

class OutputPort(Port):
    def __init__(self, name: str, task) -> None:
        super().__init__(name, task)