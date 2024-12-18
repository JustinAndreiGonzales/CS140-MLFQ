from multiprocessing import process
import time
from typing import Protocol
from project_types import Status

class Process:
    def __init__(self, name: str, arrival_time: int, burst_times: list[int]):
        self.name = name
        self.arrival_time = arrival_time
        self.current_queue: int = 1
        self.burst_times = burst_times
        self.current_time_burst: int = 0
        self.current_time_in_queue: int = 0
        self.completion_time: int = -1 # what is starting value?
        self.waiting_time: int = -1 # what is starting value?

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

EMPTY_PROCESS = Process(" ", -1, []) # dummy 

class Queue(Protocol):
    process_queue: list[Process]

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
        self.CPU: Process = EMPTY_PROCESS # dummy 
        self.is_finish_running: bool = False

        self.context_switch_time = context_switch_time
        self.context_switch_time_used = 0    # time at context switch
        self.is_in_context_switch: bool = False
        self.process_holder: Process = EMPTY_PROCESS # dummy 

        self.processes: list[Process] = []
        self.incoming_processes: list[Process] = []
        self.newlyaddedprocesses: list[Process] = []
        self.finished_processes: list[Process] = []
        self.demoted_process: Process | None = None
    
    def enqueue_to_queue(self, queue: Queue, process: Process) -> None:
        queue.enqueue_process(process)

    def dequeue_process(self, queue: Queue) -> Process:
        return queue.dequeue_process()

    def add_process(self, process: Process) -> None:
        self.processes.append(process)
        self.incoming_processes.append(process)

    def sort_incoming_processes(self) -> None:
        self.incoming_processes = sorted(self.incoming_processes, key=lambda p: (p.arrival_time, p.name))

    def check_current_queue(self, queue_index) -> Queue:
        if (queue_index == 1):
            return self.Q1
        elif (queue_index == 2):
            return self.Q2
        else: #queue_index == 3
            return self.Q3
            
    def next_process_to_run(self) -> Process:
        queue_index = self.CPU.current_queue
        
        while (queue_index < 3):
            current_queue = self.check_current_queue(queue_index)

            if current_queue.process_queue:
                return current_queue.dequeue_process()
            queue_index += 1
        
        return Process(" ", -1, []) # dummy

    def update_time_stamp(self) -> None:
        # increment time
        self.curr_time += 1

        # increment IO processes
        if (len(self.IO.process_queue) != 0):
            for proc in self.IO.process_queue:
                proc.current_time_burst += 1

        # during context switch
        if (self.is_in_context_switch):
            if self.context_switch_time <= self.context_switch_time_used:
                self.CPU = self.process_holder
                self.context_switch_time_used = 0
                self.is_in_context_switch = False
            else:
                self.context_switch_time_used += 1
            return

        # if CPU is empty
        if (self.CPU == EMPTY_PROCESS):
            return

        # increment CPU process
        self.CPU.current_time_burst += 1
        self.CPU.current_time_in_queue += 1

        # if currently running process is in Q1
        if (self.CPU.current_queue == 1):
            self.Q1.increment_quantum()

        # enqueue newly arriving processes
        if (self.incoming_processes):
            for proc in self.incoming_processes:
                if(self.curr_time == proc.arrival_time):
                    self.incoming_processes.remove(proc)
                    self.Q1.enqueue_process(proc)

        self.next_process()

    def next_process(self):
        current_queue: Queue = self.check_current_queue(self.CPU)

        if (current_queue in [self.Q1, self.Q2, self.Q3] and self.CPU != None):
            # checking CPU burst time
            if self.CPU.current_time_burst >= self.CPU.burst_times[0]:
                # check if process is finished
                if len(self.CPU.burst_times) == 1:
                    self.finished_processes.append(self.CPU)
                else: # check if there is next burst
                    self.IO.enqueue_process(self.CPU)

                # reset current_time_burst and remove finished burst time
                self.CPU.current_time_burst = 0
                self.CPU.burst_times.pop(0)

                self.check_IO()

                # context switch
                self.is_in_context_switch = True
                self.CPU = EMPTY_PROCESS # dummy 
                self.process_holder = self.next_process_to_run()
                return

            # check time allotment
            if isinstance(current_queue, RoundRobinQueue) or isinstance(current_queue, FirstComeFirstServeQueue):
                if self.CPU.current_time_in_queue >= current_queue.time_allotment:
                    self.demoted_process = self.CPU

                    lower_queue = self.check_current_queue(self.CPU.current_queue + 1)
                    lower_queue.enqueue_process(self.CPU)

                    # reset current_time_in_queue since demoted
                    self.CPU.current_queue += 1
                    self.CPU.current_time_in_queue = 0
                    
                    self.check_IO()

                    # context switch
                    self.is_in_context_switch = True
                    self.CPU = EMPTY_PROCESS # dummy 
                    self.process_holder = self.next_process_to_run()
                    return

                # check quantum
                if current_queue == self.Q1:
                    if self.Q1.quantum_used >= self.Q1.quantum_time:
                        self.Q1.enqueue_process(self.CPU)
                        self.Q1.quantum_used = 0

                        self.check_IO()

                        # context switch
                        self.is_in_context_switch = True
                        self.CPU = EMPTY_PROCESS # dummy 
                        self.process_holder = self.next_process_to_run()
                        return

    def check_IO(self):
        if (self.IO.process_queue):
            for proc in self.IO.process_queue:
                current_queue = self.check_current_queue(proc.current_queue)

                if (proc.current_time_burst == proc.burst_times[0]):
                    self.IO.process_queue.remove(proc)
                    current_queue.enqueue_process(proc)

                    proc.burst_times.pop(0)
                    proc.current_time_burst = 0
        
