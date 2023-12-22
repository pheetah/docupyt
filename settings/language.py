from enum import Enum


class StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class Keywords(StringEnum):
    ACTIVITY = "ACTIVITY"
    EVENT = "EVENT"
    IF = "IF"
    ELSE = "ELSE"
    ENDIF = "END"


class ContextKeywords(StringEnum):
    DATABASE = "[=]"


SYMBOLS = [
    Keywords.ACTIVITY,
    Keywords.EVENT,
    Keywords.IF,
    Keywords.ELSE,
    Keywords.ENDIF,
    ContextKeywords.DATABASE,
]
