from enum import Enum

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
