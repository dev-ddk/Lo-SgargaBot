from enum import Enum, auto

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_str(cls, value: str) -> "LogLevel":
        try:
            return LogLevel(value.upper())
        except ValueError:
            raise Exception(f'Could not set logging level to {value}. Allowed values: {", ".join(e.value for e in LogLevel)}')

class EconomyTXNType(Enum):
    CHECK_BALANCE = "Check Balance"
    PAYMENT = "Payment"
    INCREASE_BALANCE = "Increase Balance"
    DECREASE_BALANCE = "Decrease Balance"
