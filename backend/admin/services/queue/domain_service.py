"""
Domain Service for Queue.
Pure business logic, no I/O.
"""
from datetime import timedelta
from typing import Optional

from backend.admin.services.models import QueueJob
from backend.admin.services.providers import ISystemClock, IIdGenerator
from backend.admin.services.exceptions import QueueException
from backend.admin.services.queue.dtos import QueueJobDto


class QueueDomainService:
    """Manages queue job transitions and rules."""

    def __init__(self, clock: ISystemClock, id_gen: IIdGenerator) -> None:
        self.clock = clock
        self.id_gen = id_gen

    def create_job(self, dto: QueueJobDto) -> QueueJob:
        """Create a new job from DTO."""
        if not dto.queue_name:
            raise QueueException("Queue name is required.")
        
        if dto.priority < 0 or dto.priority > 10:
            raise QueueException("Priority must be between 0 and 10.")
            
        scheduled_for = dto.scheduled_for
        if dto.delay_sec is not None and dto.delay_sec > 0:
            scheduled_for = self.clock.now() + timedelta(seconds=dto.delay_sec)
            
        return QueueJob(
            job_id=self.id_gen.generate(),
            queue_name=dto.queue_name,
            status="Pending",
            priority=dto.priority,
            payload=dto.payload or {},
            created_at=self.clock.now(),
            scheduled_for=scheduled_for,
            completed_at=None,
            error=None,
            retries=0
        )

    def transition_to_failed(self, job: QueueJob, error_text: str) -> QueueJob:
        """Mark job as failed or retry if under max retries."""
        if job.status not in ("Pending", "Processing"):
            raise QueueException(f"Cannot fail job from status {job.status}")
            
        return QueueJob(
            job_id=job.job_id,
            queue_name=job.queue_name,
            status="Failed",
            priority=job.priority,
            payload=job.payload,
            created_at=job.created_at,
            scheduled_for=job.scheduled_for,
            completed_at=self.clock.now(),
            error=error_text,
            retries=job.retries
        )

    def transition_to_retry(self, job: QueueJob, delay_sec: int) -> QueueJob:
        """Increment retry count and reschedule."""
        if job.retries >= 5:
            return self.transition_to_dead_letter(job)
            
        return QueueJob(
            job_id=job.job_id,
            queue_name=job.queue_name,
            status="Pending",
            priority=job.priority,
            payload=job.payload,
            created_at=job.created_at,
            scheduled_for=self.clock.now() + timedelta(seconds=delay_sec),
            completed_at=None,
            error=None,
            retries=job.retries + 1
        )
        
    def transition_to_dead_letter(self, job: QueueJob) -> QueueJob:
        """Move job to dead letter queue."""
        return QueueJob(
            job_id=job.job_id,
            queue_name="dead_letter",
            status="DeadLetter",
            priority=0,
            payload={"original_queue": job.queue_name, "data": job.payload},
            created_at=job.created_at,
            scheduled_for=None,
            completed_at=self.clock.now(),
            error=job.error or "Max retries exceeded",
            retries=job.retries
        )

    def transition_to_cancelled(self, job: QueueJob) -> QueueJob:
        """Cancel a pending job."""
        if job.status != "Pending":
            raise QueueException("Only pending jobs can be cancelled.")
            
        return QueueJob(
            job_id=job.job_id,
            queue_name=job.queue_name,
            status="Cancelled",
            priority=job.priority,
            payload=job.payload,
            created_at=job.created_at,
            scheduled_for=job.scheduled_for,
            completed_at=self.clock.now(),
            error=None,
            retries=job.retries
        )
