from model import MLFQ, Process, EMPTY_PROCESS
from view import Timestamp, View, ProcessesStats, Input

class Controller:
    def __init__(self, model: MLFQ, view: View):
        self._model = model
        self._view = view

    def get_timestamp(self):
        time = self._model.curr_time
        arriving_processes = None if not self._model.newlyaddedprocesses else [p.name for p in self._model.newlyaddedprocesses]
        self._model.newlyaddedprocesses = []
        processes_done = None if not self._model.finished_processes else [p.name for p in self._model.finished_processes]
        self._model.finished_processes = []
        q1 = []
        q2 = []
        q3 = []
        if self._model.Q1.process_queue:
            for p in self._model.Q1.process_queue:
                q1.append(p.name)
        if self._model.Q2.process_queue:
            for p in self._model.Q2.process_queue:
                q2.append(p.name)
        if self._model.Q3.process_queue:
            for p in self._model.Q3.process_queue:
                q3.append(p.name)

        is_in_context_switch = self._model.is_in_context_switch
        switching_process = self._model.process_holder.name

        cpu = None if self._model.CPU.arrival_time == -1 else self._model.CPU.name
        io = None if not self._model.IO.process_queue else [p.name for p in self._model.IO.process_queue]
        self._model.IO.process_queue = []
        demoted = self._model.demoted_process
        self._model.demoted_process = None

        self._view.print_timestamp(
            Timestamp(time, arriving_processes, processes_done, q1, q2, q3, is_in_context_switch, switching_process, cpu, io, demoted)
        )

    def get_statistics(self):
        processes = self._model.processes
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
        processes = inputs.processes
        for p in processes:
            self._model.add_process(Process(p["name"], p["arrival_time"], p["bursts"]))
        

    def run(self):
        self.input_to_model(self._view.get_input())
        self._model.sort_incoming_processes()
        self._model.processes = sorted(self._model.processes, key=lambda p: p.name)
        self.get_timestamp() # for time = 0

        while (self._model.incoming_processes and \
                self._model.Q1.process_queue and \
                self._model.Q2.process_queue and \
                self._model.Q3.process_queue and \
                self._model.IO and \
                self._model.CPU == EMPTY_PROCESS):
            self._model.update_time_stamp()
            self.get_timestamp()
        print("SIMULATION DONE\n") # tinamad na
        self.get_statistics()