from unittest import TestCase

from compose import DiagramNodeAdder
from doctree import EpcDiagram
from settings.language import ContextKeywords, Keywords


class TestNodeAdder(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.node_adder = DiagramNodeAdder()

    def test_node_can_parse_description(self):
        # Before
        ACTION = "retrieve data from geo service"

        # Test
        parsed = self.node_adder._get_after(
            f"# {Keywords.ACTIVITY} {ACTION}", Keywords.ACTIVITY
        )

        # After
        assert parsed == ACTION

    def test_can_handle_activity(self):
        # Before
        diagram = EpcDiagram()
        TOKEN = f"# {Keywords.ACTIVITY} retrieve data from geo service"

        # Test
        self.node_adder._handle_activity(token=TOKEN, diagram=diagram)

        # After
        assert diagram.head._description == "retrieve data from geo service"
        assert diagram.head.next is None
        assert diagram.head._database is None

    def test_activity_can_have_database_connection(self):
        # Before
        diagram = EpcDiagram()
        TOKEN = (
            f"# {Keywords.ACTIVITY} retrieve data from geo service"
            f" {ContextKeywords.DATABASE} GEODB.LOCATIONS"
        )

        # Test
        self.node_adder._handle_activity(token=TOKEN, diagram=diagram)

        # After
        assert diagram.head._description == "retrieve data from geo service"
        assert diagram.head._database == "GEODB.LOCATIONS"
        assert diagram.head.next is None

    def test_can_handle_event(self):
        # Before
        diagram = EpcDiagram()
        TOKEN = f"# {Keywords.EVENT} message to notification service user service out of range"

        # Test
        self.node_adder._handle_event(token=TOKEN, diagram=diagram)

        # After
        assert diagram.head._description == (
            "message to notification service" " user service out of range"
        )
        assert diagram.head.next is None
