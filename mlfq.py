"""
CS 140 Project 1: MLFQ Scheduler in Python

Andal, David Vincent C. (CS 140 - THY/FUV)
De Leon, Angelo Luis (CS 140 - THY/FQR)
Eliserio, Seth Michael (CS 140 - THY/FUV)
Gonzales, Justin Andrei (CS 140 - THY/FUV)

AY 2024-2025
"""

from typing import Protocol, Any
from dataclasses import dataclass



"""
View
"""

@dataclass(frozen=True)
class User_input:
    N: int
    Q1: int
    Q2: int
    CS: int
    processes: list[dict[str, Any]]

@dataclass(frozen=True)
class Timestamp:
    time: int
    arriving_process: list[str] | None
    process_done: list[str] | None
    q1: list[str]
    q2: list[str]
    q3: list[str]
    is_in_context_switch: bool
    switching_process: str
    cpu: str | None
    io: list[str] | None
    demoted: str | None

@dataclass(frozen=True)
class ProcessesStats:
    process_names: list[str]
    completion_times: list[int]
    arrival_times: list[int]
    waiting_times: list[int]
    turnaround_times: list[int]
    avg_turnaround_time: float

class View:
    def __init__(self):
        ...
        
    def get_input(self):
        N = int(input())
        Q1 = int(input())
        Q2 = int(input())
        CS = int(input())
        processes = []
        for _ in range(N):
            process = input().split(";")
            process_dict = {
                "name": process[0],
                "arrival_time": int(process[1]),
                "bursts": [int(x) for x in process[2:]]
            }
            processes.append(process_dict)

        return User_input(N, Q1, Q2, CS, processes)

    def print_timestamp(self, ts: Timestamp) -> None:
        print(f"At Time = {ts.time}")

        if (ts.arriving_process != None):
            print(f"Arriving : [{', '.join(ts.arriving_process)}]")

        if (ts.process_done != None):
            for p in ts.process_done:
                print(f"{p} DONE")

        print(f"Queues : [{', '.join(ts.q1)}];[{', '.join(ts.q2)}];[{', '.join(ts.q3)}]")

        if (ts.is_in_context_switch):
            print(f"CPU : CONTEXT SWITCHING TO {ts.switching_process}")
        elif (ts.cpu == None):
            print(f"CPU : []")
        else:
            print(f"CPU : {ts.cpu}")
            
        if (ts.io != None):
            print(f"I/O : [{', '.join(ts.io)}]")

        if (ts.demoted != None):
            print(f"{ts.demoted} DEMOTED")
            
        print("")

    def print_statistics(self, processes_info: ProcessesStats) -> None:
        for i, process_name in enumerate(processes_info.process_names):
            completion_time = processes_info.completion_times[i]
            arrival_time = processes_info.arrival_times[i]
            ta_time = processes_info.turnaround_times[i]
            print(f"Turn-around time for Process {process_name} : {completion_time} - {arrival_time} = {ta_time} ms")

        avg_tt = processes_info.avg_turnaround_time
        print(f"Average Turn-around time = {int(avg_tt) if avg_tt.is_integer() else avg_tt} ms") 

        for i, process_name in enumerate(processes_info.process_names):
            waiting_time = processes_info.waiting_times[i]
            print(f"Waiting time for Process {process_name} : {waiting_time} ms")



"""
Model
"""

class Process:
    def __init__(self, name: str, arrival_time: int, burst_times: list[int]):
        self.name = name
        self.arrival_time = arrival_time
        self.current_queue: int = 1
        self.burst_times = burst_times
        self.total_burst = sum(burst_times)
        self.current_time_burst: int = 0
        self.current_time_in_queue: int = 0
        self.completion_time: int = -1
        self.waiting_time: int = -1

    def __lt__(self, other):
        self_burst = self.burst_times[0] - self.current_time_burst
        other_burst = other.burst_times[0] - other.current_time_burst 
        return self_burst < other_burst

# Represents an empty value
EMPTY_PROCESS = Process(" ", -1, [])

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
        self.process_queue.sort()

class IO:
    def __init__(self):
        self.process_queue: list[Process] = []

    def enqueue_process(self, p: Process) -> None:
        self.process_queue.append(p)

    def dequeue_process(self) -> Process:
        return self.process_queue.pop(0)
    

