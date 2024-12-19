
from model import MLFQ
from view import View, ProcessesStats, Input

class Controller:
    def __init__(self, model: MLFQ, view: View):
        self._model = model
        self._view = view

    def get_timestamp(self):
        ...

    def get_statistics(self):
        processes = sorted(self._model.processes, lambda p: p.name)
        process_names = []
        completion_times = []
        arrival_times = []
        waiting_times = []
        turnaround_times = []

        for p in processes:
            process_names.append(p.name)
            completion_times.append(p.completion_time)
            arrival_times.append(p.arrival_time)
            turnaround_times.append(p.completion_time - p.arrival_time)
            waiting_times.append(p.waiting_time)

        avg_turnaround_time = round(sum(turnaround_times) / len(turnaround_times), 2)
        
        self._view.print_statistics(
            ProcessesStats(process_names, completion_times, arrival_times, waiting_times, turnaround_times, avg_turnaround_time)
        )

    def input_to_model(self, inputs: Input):
        ...

    def run(self):
        ...