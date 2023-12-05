from abc import ABC, abstractmethod

import code_tokenize as ctok


class IParser(ABC):
    @abstractmethod
    def parse(self):
        raise NotImplementedError("Parser functionality not implemented!")


class Parser(IParser):
    def parse(self, file_path: str):
        with open(file_path) as file:
            file_str = file.read()
            return ctok.tokenize(
                file_str,
                lang="python",
            )