class MLFQ:
    def __init__(self, q1_time: int, q2_time: int, context_switch_time: int):
        self.curr_time = 0
        self.Q1 = RoundRobinQueue(q1_time)
        self.Q2 = FirstComeFirstServeQueue(q2_time)
        self.Q3 = ShortestJobFirst()
        self.IO = IO()
        self.CPU: Process = EMPTY_PROCESS # dummy 
        self.is_finish_running: bool = False

        self.context_switch_time = context_switch_time
        self.context_switch_time_used = 1    # time at context switch
        self.is_in_context_switch: bool = False
        self.process_holder: Process = EMPTY_PROCESS # holds the process to be context switched to

        self.processes: list[Process] = []
        self.incoming_processes: list[Process] = [] # stores new processes from input
        self.newlyaddedprocesses: list[Process] = []
        self.finished_processes: list[Process] = []
        self.demoted_process: Process = EMPTY_PROCESS

    def add_process(self, process: Process) -> None:
        self.processes.append(process)
        self.incoming_processes.append(process)

    def sort_incoming_processes(self) -> None:
        self.incoming_processes = sorted(self.incoming_processes, key=lambda p: (p.arrival_time, p.name))

    # given the queue number return the actual Queue object
    def check_current_queue(self, queue_index: int) -> Queue:
        if (queue_index == 1):
            return self.Q1
        elif (queue_index == 2):
            return self.Q2
        else: #queue_index == 3
            return self.Q3
            
    def next_process_to_run(self) -> Process:
        queue_index = 1
        
        while (queue_index < 4):
            current_queue = self.check_current_queue(queue_index)

            if current_queue.process_queue:
                return current_queue.process_queue[0]
            queue_index += 1
        
        return EMPTY_PROCESS

    # enters the newly arriving process to the MLFQ
    def check_arriving_processes(self):
        if (self.incoming_processes):
            processes_to_check = self.incoming_processes[:]
            for proc in processes_to_check:
                if(self.curr_time == proc.arrival_time):
                    self.incoming_processes.remove(proc)
                    self.Q1.enqueue_process(proc)
                    self.newlyaddedprocesses.append(proc)

    def is_quantum_done(self, curr_queue: Queue) -> bool:
        return isinstance(curr_queue, RoundRobinQueue) and self.Q1.quantum_used >= self.Q1.quantum_time

    def is_time_allotment_done(self, curr_queue: Queue) -> bool:
        if not isinstance(curr_queue, ShortestJobFirst):
            return self.CPU.current_time_in_queue >= curr_queue.time_allotment # ignore error
        return False

    def is_burst_done(self) -> bool:
        return self.CPU.current_time_burst >= self.CPU.burst_times[0]
    
    # return the queue of the highest priority process that returned to its queue
    # 4 if no process returned
    def check_IO(self) -> int:
        highest_queue_returned = 4
        if (self.IO.process_queue):
            io_processes = self.IO.process_queue[:]
            for proc in io_processes:
                current_queue = self.check_current_queue(proc.current_queue)
                # if process is done in IO
                if (proc.current_time_burst >= proc.burst_times[0]):
                    self.IO.process_queue.remove(proc)
                    # if process is done running
                    if (len(proc.burst_times) == 1):
                        proc.completion_time = self.curr_time
                        proc.waiting_time = proc.completion_time - proc.arrival_time - proc.total_burst
                        self.finished_processes.append(proc)
                    else:
                        current_queue.enqueue_process(proc)
                        highest_queue_returned = min(highest_queue_returned, proc.current_queue)

                        proc.burst_times.pop(0)
                        proc.current_time_burst = 0
        return highest_queue_returned
                
    # method to run to updated to the next timestamp
    def update_time_stamp(self) -> None:
        # increment time
        self.curr_time += 1

        # increment IO processes
        if (len(self.IO.process_queue) != 0):
            for proc in self.IO.process_queue:
                proc.current_time_burst += 1

        # during context switch
        just_finished_context_switch = False
        if (self.is_in_context_switch):
            # if context switch done
            if self.context_switch_time <= self.context_switch_time_used:
                self.CPU = self.process_holder
                self.check_current_queue(self.CPU.current_queue).dequeue_process()
                self.context_switch_time_used = 1
                self.is_in_context_switch = False
                just_finished_context_switch = True
            else:
                self.context_switch_time_used += 1

        # if CPU is empty
        is_cpu_currently_empty = True
        if self.CPU != EMPTY_PROCESS:
            is_cpu_currently_empty = False
            # must not increment if newly CSed
            if not just_finished_context_switch:
                # increment CPU process
                self.CPU.current_time_burst += 1
                self.CPU.current_time_in_queue += 1

                # if currently running process is in Q1
                if (self.CPU.current_queue == 1):
                    self.Q1.increment_quantum() 

        # enqueue newly arriving processes
        self.check_arriving_processes()

        self.next_process(is_cpu_currently_empty)

    # updates CPU process and check for what process to run
    def next_process(self, is_cpu_currently_empty: bool):
        if is_cpu_currently_empty:
            is_burst_done = False
            is_time_allotment_done = False
            is_quantum_done = False
        else:
            curr_queue = self.check_current_queue(self.CPU.current_queue)

            is_burst_done = self.is_burst_done()
            is_time_allotment_done = self.is_time_allotment_done(curr_queue)
            is_quantum_done = self.is_quantum_done(curr_queue)

        is_process_done = False
        if is_burst_done:
            # if process is finished
            if len(self.CPU.burst_times) == 1:
                self.CPU.completion_time = self.curr_time
                self.CPU.waiting_time = self.CPU.completion_time - self.CPU.arrival_time - self.CPU.total_burst
                self.finished_processes.append(self.CPU)
                is_process_done = True
            else: # enqueue to IO
                self.IO.enqueue_process(self.CPU)
                self.CPU.burst_times.pop(0)
                self.CPU.current_time_burst = 0
                self.CPU.current_time_in_queue = 0

            # reset quantum
            if (self.CPU.current_queue == 1):
                self.Q1.quantum_used = 0

        # reset quantum
        if is_quantum_done:
            self.Q1.quantum_used = 0

        # enqueue back to Q1
        if is_quantum_done and not is_time_allotment_done and not is_burst_done:
            self.Q1.enqueue_process(self.CPU)

        # process is demoted
        if is_time_allotment_done and not is_process_done:
            self.demoted_process = self.CPU
            lower_queue = self.check_current_queue(self.CPU.current_queue + 1)
            self.CPU.current_queue += 1
            self.CPU.current_time_in_queue = 0

            if not is_burst_done:
                lower_queue.enqueue_process(self.CPU)

        highest_queue_returned = self.check_IO()

        self.Q3.sort_queue() # sorts Q3 by shortest job first

        # context switch will occur
        next_proc = self.next_process_to_run()
        if is_burst_done or is_time_allotment_done or is_quantum_done:
            # there is still a process in the queues
            if next_proc != EMPTY_PROCESS:
                # if there is context switch time
                if self.context_switch_time and (self.CPU != next_proc):            
                    self.is_in_context_switch = True
                    self.CPU = EMPTY_PROCESS
                    self.process_holder = next_proc
                else: # no cs time or next_process to run is same process
                    self.CPU = next_proc
                    self.check_current_queue(self.CPU.current_queue).dequeue_process()
            else: # CPU is idle
                self.CPU = EMPTY_PROCESS
        # Check for a higher priority process
        elif highest_queue_returned < self.CPU.current_queue or (next_proc != EMPTY_PROCESS and next_proc.current_queue < self.CPU.current_queue):
            self.check_current_queue(self.CPU.current_queue).enqueue_process(self.CPU)
            # if there is context switch time
            if self.context_switch_time:
                self.is_in_context_switch = True
                self.CPU = EMPTY_PROCESS
                self.process_holder = next_proc
            else:
                self.CPU = next_proc
                self.check_current_queue(self.CPU.current_queue).dequeue_process()
        # No context switch needed if next process is same process
        elif is_cpu_currently_empty and not self.is_in_context_switch and next_proc != EMPTY_PROCESS:
            self.CPU = next_proc
            self.check_current_queue(self.CPU.current_queue).dequeue_process()



