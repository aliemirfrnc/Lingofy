"""
Domain Service for Health.
Pure business logic, no I/O.
"""
from backend.admin.services.models import HealthSnapshot, HealthDependency
from backend.admin.services.providers import ISystemClock
from backend.admin.services.health.dtos import HealthRawData, DependencyStatusDto


class HealthDomainService:
    """Evaluates health conditions and generates a snapshot."""

    def __init__(self, clock: ISystemClock) -> None:
        self.clock = clock

    def evaluate_health(self, raw: HealthRawData) -> HealthSnapshot:
        """Evaluate raw dependency data to compute a global health snapshot."""
        dependencies = []
        total_score = 0
        total_weight = 0

        for dep in raw.dependencies:
            status = self._determine_dependency_status(dep)
            dependencies.append(
                HealthDependency(
                    name=dep.name,
                    status=status,
                    latency_ms=dep.latency_ms if dep.is_reachable else None,
                    error=dep.error_message
                )
            )
            
            weight = self._get_dependency_weight(dep.name)
            dep_score = self._calculate_dependency_score(status)
            total_score += dep_score * weight
            total_weight += weight

        final_score = int(total_score / total_weight) if total_weight > 0 else 100
        level = self._determine_overall_level(final_score, dependencies)

        return HealthSnapshot(
            score=final_score,
            level=level,
            dependencies=dependencies,
            evaluated_at=self.clock.now()
        )

    def _determine_dependency_status(self, dep: DependencyStatusDto) -> str:
        if not dep.is_reachable:
            return "Critical"
        if dep.latency_ms > 2000:
            return "Unhealthy"
        if dep.latency_ms > 800:
            return "Degraded"
        return "Healthy"

    def _calculate_dependency_score(self, status: str) -> int:
        mapping = {
            "Healthy": 100,
            "Degraded": 70,
            "Unhealthy": 30,
            "Critical": 0
        }
        return mapping.get(status, 0)

    def _get_dependency_weight(self, name: str) -> int:
        """Core DB is more important than external APIs."""
        if name.lower() == "database":
            return 3
        if "cache" in name.lower() or "redis" in name.lower():
            return 2
        return 1

    def _determine_overall_level(self, score: int, deps: list[HealthDependency]) -> str:
        # If any critical dependency (weight 3) is Critical, overall is Critical
        for d in deps:
            if d.status == "Critical" and self._get_dependency_weight(d.name) >= 3:
                return "Critical"
                
        if score >= 90:
            return "Healthy"
        elif score >= 70:
            return "Degraded"
        elif score >= 40:
            return "Unhealthy"
        return "Critical"
