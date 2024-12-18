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

    def pop_burst_time(self):
        ...

    def change_state(self):
        ...


class Queue(Protocol):
    def push_process(self, p: Process) -> None:
        ...

    def pop_process(self) -> Process:
        ...


class RoundRobinQueue:
    def __init__(self, time_allotment: int):
        self.process_queue: list[Process] = []
        self.time_allotment = time_allotment
        self.quantum_used: int = 0

    def increment_quantum(self) -> None:
        self.quantum_used += 1

    def push_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def pop_process(self) -> Process:
        return self.process_queue.pop()

class FirstComeFirstServeQueue:
    def __init__(self, time_allotment: int):
        self.process_queue: list[Process] = []
        self.time_allotment = time_allotment

    def push_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def pop_process(self) -> Process:
        return self.process_queue.pop()

class ShortestJobFirst:
    def __init__(self):
        self.process_queue: list[Process] = []

    def push_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def pop_process(self) -> Process:
        return self.process_queue.pop()

    def sort_queue(self) -> None:
        self.process_queue.sort() # check nalang if tama

class IO:
    def __init__(self):
        self.process_queue: list[Process] = []

    def push_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def pop_process(self) -> Process:
        return self.process_queue.pop()
    

class MLFQ:
    def __init__(self, Q1: RoundRobinQueue, Q2: FirstComeFirstServeQueue, context_switch_time: int):
        self.curr_time = 0
        self.Q1 = Q1
        self.Q2 = Q2
        self.Q3 = ShortestJobFirst()
        self.IO = IO()
        self.context_switch_time = context_switch_time
        self.processes: list[Process] = []
        self.CPU: Process | None = None
        self.is_finish_running: bool = False

        self.incoming_processes: list[Process] = []
    
    def push_to_queue(self, queue: Queue, process: Process) -> None:
        queue.push_process(process)

    def pop_process(self, queue: Queue) -> Process:
        return queue.pop_process()

    def add_process(self, process: Process) -> None:
        self.processes.append(process)
        self.incoming_processes.append(process)

    def sort_incoming_processes(self) -> None:
        self.incoming_processes = sorted(self.incoming_processes, key=lambda p: (p.arrival_time, p.name))

    def update_time_stamp(self) -> None:
        ...