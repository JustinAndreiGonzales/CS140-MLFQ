from enum import StrEnum

class Status(StrEnum):
    CPU = "CPU"
    I_O = "I/O"
    DONE = "DONE"
    READY = "READY"