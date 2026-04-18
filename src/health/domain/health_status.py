from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HealthStatus:
    status: str
    timestamp: datetime

    @staticmethod
    def healthy() -> "HealthStatus":
        return HealthStatus(status="ok", timestamp=datetime.utcnow())
