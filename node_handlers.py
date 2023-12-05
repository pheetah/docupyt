from abc import ABC, abstractmethod

from doctree import ActivityNode, EpcDiagram, EpcNode, EventNode, IfNode
from settings.language import Keywords


class NodeHandler(ABC):
    def __init__(self, token: str) -> None:
        self._token = token

    def _get_after(self, string: str, keyword: str):
        return string.split(keyword, 1)[1]

    @abstractmethod
    def handle(self, diagram: EpcDiagram) -> EpcDiagram:
        raise NotImplementedError("This type of node is not supported.")


class MainFlowHandler(NodeHandler):
    @property
    def keyword() -> Keywords:
        raise NotImplementedError("No keyword for the handler!")

    @abstractmethod
    def _get_node(self, description: str) -> EpcNode:
        pass

    def handle(self, diagram: EpcDiagram) -> EpcDiagram:
        if self.keyword in self._token:
            raw_action = self._get_after(self._token, self.keyword)
            current_node = self._get_node(description=raw_action)
            diagram.push(current_node)

            return diagram


class EventHandler(MainFlowHandler):
    @property
    def keyword() -> Keywords:
        return Keywords.EVENT

    def _get_node(self, description: str) -> EpcNode:
        return EventNode(description=description)


class ActivityHandler(MainFlowHandler):
    @property
    def keyword() -> Keywords:
        return Keywords.ACTIVITY

    def _get_node(self, description: str) -> EpcNode:
        return ActivityNode(description=description)


class ElseHandler(NodeHandler):
    def __init__(self, token: str, current_node: IfNode) -> None:
        super().__init__(token)
        self._node_current = current_node

    @property
    def keyword() -> Keywords:
        return Keywords.ELSE

    def _get_node(self, description: str) -> EpcNode:
        return IfNode(description=description)

    def handle(self, diagram: EpcDiagram):
        # add current node as a branch in if
        self._node_current.branches.append(diagram.head)
        # create a new diagram to be a new branch in if statement
        return EpcDiagram()


class EndifHandler(NodeHandler):
    def __init__(self, token: str, current_node: IfNode) -> None:
        super().__init__(token)
        self._node_current = current_node

    @property
    def keyword() -> Keywords:
        return Keywords.ENDIF

    def _get_node(self, description: str) -> EpcNode:
        return IfNode(description=description)

    def handle(self, diagram: EpcDiagram):
        # add current node as a branch in if
        self._node_current.branches.append(diagram.head)
        # create a new diagram to be a new branch in if statement
        return diagram


class MainFlowHandlerFactory:
    def __new__(cls, token: str) -> MainFlowHandler:
        if Keywords.ACTIVITY in token:
            return ActivityHandler(token=token)
        elif Keywords.EVENT in token:
            return EventHandler(token=token)
        else:
            NotImplementedError("This keyword is unsupported in main flow.")


class IfFlowHandlerFactory:
    pass
