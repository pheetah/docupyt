import re
from copy import deepcopy
from parser.doctree_parser import Parser

from settings.language import ClusterKeywords


class Flow:
    tokens: list
    name: str

    def __init__(self) -> None:
        self.tokens = []


class Flows:
    processed_indexes = {}
    latest_flow: Flow = None


class Cluster:
    _inner_flows: list[Flow] = []
    _main_flows: list[str] = []

    def __init__(self) -> None:
        pass

    def _find_inner_diagrams(self, token: str, index: int, flows: Flows):
        if ClusterKeywords.CLUSTER in token:
            flow = deepcopy(Flow())
            flow.name = (
                re.search(rf"(?<={ClusterKeywords.CLUSTER})(.*?)$", token)[0]
                .lstrip()
                .rstrip()
            )
            flows.latest_flow = deepcopy(flow)
            flows.processed_indexes.update({"start_index": index})

        elif ClusterKeywords.END_CLUSTER in token:
            self._inner_flows.append(deepcopy(flows.latest_flow))
            flows.processed_indexes.update({"end_index": index})
            flows.latest_flow = None
            return True

        if flows.latest_flow is not None:
            flows.latest_flow.tokens.append(token)

    def extract_flows(self, file_name_list: list[str]):
        for file in file_name_list:
            parser = Parser()
            parsed = parser.parse(file)
            flows = Flows()

            for index, token_raw in enumerate(parsed):
                indexes_processed = self._find_inner_diagrams(
                    str(token_raw), index, flows
                )

                if indexes_processed:
                    start_index = flows.processed_indexes["start_index"]
                    end_index = flows.processed_indexes["end_index"] + 1

                    del parsed[start_index:end_index]

            self._main_flows.append(parsed)
