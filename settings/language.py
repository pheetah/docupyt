from enum import Enum


class StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class Keywords(StringEnum):
    ACTIVITY = "act:"
    EVENT = "event:"
    IF = "if:"
    ELSE = "else:"
    ENDIF = "end:"


class ContextKeywords(StringEnum):
    DATABASE = "[=]"
    API_CALL_OUT = "->"
    API_CALL_IN = "<-"


class ClusterKeywords(StringEnum):
    CLUSTER = "inner-diagram:"
    END_CLUSTER = "end-diagram:"
    INNER_FLOW = "inner-flow:"
    MAIN_CLUSTER = "main-diagram:"
    END_MAIN_CLUSTER = "end-diagram-main:"


class ArchitecturalKeywords(StringEnum):
    SUBSCRIBES = "subscribes:"
    PUBLISHES = "publishes:"


NODE_KEYWORDS = [
    Keywords.ACTIVITY,
    Keywords.EVENT,
    Keywords.IF,
    Keywords.ELSE,
    Keywords.ENDIF,
]

SYMBOLS = [
    Keywords.ACTIVITY,
    Keywords.EVENT,
    Keywords.IF,
    Keywords.ELSE,
    Keywords.ENDIF,
    ContextKeywords.DATABASE,
    ContextKeywords.API_CALL_OUT,
    ContextKeywords.API_CALL_IN,
    ArchitecturalKeywords.PUBLISHES,
]
