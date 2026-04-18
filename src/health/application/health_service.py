from src.health.domain.health_status import HealthStatus


class HealthService:
    def check(self) -> HealthStatus:
        return HealthStatus.healthy()
