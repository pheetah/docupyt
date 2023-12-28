from unittest import TestCase

from compose import DiagramNodeAdder
from doctree import ActivityNode, EpcDiagram
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

    def test_can_separate_multiple_sources(self):
        # Before
        diagram = EpcDiagram()
        TOKEN = (
            f"# {Keywords.ACTIVITY} find related tax rates "
            "[=] banking.rates "
            "-> id "
            "<- tax_rate_list, permissions"
        )

        # Test
        self.node_adder._handle_activity(token=TOKEN, diagram=diagram)

        # After
        activity: ActivityNode = diagram.head

        assert activity._description == "find related tax rates"
        assert activity._database == "banking.rates"
        assert set(activity._outgoing_api_calls) == set(["id"])
        assert set(activity._incoming_api_calls) == set(
            ["tax_rate_list", "permissions"]
        )

        assert activity.next is None

    def test_can_cascade_multiple_nodes(self):
        # Before
        diagram = EpcDiagram()
        TOKEN = (
            f"# {Keywords.ACTIVITY} find related tax rates "
            "[=] banking.rates "
            f"{Keywords.ACTIVITY} fetch tax rates and permissions "
            "-> id <- tax_rate_list, permissions "
            f"{Keywords.EVENT} payment completed"
        )

        # Test
        self.node_adder._handle_flow(token=TOKEN, diagram=diagram)

        # After
        # Assert first node
        first_node: ActivityNode = diagram.head
        assert first_node._description == "find related tax rates"
        assert first_node._database == "banking.rates"

        # Assert next node
        second_node = first_node.next
        assert set(second_node._outgoing_api_calls) == set(["id"])
        assert set(second_node._incoming_api_calls) == set(
            ["tax_rate_list", "permissions"]
        )

        # Assert next node
        third_node = second_node.next
        assert third_node._description == "payment completed"
        assert third_node.next is None
