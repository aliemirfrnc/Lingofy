"""
Application Service for Health Domain.
Coordinates dependency pings and delegates to Domain Service.
"""
from backend.admin.events.interfaces import IEventBus
import time
from typing import List, Callable, Tuple, Any

from backend.admin.services.interfaces import IHealthQueryService
from backend.admin.services.models import HealthSnapshot
from backend.admin.services.providers import ObservabilityContext
from backend.admin.services.health.domain_service import HealthDomainService
from backend.admin.services.health.dtos import HealthRawData, DependencyStatusDto
from backend.admin.repositories.interfaces import IHealthRepository


class HealthQueryService(IHealthQueryService):
    """Query service for checking health status."""

    def __init__(
        self, 
        domain_service: HealthDomainService,
        health_repo: IHealthRepository,
        event_bus: IEventBus,
        db_ping_func: Callable[[], bool] = lambda: True,
        ai_ping_func: Callable[[], bool] = lambda: True,
        payment_ping_func: Callable[[], bool] = lambda: True
    ) -> None:
        self.domain_service = domain_service
        self.health_repo = health_repo
        self.event_bus = event_bus
        self.db_ping_func = db_ping_func
        self.ai_ping_func = ai_ping_func
        self.payment_ping_func = payment_ping_func

    def check_health(self, ctx: ObservabilityContext) -> HealthSnapshot:
        """Check all dependencies and return a HealthSnapshot."""
        deps = []
        
        # Ping Database
        deps.append(self._measure_dependency("Database", self.db_ping_func))
        
        # Ping AI Providers
        deps.append(self._measure_dependency("AI Providers", self.ai_ping_func))
        
        # Ping Payment Gateway
        deps.append(self._measure_dependency("Payment Gateway", self.payment_ping_func))

        raw = HealthRawData(dependencies=deps)
        snapshot = self.domain_service.evaluate_health(raw)
        
        # Note: Event publish is generally done by Command Services,
        # but health checks act somewhat like an observation that we may want to record.
        self.health_repo.insert_health_snapshot(
            service_name="Operations_Backend",
            status=snapshot.level,
            details_json=str({"score": snapshot.score})
        )
        
        self.event_bus.publish_sync(
            "HealthChecked", 
            {"score": snapshot.score, "level": snapshot.level, "evaluated_at": snapshot.evaluated_at.isoformat()}
        )

        return snapshot

    def _measure_dependency(self, name: str, ping_func: Callable[[], bool]) -> DependencyStatusDto:
        start_time = time.perf_counter()
        is_reachable = False
        error_msg = None
        
        try:
            is_reachable = ping_func()
        except Exception as e:
            error_msg = str(e)
            
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        
        return DependencyStatusDto(
            name=name,
            is_reachable=is_reachable,
            latency_ms=latency_ms,
            error_message=error_msg
        )
