from enum import Enum

class TaskState(Enum):
    new = 1
    processing = 2
    finished = 3
    error = 4
    other = 5
    selected = 6
