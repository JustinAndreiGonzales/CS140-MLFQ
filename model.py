from typing import Protocol


class Process:
    def __init__(self, name: str, arrival_time: int, burst_times: list[int]):
        self.name = name
        self.arrival_time = arrival_time
        self.current_queue: int = 1
        self.burst_times = burst_times
        self.total_burst = sum(burst_times)
        self.current_time_burst: int = 0
        self.current_time_in_queue: int = 0
        self.completion_time: int = -1 # what is starting value?
        self.waiting_time: int = -1 # what is starting value?

    def __lt__(self, other):
        self_burst = self.burst_times[0] - self.current_time_burst
        other_burst = other.burst_times[0] = other.current_time_burst 
        return self_burst < other_burst

    # @property
    # def get_arrival_time(self) -> int:
    #     return self.get_arrival_time
    
    # def increment_time_burst(self) -> None:
    #     self.current_time_burst += 1

    # def increment_allotment_in_queue(self) -> None:
    #     self.current_time_in_queue += 1

    # def dequeue_burst_time(self):
    #     ...

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
        self.process_holder: Process = EMPTY_PROCESS # dummy 

        self.processes: list[Process] = []
        self.incoming_processes: list[Process] = []
        self.newlyaddedprocesses: list[Process] = []
        self.finished_processes: list[Process] = []
        self.demoted_process: Process = EMPTY_PROCESS

    # def dequeue_process(self, queue: Queue) -> Process:
    #     return queue.dequeue_process()

    def add_process(self, process: Process) -> None:
        self.processes.append(process)
        self.incoming_processes.append(process)

    def sort_incoming_processes(self) -> None:
        self.incoming_processes = sorted(self.incoming_processes, key=lambda p: (p.arrival_time, p.name))

    def check_current_queue(self, queue_index: int) -> Queue:
        if (queue_index == 1):
            return self.Q1
        elif (queue_index == 2):
            return self.Q2
        else: #queue_index == 3
            return self.Q3
            
    # edited queue_index
    def next_process_to_run(self) -> Process:
        queue_index = 1
        
        while (queue_index < 4):
            current_queue = self.check_current_queue(queue_index)

            if current_queue.process_queue:
                return current_queue.process_queue[0]
            queue_index += 1
        
        return EMPTY_PROCESS # dummy
    
    # def next_process_to_run(self) -> Process:
    #     queue_index = self.CPU.current_queue
        
    #     while (queue_index < 3):
    #         current_queue = self.check_current_queue(queue_index)

    #         if current_queue.process_queue:
    #             return current_queue.process_queue[0]
    #         queue_index += 1
        
    #     return EMPTY_PROCESS # dummy

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
        # changed to shortestjobfirst
        if not isinstance(curr_queue, ShortestJobFirst):
            return self.CPU.current_time_in_queue >= curr_queue.time_allotment # ignore error
        return False

    def is_burst_done(self) -> bool:
        return self.CPU.current_time_burst >= self.CPU.burst_times[0]
    
    # edited highest return
    def check_IO(self) -> int:
        highest_queue_returned = 4
        if (self.IO.process_queue):
            io_processes = self.IO.process_queue[:]
            for proc in io_processes:
                current_queue = self.check_current_queue(proc.current_queue)

                if (proc.current_time_burst >= proc.burst_times[0]):
                    self.IO.process_queue.remove(proc)
                    # if process is done
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
            print(f"CS {self.context_switch_time_used}/{self.context_switch_time}") # <--- debugging
            if self.context_switch_time <= self.context_switch_time_used:
                self.CPU = self.process_holder
                self.check_current_queue(self.CPU.current_queue).dequeue_process()
                # changed to 1 (isip better way)
                self.context_switch_time_used = 1
                self.is_in_context_switch = False
                # added condition if newly finished cs
                just_finished_context_switch = True
            else:
                self.context_switch_time_used += 1
            # di dapat mag return 
            # madami pa ichecheck sa baba
            # return

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

        # # if CPU is empty
        # if (self.CPU == EMPTY_PROCESS):
        #     return

        # # increment CPU process
        # self.CPU.current_time_burst += 1
        # self.CPU.current_time_in_queue += 1

        # # if currently running process is in Q1
        # if (self.CPU.current_queue == 1):
        #     self.Q1.increment_quantum() 

        # # enqueue newly arriving processes
        # self.check_arriving_processes()

        # self.next_process()

    # added bool
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

        #added
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
                # reset burst and allotment and remove finished burst time
                self.CPU.burst_times.pop(0)
                self.CPU.current_time_burst = 0
                self.CPU.current_time_in_queue = 0

            # reset quantum
            if (self.CPU.current_queue == 1):
                self.Q1.quantum_used = 0

        if is_quantum_done:
            self.Q1.quantum_used = 0

        # edited added not is_burst_done
        if is_quantum_done and not is_time_allotment_done and not is_burst_done:
            self.Q1.enqueue_process(self.CPU)

        if is_time_allotment_done and not is_process_done:
            self.demoted_process = self.CPU
            lower_queue = self.check_current_queue(self.CPU.current_queue + 1)
            self.CPU.current_queue += 1
            self.CPU.current_time_in_queue = 0
            # added condition
            if not is_burst_done:
                lower_queue.enqueue_process(self.CPU)

        highest_queue_returned = self.check_IO()

        self.Q3.sort_queue()

        # context switch will occur
        if is_burst_done or is_time_allotment_done or is_quantum_done:
            next_proc = self.next_process_to_run()
            # there is process in queue
            if next_proc != EMPTY_PROCESS:
                # if there is context switch time
                if self.context_switch_time and (self.CPU != next_proc):            
                    self.is_in_context_switch = True
                    self.CPU = EMPTY_PROCESS
                    self.process_holder = next_proc
                else: # no cs time or next_process to run is same process
                    self.CPU = next_proc
                    self.check_current_queue(self.CPU.current_queue).dequeue_process()
            else:
                self.CPU = EMPTY_PROCESS
        # added elif (priority higher queue)
        elif highest_queue_returned < self.CPU.current_queue:
            next_proc = self.next_process_to_run()
            self.check_current_queue(self.CPU.current_queue).enqueue_process(self.CPU)
            if self.context_switch_time:
                self.is_in_context_switch = True
                self.CPU = EMPTY_PROCESS
                self.process_holder = next_proc
            else:
                self.CPU = next_proc
                self.check_current_queue(self.CPU.current_queue).dequeue_process()
        # added elif if cpu currently empty (no cs needed?)
        elif is_cpu_currently_empty and not self.is_in_context_switch:
            self.CPU = self.next_process_to_run()
            self.check_current_queue(self.CPU.current_queue).dequeue_process()
        # elif self.next_process_to_run() == self.CPU:
        #     self.CPU = self.next_process_to_run()
        #     self.check_current_queue(self.CPU.current_queue).dequeue_process()