"""
Controller
"""

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

        demoted = None if self._model.demoted_process.arrival_time == -1 else self._model.demoted_process.name
        self._model.demoted_process = EMPTY_PROCESS

        self._view.print_timestamp(
            Timestamp(time, arriving_processes, processes_done, q1, q2, q3, is_in_context_switch, switching_process, cpu, io, demoted)
        )

    def get_statistics(self):
        processes = sorted(self._model.processes, key=lambda p: p.name)
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

    def input_to_model(self, inputs: User_input):
        processes = inputs.processes
        for p in processes:
            self._model.add_process(Process(p["name"], p["arrival_time"], p["bursts"]))
        

    def run(self, inputs: User_input):
        # gets inputs and sends them to the MLFQ
        self.input_to_model(inputs)

        self._model.sort_incoming_processes()
        self._model.processes = sorted(self._model.processes, key=lambda p: p.name)

         # for time = 0
        self._model.check_arriving_processes()
        self._model.CPU = self._model.Q1.dequeue_process()
        self.get_timestamp()

        # loops until no more incoming proceses / Q1 to Q3 is empty / IO is empty / CPU is empty
        while (self._model.incoming_processes or self._model.Q1.process_queue or self._model.Q2.process_queue or self._model.Q3.process_queue or self._model.IO.process_queue or (self._model.CPU != EMPTY_PROCESS and not self._model.is_in_context_switch)):
            self._model.update_time_stamp()
            self.get_timestamp()

        print("SIMULATION DONE\n")
        
        self.get_statistics()



if __name__ == "__main__":
    view = View()
    inputs = view.get_input()
    model = MLFQ(inputs.Q1, inputs.Q2, inputs.CS)
    controller = Controller(model, view)
    controller.run(inputs)