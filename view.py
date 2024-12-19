
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Input:
    N: int
    Q1: int
    Q2: int
    CS: int
    processes: list[dict[str, Any]]

@dataclass(frozen=True)
class Timestamp:
    time: int
    arriving_process: list[str] | None
    process_done: str | None
    q1: list[str]
    q2: list[str]
    q3: list[str]
    cpu: str
    io: list[str] | None
    demoted: str | None

@dataclass(frozen=True)
class ProcessesStats:
    process_names: list[str]
    completion_times: list[int]
    arrival_times: list[int]
    waiting_times: list[int]
    turnaround_times: list[int]
    avg_turnaround_time = float

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

        return Input(N, Q1, Q2, CS, processes)

    def print_timestamp(self, ts: Timestamp) -> None:
        print(f"At Time = {ts.time}")
        if (ts.arriving_process != None):
            print(f"Arriving : [{", ".join(ts.arriving_process)}]")
        if (ts.process_done != None):
            print(f"{ts.process_done} DONE")
        print(f"Queues : [{", ".join(ts.q1)}];[{", ".join(ts.q2)}];[{", ".join(ts.q3)}]")
        print(f"CPU : {ts.cpu}")
        if (ts.io != None):
            print(f"I/O : [{", ".join(ts.io)}]")
        if (ts.demoted != None):
            print(f"{ts.demoted} DEMOTED\n")

    def print_statistics(self, processes_info: ProcessesStats) -> None:
        print("SIMULATION DONE\n")
        for i, process_name in enumerate(processes_info.process_names):
            completion_time = processes_info.completion_times[i]
            arrival_time = processes_info.arrival_times[i]
            ta_time = processes_info.turnaround_times[i]
            print(f"Turn-around time for Process {process_name} : {completion_time} - {arrival_time} = {ta_time[i]}")

        print(f"Average Turn-around time = {processes_info.avg_turnaround_time}") 

        for i, process_name in enumerate(processes_info.process_names):
            waiting_time = processes_info.waiting_times[i]
            print(f"Waiting time for Process {process_name} : {waiting_time}")
