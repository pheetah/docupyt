import copy
from uuid import uuid4

from code_tokenize.tokens import TokenSequence
from pygraphviz import AGraph

from doctree import ActivityNode, EpcDiagram, EpcNode, EventNode, IfNode
from logs import log
from settings.language import Keywords

G = AGraph(directed=True)


class DiagramNodeAdder:
    def _get_after(self, string: str, keyword: str):
        return string.split(keyword, 1)[1]

    def _handle_activity(self, token: str, diagram: EpcDiagram) -> EpcNode:
        if Keywords.ACTIVITY in token:
            raw_action = self._get_after(token, Keywords.ACTIVITY)
            diagram.push(ActivityNode(description=raw_action))

    def _handle_event(self, token: str, diagram: EpcDiagram) -> EpcNode:
        if Keywords.EVENT in token:
            raw_action = self._get_after(token, Keywords.EVENT)
            diagram.push(EventNode(description=raw_action))

    def _handle_if(self, sequence: TokenSequence, depth=0) -> EpcNode:
        first_element = str(sequence.pop(0))
        if Keywords.IF not in str(first_element):
            return None, None

        if_node = copy.deepcopy(IfNode(uuid4()))
        current_branch = copy.deepcopy(EpcDiagram())

        depth_inner_processed_index = None
        depth_latest_index = None

        for index, token_raw in enumerate(sequence):
            token = str(token_raw)

            if (
                depth_latest_index and depth_inner_processed_index
            ) and index < depth_latest_index + depth_inner_processed_index + 1:
                continue
            else:
                depth_inner_processed_index = None
                depth_latest_index = None

            if Keywords.IF in token:
                # eğer diagramı içeri geçersen hem içteki hem dıştaki çizecek.
                depth_latest_index = index
                depth_inner_processed_index, depth_if = self._handle_if(
                    sequence=sequence[index:], depth=depth + 1
                )

                if depth_inner_processed_index:
                    current_branch.push(depth_if)
                    continue

            self._handle_activity(token=token, diagram=current_branch)
            self._handle_event(token=token, diagram=current_branch)

            if Keywords.ELSE in token:
                if_node.branches.append(current_branch.head)
                current_branch = EpcDiagram()

            if Keywords.ENDIF in token:
                if_node.branches.append(current_branch.head)
                return index + 1, if_node

        return None, None

    def add_nodes(self, token_sequence: str) -> EpcDiagram:
        diagram = EpcDiagram()
        inner_processed_index = None
        latest_index = None
        for index, token_raw in enumerate(token_sequence):
            token = str(token_raw)

            if (
                latest_index and inner_processed_index
            ) and index < latest_index + inner_processed_index + 1:
                continue

            inner_processed_index, if_node = self._handle_if(
                sequence=token_sequence[index:]
            )

            if inner_processed_index:
                latest_index = index
                diagram.push(if_node)
                continue

            self._handle_activity(token=token, diagram=diagram)
            self._handle_event(token=token, diagram=diagram)

        return diagram


class Composer:
    _endix: int = None

    def _get_after(self, string: str, keyword: str):
        return string.split(keyword, 1)[1]

    def _struct(self, parsed: TokenSequence) -> EpcDiagram:
        node_adder = DiagramNodeAdder()
        diagram = node_adder.add_nodes(token_sequence=parsed)

        return diagram

    def compose(self, export_to: str, parsed: TokenSequence):
        diagram = self._struct(parsed=parsed)
        current_node = diagram.head

        while current_node:
            current_node.draw_line(G)
            current_node = current_node.next

        G.layout()
        G.draw(export_to, prog="dot")

        log.info("Done.")
