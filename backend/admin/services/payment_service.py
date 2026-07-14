import json
from typing import Dict, Any, Optional
from backend.core.db import get_conn
from backend.admin.repositories.payment_read_repo import PaymentReadRepository
from backend.admin.repositories.payment_write_repo import PaymentWriteRepository
from backend.admin.security.audit import log_admin_action
from backend.admin.events.memory_event_bus import memory_event_bus

class PaymentService:
    def __init__(self):
        self.read_repo = PaymentReadRepository()
        self.write_repo = PaymentWriteRepository()

    def get_payments(self, cursor_id: Optional[int], limit: int = 50):
        return self.read_repo.get_payments_paginated(cursor_id, limit)

    async def process_refund(self, admin_id: int, payment_id: int, reason: str, ip_address: Optional[str] = None):
        conn = get_conn()
        
        # 1. Update DB Status
        success = self.write_repo.update_payment_status(payment_id, "REFUNDED")
        if not success:
            raise ValueError("Payment not found or cannot be refunded")
            
        # 2. Add Payment Event
        self.write_repo.add_payment_event(payment_id, "REFUND_INITIATED", None, json.dumps({"reason": reason}))
        
        conn.commit()
        
        # 3. Audit Log
        log_admin_action(
            admin_id=admin_id,
            action="REFUND_PAYMENT",
            resource="payments",
            target_id=str(payment_id),
            diff_after=json.dumps({"status": "REFUNDED", "reason": reason}),
            ip_address=ip_address
        )
        
        # 4. Event Bus
        await memory_event_bus.publish("PAYMENT_REFUNDED", {
            "payment_id": payment_id,
            "reason": reason
        })
        return True
