from enum import Enum

class TaskState(Enum):
    new = 1
    bg = 2
    bgDone = 3
    track = 4
    trackDone = 5
    proc = 6
    finished = 7
    error = 8
    other = 9
    selected = 10
