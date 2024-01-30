from abc import ABC, abstractmethod
from typing import Optional, Self
from uuid import uuid4

import pygraphviz as pgv


class EpcNode(ABC):
    _description: str
    _start: str
    _end: str
    next: Optional[Self]

    def __init__(self, description: str, next: Self | None = None) -> None:
        self._description = description
        self.next = next
        self._start = description
        self._end = description
        self._database = None

    def set_database_connection(self, database: str):
        self._database = database

    def add_db_node(self, pygraph: pgv.AGraph, description: str, group: str):
        id = uuid4()
        pygraph.add_node(
            id,
            label=description,
            color="orange",
            height="0.25",
            width="0.10",
            shape="cylinder",
            style="filled",
            margin="0.1",
            fontcolor="white",
            group=group,
        )

        return id

    @abstractmethod
    def add_node(self, pygraph: pgv.AGraph, description: str):
        pass

    def draw_line(self, pygraph: pgv.AGraph, end_id: str = None):
        self.add_node(pygraph, self._description)
        if self.next:
            pygraph.add_edge(self._description, self.next._description)

        if self._database:
            graph = pygraph.add_subgraph(
                [self._description, self._database],
                name=self._description + self._database,
            )
            db_id = self.add_db_node(
                pygraph=graph, description=self._database, group=self._description
            )
            graph.add_edge(self._description, db_id)


class ActivityNode(EpcNode):
    def __init__(self, description: str, next: Self | None = None) -> None:
        super().__init__(description, next)
        self._incoming_api_calls: list[str] = []
        self._outgoing_api_calls: list[str] = []

    def _parse_api_call(self, api_call: str) -> list[str]:
        return list(map(lambda x: x.lstrip().rstrip(), api_call.split(",")))

    def set_incoming_api_call(self, api_call: str):
        calls = self._parse_api_call(api_call)
        self._incoming_api_calls = calls

    def set_outgoing_api_call(self, api_call: str):
        calls = self._parse_api_call(api_call)
        self._outgoing_api_calls = calls

    def add_api_call_node(
        self,
        pygraph: pgv.AGraph,
        incoming_api_calls: list[str],
        outgoing_api_calls: list[str],
        group: str,
    ):
        id = uuid4()

        incoming = "".join(
            [
                f"<tr> <td> <i> &#8592; {call.lstrip().rstrip()} </i> </td> </tr>"
                for call in incoming_api_calls
            ]
        )
        outgoing = "".join(
            [
                f"<tr> <td> <i> &#8594; {call.lstrip().rstrip()} </i> </td> </tr>"
                for call in outgoing_api_calls
            ]
        )

        label = (
            "<<table border='0' cellborder='1' cellspacing='0'>"
            "<tr> <td> API CALL </td> </tr>"
            f"{outgoing}"
            f"{incoming}"
            "</table>>"
        )

        pygraph.add_node(
            id,
            label=label,
            color="orange2",
            height=0.45,
            width=0.2,
            shape="component",
            margin="0.1",
            fontcolor="royalblue3",
            fontsize=12,
            group=group,
        )

        return id

    def add_node(self, pygraph: pgv.AGraph, description: str):
        pygraph.add_node(
            description,
            color="palegoldenrod",
            shape="polygon",
            fontcolor="black",
            style="filled",
            fontsize=16,
            width=4,
            group="1",
        )

    def draw_line(self, pygraph: pgv.AGraph, end_id: str = None):
        super().draw_line(pygraph, end_id)

        if self._incoming_api_calls or self._outgoing_api_calls:
            cluster = (
                [self._description]
                + self._incoming_api_calls
                + self._outgoing_api_calls
            )
            graph = pygraph.add_subgraph(
                cluster,
                name=self._description + "apicalls",
            )
            api_call_id = self.add_api_call_node(
                pygraph=graph,
                incoming_api_calls=self._incoming_api_calls,
                outgoing_api_calls=self._outgoing_api_calls,
                group=self._description,
            )
            graph.add_edge(self._description, api_call_id)


class EventNode(EpcNode):
    def add_node(self, pygraph: pgv.AGraph, description: str):
        pygraph.add_node(
            description,
            color="darkred",
            shape="octagon",
            fontcolor="white",
            style="filled",
            width=1.0,
            height=0.6,
            fixedsize=False,
            group="1",
        )


class ProcessNode(EpcNode):
    def add_node(self, pygraph: pgv.AGraph, description: str):
        pygraph.add_node(
            description,
            color="darkblue",
            shape="polygon",
            fontcolor="white",
            style="filled",
            fontsize=16,
            width=4,
            group="1",
        )


class IfNode(EpcNode):
    branches: list[EpcNode]

    def __init__(
        self, description: str, next: Self | None = None, branches: list[EpcNode] = []
    ) -> None:
        super().__init__(description, next)
        self.branches = branches

    def add_node(self, pygraph: pgv.AGraph, description: str):
        pygraph.add_node(
            description,
            label="X",
            color="gray",
            height="0.2",
            width="0.2",
            group="1",
        )

    def draw_line(self, pygraph: pgv.AGraph, end_id: str = None):
        if self.branches:
            self._end = uuid4()
            self.add_node(pygraph, self._start)
            self.add_node(pygraph, self._end)

        for branch in self.branches:
            pygraph.add_edge(self._description, branch._description)

            while branch:
                branch.draw_line(pygraph=pygraph, end_id=self._end)

                if not branch.next:
                    pygraph.add_edge(branch._end, self._end)
                branch = branch.next

            if self.next:
                pygraph.add_edge(self._end, self.next._description)

            if not self.next and end_id:
                pygraph.add_edge(self._end, end_id)


class EpcDiagram:
    head: EpcNode
    tail: EpcNode
    inner_flow_names: list[str]
    length: int

    def __init__(self, name: str = "EPC") -> None:
        self.name = name
        self.head = None
        self.tail = None
        self.length = 0
        self.inner_flow_names = []

    def add(self, node: EpcNode):
        self.head = node

    def push(self, node):
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node

        self.length += 1

        return self
