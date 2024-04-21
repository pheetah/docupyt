from dataclasses import dataclass
from parser.doctree_parser import Parser

from code_tokenize.tokens import TokenSequence
from pygraphviz import AGraph

from clusterer import Cluster
from compose import Composer
from logs import log


@dataclass
class FileFormat:
    input_path: str
    output_path: str


# Façade
class DocupytClient:
    def __init__(
        self, parser: Parser = Parser(), composer: Composer = Composer()
    ) -> None:
        self._parser = parser
        self._composer = composer

    def _compose_and_draw(self, pygraph: AGraph, flow: TokenSequence):
        # act: compose diagram
        diagram = self._composer.compose(parsed=flow)

        # act: draw diagram
        current_node = diagram.head
        while current_node:
            current_node.draw_line(pygraph)
            current_node = current_node.next

        return diagram

    def _compose_and_draw_inner(
        self, pygraph: AGraph, flow: TokenSequence, name: str
    ):
        pygraph.add_subgraph(
            name=name, label=name, cluster=True, labelloc="t", fontcolor="blue"
        )
        sg = pygraph.get_subgraph(name=name)

        returned = self._compose_and_draw(pygraph=sg, flow=flow)
        return returned

    def draw_epc(self, file_format: list[FileFormat]):
        cluster = Cluster()
        cluster.extract_flows(
            file_name_list=[file.input_path for file in file_format]
        )

        main_flows = [flow.tokens for flow in cluster._main_flows]
        for index, main_flow in enumerate(main_flows):
            G = AGraph(directed=True, compound=True)
            current_main_process = self._compose_and_draw(
                pygraph=G, flow=main_flow
            )
            inner_flows = [
                flow
                for flow in cluster._inner_flows
                if flow.name in current_main_process.inner_flow_names
            ]
            for inner_flow in inner_flows:
                self._compose_and_draw_inner(
                    pygraph=G, flow=inner_flow.tokens, name=inner_flow.name
                )

            file = file_format[index]
            G.layout()
            G.draw(
                f"./_outputs/{cluster._main_flows[index].name}.png",
                prog="dot",
            )

            log.info(msg=f"{file.output_path} - Done.")
