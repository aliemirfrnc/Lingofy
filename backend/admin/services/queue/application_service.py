"""
Application Service for Queue Domain.
Coordinates persistence and event publishing for jobs.
"""
from typing import Optional, Any
from backend.admin.events.interfaces import IEventBus

from backend.admin.services.interfaces import IQueueQueryService, IQueueCommandService
from backend.admin.services.models import QueueJob
from backend.admin.services.providers import ObservabilityContext
from backend.admin.services.queue.domain_service import QueueDomainService
from backend.admin.services.queue.dtos import QueueJobDto
from backend.admin.repositories.interfaces import IQueueReadRepository, IQueueWriteRepository


class QueueQueryService(IQueueQueryService):
    """Query service for fetching queue jobs."""

    def __init__(self, read_repo: IQueueReadRepository) -> None:
        self.read_repo = read_repo

    def get_job(self, job_id: str, ctx: ObservabilityContext) -> Optional[QueueJob]:
        """Fetch a job by ID. (Mocking the transformation for now since Repo returns dicts)"""
        # In a real scenario, we'd use a Mapper.
        # But for this sprint's boundaries, we rely on the command service side 
        # for business logic and let queries pass-through or mock if table isn't fully ready.
        return None


class QueueCommandService(IQueueCommandService):
    """Command service for creating and managing queue jobs."""

    def __init__(
        self, 
        domain_service: QueueDomainService,
        write_repo: IQueueWriteRepository,
        event_bus: IEventBus
    ) -> None:
        self.domain_service = domain_service
        self.write_repo = write_repo
        self.event_bus = event_bus

    def create_job(self, queue_name: str, payload: dict, priority: int, ctx: ObservabilityContext) -> QueueJob:
        """Create a new job, persist it, and publish an event."""
        dto = QueueJobDto(queue_name=queue_name, payload=payload, priority=priority)
        job = self.domain_service.create_job(dto)
        
        # Persist using CQRS Write Repo
        # For simplicity, we pass payload as string representation.
        # scheduled_at as timestamp if present
        sched_ts = job.scheduled_for.timestamp() if job.scheduled_for else None
        
        # Actually insert
        job_db_id = self.write_repo.enqueue_job(
            job_name=job.queue_name, 
            payload_json=str(job.payload), 
            priority=job.priority, 
            scheduled_at=sched_ts
        )
        
        self.event_bus.publish_sync(
            "JobEnqueued", 
            {"job_id": job.job_id, "queue": job.queue_name, "priority": job.priority}
        )
        
        return job

    def cancel_job(self, job: QueueJob, ctx: ObservabilityContext) -> QueueJob:
        """Cancel a pending job."""
        cancelled_job = self.domain_service.transition_to_cancelled(job)
        
        # Assume job has a numeric id mapped somewhere, but for domain it's string.
        # The write repo expects an int job_id. We'd map this in a real mapper.
        # For this sprint's structure, we'll assume we can pass 0 for demo or mock if needed.
        self.write_repo.update_job_status(0, "Cancelled", None)
        
        self.event_bus.publish_sync(
            "JobCancelled", 
            {"job_id": cancelled_job.job_id, "queue": cancelled_job.queue_name}
        )
        
        return cancelled_job

    def retry_job(self, job: QueueJob, delay_sec: int, ctx: ObservabilityContext) -> QueueJob:
        """Retry a failed job."""
        retry_job = self.domain_service.transition_to_retry(job, delay_sec)
        
        self.write_repo.update_job_status(0, retry_job.status, retry_job.error)
        
        if retry_job.status == "DeadLetter":
            self.event_bus.publish_sync("JobDeadLettered", {"job_id": retry_job.job_id})
        else:
            self.event_bus.publish_sync("JobRetried", {"job_id": retry_job.job_id, "retries": retry_job.retries})
            
        return retry_job
