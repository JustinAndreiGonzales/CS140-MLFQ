from multiprocessing import process
import time
from typing import Protocol
from project_types import Status


class Process:
    def __init__(self, name: str, arrival_time: int, burst_times: list[int]):
        self.name = name
        self.arrival_time = arrival_time
        self.current_queue: int = 0
        self.burst_times = burst_times
        self.current_time_burst: int = 0
        self.current_time_in_queue: int = 0
        self.completion_time: int = -1 # what is starting value?
        self.waiting_time: int = -1 # what is starting value?
        self.state: Status = Status.READY

    def __lt__(self, other):
        self_burst = self.burst_times[0] - self.current_time_burst
        other_burst = other.burst_times[0] = other.current_time_burst 
        return self_burst < other_burst

    @property
    def get_arrival_time(self) -> int:
        return self.get_arrival_time
    
    def increment_time_burst(self) -> None:
        self.current_time_burst += 1

    def increment_allotment_in_queue(self) -> None:
        self.current_time_in_queue += 1

    def dequeue_burst_time(self):
        ...

    def change_state(self):
        ...


class Queue(Protocol):
    def enqueue_process(self, p: Process) -> None:
        ...

    def dequeue_process(self) -> Process:
        ...


class RoundRobinQueue:
    def __init__(self, time_allotment: int):
        self.quantum_time = 4
        self.process_queue: list[Process] = []
        self.time_allotment = time_allotment
        self.quantum_used: int = 0

    def increment_quantum(self) -> None:
        self.quantum_used += 1

    def enqueue_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def dequeue_process(self) -> Process:
        return self.process_queue.pop(0)

class FirstComeFirstServeQueue:
    def __init__(self, time_allotment: int):
        self.process_queue: list[Process] = []
        self.time_allotment = time_allotment

    def enqueue_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def dequeue_process(self) -> Process:
        return self.process_queue.pop(0)

class ShortestJobFirst:
    def __init__(self):
        self.process_queue: list[Process] = []

    def enqueue_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def dequeue_process(self) -> Process:
        return self.process_queue.pop(0)

    def sort_queue(self) -> None:
        self.process_queue.sort() # check nalang if tama

class IO:
    def __init__(self):
        self.process_queue: list[Process] = []

    def enqueue_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def dequeue_process(self) -> Process:
        return self.process_queue.pop(0)
    

class MLFQ:
    def __init__(self, Q1: RoundRobinQueue, Q2: FirstComeFirstServeQueue, context_switch_time: int):
        self.curr_time = 0
        self.Q1 = Q1
        self.Q2 = Q2
        self.Q3 = ShortestJobFirst()
        self.IO = IO()
        self.context_switch_time = context_switch_time
        self.processes: list[Process] = []
        self.CPU: Process = Process(" ", -1, []) # dummy value
        self.is_finish_running: bool = False
        self.incoming_processes: list[Process] = []

        self.newlyaddedprocesses: list[Process] = []
    
    def enqueue_to_queue(self, queue: Queue, process: Process) -> None:
        queue.enqueue_process(process)

    def dequeue_process(self, queue: Queue) -> Process:
        return queue.dequeue_process()

    def add_process(self, process: Process) -> None:
        self.processes.append(process)
        self.incoming_processes.append(process)

    def sort_incoming_processes(self) -> None:
        self.incoming_processes = sorted(self.incoming_processes, key=lambda p: (p.arrival_time, p.name))

    def update_time_stamp(self) -> None:
        # increment time
        self.curr_time += 1

        # increment IO processes
        if (len(self.IO.process_queue) != 0):
            for p in self.IO.process_queue:
                p.current_time_burst += 1

        # increment CPU process
        self.CPU.current_time_burst += 1
        self.CPU.current_time_in_queue += 1
        self.Q1.increment_quantum()

        # enqueue newly arriving processes
        if (len(self.incoming_processes) != 0):
            for p in self.incoming_processes:
                if(self.curr_time == p.arrival_time):
                    self.incoming_processes.remove(p)
                    self.Q1.enqueue_process(p)

def check_current_queue(self, queue_index) -> Queue:
        if (queue_index == 1):
            return self.Q1
        elif (queue_index == 2):
            return self.Q2
        elif (queue_index == 3):
            return self.Q3
    
def next_process(self):
    current_queue = self.check_current_queue(self.CPU)

    if (current_queue in [self.Q1, self.Q2, self.Q3] and self.CPU != None):
        if self.CPU.current_time_burst >= self.CPU.burst_times[0]:
            if len(self.CPU.burst_times) == 1:
                self.finished_processes.append(current_queue.dequeue_process())
            else:
                self.IO.enqueue_process(current_queue.dequeue_process())

            self.CPU = current_queue.dequeue_process()
            return

        if isinstance(current_queue, RoundRobinQueue) or isinstance(current_queue, FirstComeFirstServeQueue):
            if self.CPU.current_time_in_queue >= current_queue.time_allotment:
                self.demoted_process.append(self.CPU)

                lower_queue = check_current_queue(self.CPU.current_queue + 1)
                lower_queue.enqueue_process(current_queue.dequeue_process())

                self.CPU = current_queue.dequeue_process()
                return

            if current_queue == self.Q1:
                if self.Q1.quantum_used >= self.Q1.quantum_time:
                    self.Q1.enqueue_process(self.Q1.dequeue_process())

                self.CPU = self.Q1.dequeue_process()
                return
            