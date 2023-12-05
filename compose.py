from code_tokenize.tokens import TokenSequence
from pygraphviz import AGraph

from doctree import EpcDiagram, IfNode
from logs import log
from node_handlers import MainFlowHandler, MainFlowHandlerFactory
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
                # raw_action = self._get_after(stringified_token, Keywords.IF)
                if_node = IfNode("!")
                inner_diagram = EpcDiagram()
                for idx, tok in enumerate(parsed[index:]):
                    stringified_token = str(tok)
                    main_flow_handler: MainFlowHandler = MainFlowHandlerFactory(
                        token=stringified_token
                    )
                    main_flow_handler.handle(diagram=inner_diagram)
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

            main_flow_handler: MainFlowHandler = MainFlowHandlerFactory(
                token=stringified_token
            )
            main_flow_handler.handle(diagram=self._diagram)

    def compose(self):
        current_node = self._diagram.head
        while current_node:
            current_node.draw_line(G)
            current_node = current_node.next

        G.layout()
        G.draw("_outputs/epc.png", prog="dot")

        log.info("Done.")
