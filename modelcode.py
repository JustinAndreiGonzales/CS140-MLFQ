def check_current_queue(self, queue_index: int) -> Queue:
    if (queue_index == 1):
        return self.Q1
    elif (queue_index == 2):
        return self.Q2
    else: #queue_index == 3
        return self.Q3

def check_arriving_processes(self):
    if (self.incoming_processes):
        processes_to_check = self.incoming_processes[:]
        for proc in processes_to_check:
            if(self.curr_time == proc.arrival_time):
                self.incoming_processes.remove(proc)
                self.Q1.enqueue_process(proc)
                self.newlyaddedprocesses.append(proc)

def next_process_to_run(self) -> Process:
    queue_index = self.CPU.current_queue
    
    while (queue_index < 3):
        current_queue = self.check_current_queue(queue_index)

        if current_queue.process_queue:
            return current_queue.dequeue_process()
        queue_index += 1
    
    return Process(" ", -1, []) # dummy

def is_quantum_done(self, curr_queue: Queue) -> bool:
    return isinstance(curr_queue, RoundRobinQueue) and self.Q1.quantum_used >= self.Q1.quantum_time:

def is_time_allotment_done(self, curr_queue: Queue) -> bool:
    if not isinstance(curr_queue, ShortestJobFirst):
        return self.CPU.current_time_in_queue >= curr_queue.time_allotment
    return False

def is_burst_done(self) -> bool:
    return self.CPU.current_time_burst >= self.CPU.burst_times[0]

def check_IO(self):
    if (self.IO.process_queue):
        io_processes = self.IO.process_queue[:]
        for proc in io_processes:
            current_queue = self.check_current_queue(proc.current_queue)

            if (proc.current_time_burst == proc.burst_times[0]):
                self.IO.process_queue.remove(proc)
                current_queue.enqueue_process(proc)

                proc.burst_times.pop(0)
                proc.current_time_burst = 0
            
            # if natapos sa IO yung process

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
            self.check_current_queue(self.CPU.current_queue).dequeue_process()
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
    self.check_arriving_processes()

    self.next_process()

def next_process(self):
    curr_queue = self.check_current_queue(self.CPU.current_queue)
    is_burst_done = self.is_burst_done()
    is_time_allotment_done = self.is_time_allotment_done(curr_queue)
    is_quantum_done = self.is_quantum_done(curr_queue)

    if is_burst_done:
        if len(self.CPU.burst_times) == 1:
            # add completion time
            # add waiting time
            self.finished_processes.append(self.CPU)
        else:
            self.IO.enqueue_process(self.CPU)
            # reset burst and allotment and remove finished burst time
            self.CPU.burst_times.pop(0)
            self.CPU.current_time_burst = 0
            self.CPU.current_time_in_queue = 0

    if is_quantum_done:
        self.Q1.quantum_used = 0
    if is_quantum_done and not is_time_allotment_done:
        self.Q1.enqueue_process(self.CPU)
    if is_time_allotment_done:
        self.demoted_process = self.CPU
        lower_queue = self.check_current_queue(self.CPU.current_queue + 1)
        lower_queue.enqueue_process(self.CPU)
        self.CPU.current_queue += 1
        self.CPU.current_time_in_queue = 0

    self.check_IO()

    if is_burst_done or is_time_allotment_done or is_quantum_done:
        next_proc = self.next_process_to_run()
        if next_proc != EMPTY_PROCESS:
            if self.context_switch_time:            
                self.is_in_context_switch = True
                self.CPU = EMPTY_PROCESS
                self.process_holder = next_proc
            else:
                self.CPU = next_proc
                self.check_current_queue(self.CPU.current_queue).dequeue_process()
        else:
            self.CPU = EMPTY_PROCESS
