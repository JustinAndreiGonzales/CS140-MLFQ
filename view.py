
from dataclasses import dataclass


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


class View:
    def __init__(self):
        ...

    def get_input(self):
        ...

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

    def print_statistics(self) -> None:
        ...
        # ano input?

view = View()

t1 = Timestamp(4, ['A', 'B'], 'C', [], ['A'], ['B', 'C'],
               'D', ['A', 'B'], 'Z')

view.print_timestamp(t1)
view.print_timestamp(t1)