"""
@author: Andrei Istudor     andrei.istudor@hu-berlin.de
"""

from enum import Enum

class TaskState(Enum):
    '''
    Describes the current status of a :class:`PhenoTask.PhenoTask`
    '''
    #: just created and queued
    new = 1
    #: currently being processed
    processing = 2
    #: processed
    finished = 3
    #: error state - not used
    error = 4
    #: other - not used
    other = 5
    #: selected from the list
    selected = 6
