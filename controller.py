
from model import MLFQ
from view import Input


class Controller:
    def __init__(self):
        ...

    def get_timestamp(self):
        ...

    def get_statistics(self):
        ...

    def input_to_model(self, inputs: Input):
        ...

    def run(self):
        ...