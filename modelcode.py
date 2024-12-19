







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
