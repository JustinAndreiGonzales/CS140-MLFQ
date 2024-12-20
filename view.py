
from dataclasses import dataclass
from typing import Any

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