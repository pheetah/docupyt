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

    @abstractmethod
    def add_node(self, pygraph: pgv.AGraph, description: str):
        pass

    def draw_line(self, pygraph: pgv.AGraph, end_id: str = None):
        self.add_node(pygraph, self._description)
        if self.next:
            pygraph.add_edge(self._description, self.next._description)


class ActivityNode(EpcNode):
    def add_node(self, pygraph: pgv.AGraph, description: str):
        pygraph.add_node(
            description,
            color="palegoldenrod",
            shape="polygon",
            fontcolor="black",
            style="filled",
            fontsize=16,
            width=2,
        )


class EventNode(EpcNode):
    def add_node(self, pygraph: pgv.AGraph, description: str):
        pygraph.add_node(
            description,
            color="darkred",
            shape="octagon",
            fontcolor="white",
            style="filled",
            fontsize=16,
            width=2,
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
            description, label="X", color="gray", height="0.2", width="0.2"
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
    length: int

    def __init__(self) -> None:
        self.head = None
        self.tail = None
        self.length = 0

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
