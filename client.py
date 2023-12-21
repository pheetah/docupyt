from parser.doctree_parser import Parser

from compose import Composer


# Façade
class DocupytClient:
    def __init__(
        self, parser: Parser = Parser(), composer: Composer = Composer()
    ) -> None:
        self._parser = parser
        self._composer = composer

    def create_epc(self, input_file_path: str, output_path: str):
        parsed = self._parser.parse(input_file_path)
        self._composer.compose(export_to=output_path, parsed=parsed)
