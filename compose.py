import copy
import re
from uuid import uuid4

from code_tokenize.tokens import TokenSequence

from doctree import ActivityNode, EpcDiagram, EpcNode, EventNode, IfNode, ProcessNode
from settings.language import (
    NODE_KEYWORDS,
    SYMBOLS,
    ArchitecturalKeywords,
    ClusterKeywords,
    ContextKeywords,
    Keywords,
)


class DiagramNodeAdder:
    def _process_regex_sentitivity(self, keyword: str):
        processed = keyword.replace("[", r"\[").replace("]", r"\]")
        return processed

    def _search_exact_regex(self, regex: str, token: str):
        result = re.search(regex, token)
        return result[0] if result else None

    def _extract(self, token: str, keyword: str, until_one_of: list):
        rules = "|".join(until_one_of)
        processed_keyword = self._process_regex_sentitivity(keyword=keyword)
        processed_rules = self._process_regex_sentitivity(keyword=rules)
        return self._search_exact_regex(
            regex=rf"(?<={processed_keyword})(.*?)(?=({processed_rules}|$))",
            token=token,
        )

    def _get_after(self, token: str, keyword: str):
        return (
            self._extract(token=token, keyword=keyword, until_one_of=SYMBOLS)
            .lstrip()
            .rstrip()
        )

    def _split_flow(self, token: str):
        rules = "|".join(NODE_KEYWORDS)
        regex = rf"({rules})(.*?)(?=({rules}|$))"
        flows = [
            x.group()
            for x in re.finditer(
                regex,
                token,
            )
        ]

        return flows

    def _handle_subscriptions(self, token: str, diagram: EpcDiagram) -> EpcNode:
        if ArchitecturalKeywords.SUBSCRIBES in token:
            raw_action = self._get_after(token, ArchitecturalKeywords.SUBSCRIBES)
            subscriptions = list(
                map(lambda x: x.lstrip().rstrip(), raw_action.split(","))
            )

            for subscription in subscriptions:
                diagram.architecture.subscribe(subscription)

    def _handle_activity(self, token: str, diagram: EpcDiagram) -> EpcNode:
        if Keywords.ACTIVITY in token:
            raw_action = self._get_after(token, Keywords.ACTIVITY)
            node = ActivityNode(description=raw_action)

            if ContextKeywords.DATABASE in token:
                db = self._get_after(token, ContextKeywords.DATABASE)
                node.set_database_connection(database=db)

            if ContextKeywords.API_CALL_IN in token:
                call = self._get_after(token, ContextKeywords.API_CALL_IN)
                node.set_incoming_api_call(api_call=call)

            if ContextKeywords.API_CALL_OUT in token:
                call = self._get_after(token, ContextKeywords.API_CALL_OUT)
                node.set_outgoing_api_call(api_call=call)

            diagram.push(node)

    def _handle_event(self, token: str, diagram: EpcDiagram) -> EpcNode:
        if Keywords.EVENT in token:
            raw_action = self._get_after(token, Keywords.EVENT)
            diagram.push(EventNode(description=raw_action))

            if ArchitecturalKeywords.PUBLISHES in token:
                raw_action = self._get_after(token, ArchitecturalKeywords.PUBLISHES)
                diagram.architecture.publish(raw_action)

    def _handle_inner_flow(self, token: str, diagram: EpcDiagram) -> EpcNode:
        if ClusterKeywords.INNER_FLOW in token:
            raw_name = self._get_after(token, ClusterKeywords.INNER_FLOW)
            diagram.inner_flow_names.append(str(raw_name))
            diagram.push(ProcessNode(description=raw_name))

    def _handle_flow(self, token: str, diagram: EpcDiagram):
        self._handle_inner_flow(token=token, diagram=diagram)
        self._handle_subscriptions(token=token, diagram=diagram)

        flows = self._split_flow(token=token)
        for flow in flows:
            self._handle_activity(token=flow, diagram=diagram)
            self._handle_event(token=flow, diagram=diagram)

    def _handle_if(self, sequence: TokenSequence, depth=0) -> EpcNode:
        first_element = str(sequence.pop(0))
        if Keywords.IF not in str(first_element):
            return None, None

        if_node = copy.deepcopy(IfNode(uuid4()))
        current_branch = copy.deepcopy(EpcDiagram())

        self._handle_flow(token=first_element, diagram=current_branch)

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

            if Keywords.ELSE in token:
                if_node.branches.append(current_branch.head)
                current_branch = EpcDiagram()

            self._handle_flow(token=token, diagram=current_branch)

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

            self._handle_flow(token=token, diagram=diagram)

        return diagram


class Composer:
    _endix: int = None

    def _get_after(self, string: str, keyword: str):
        return string.split(keyword, 1)[1]

    def _struct(self, parsed: TokenSequence) -> EpcDiagram:
        node_adder = DiagramNodeAdder()
        diagram = node_adder.add_nodes(token_sequence=parsed)

        return diagram

    def compose(self, parsed: TokenSequence):
        diagram = self._struct(parsed=parsed)
        return diagram
