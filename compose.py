from code_tokenize.tokens import TokenSequence
from pygraphviz import AGraph

from doctree import ActivityNode, EpcDiagram, EventNode, IfNode
from logs import log
from settings.language import Keywords

G = AGraph(directed=True)


class Composer:
    _endix: int = None

    def __init__(self) -> None:
        self._diagram = EpcDiagram()

    def _get_after(self, string: str, keyword: str):
        return string.split(keyword, 1)[1]

    def struct(self, parsed: TokenSequence, current_node=None):
        for index, token in enumerate(parsed):
            stringified_token = str(token)

            if Keywords.IF in str(token):
                raw_action = self._get_after(stringified_token, Keywords.IF)
                if_node = IfNode("!")
                inner_diagram = EpcDiagram()
                for idx, tok in enumerate(parsed[index:]):
                    stringified_token = str(tok)
                    if Keywords.ACTIVITY in str(tok):
                        raw_action = self._get_after(
                            stringified_token, Keywords.ACTIVITY
                        )
                        current_node = ActivityNode(raw_action)
                        inner_diagram.push(current_node)
                    if Keywords.EVENT in str(tok):
                        raw_action = self._get_after(stringified_token, Keywords.EVENT)
                        current_node = EventNode(raw_action)
                        inner_diagram.push(current_node)

                    if Keywords.ELSE in str(tok):
                        if_node.branches.append(inner_diagram.head)
                        inner_diagram = EpcDiagram()

                    if Keywords.ENDIF in str(tok):
                        if_node.branches.append(inner_diagram.head)
                        self._endix = index + idx + 1
                        break

            if self._endix:
                if index < self._endix:
                    continue
                else:
                    self._diagram.push(if_node)
                    for branch in if_node.branches:
                        while branch:
                            branch = branch.next
                    self._endix = None

            if Keywords.ACTIVITY in str(token):
                raw_action = self._get_after(stringified_token, Keywords.ACTIVITY)
                current_node = ActivityNode(raw_action)
                self._diagram.push(current_node)
                continue

            if Keywords.EVENT in str(token):
                raw_action = self._get_after(stringified_token, Keywords.EVENT)
                current_node = EventNode(raw_action)
                self._diagram.push(current_node)
                continue

    def compose(self):
        current_node = self._diagram.head
        while current_node:
            current_node.draw_line(G)
            current_node = current_node.next

        G.layout()
        G.draw("_outputs/epc.png", prog="dot")

        log.info("Done.")
