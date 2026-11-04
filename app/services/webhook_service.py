"""Webhook dispatching service with cryptographic signing and delivery logging."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.core.security import compute_hmac_signature
from app.models.store import data_store
from app.schemas.webhook import WebhookDeliveryResponse


class WebhookDispatcher:
    """Dispatches webhook payloads with HMAC-SHA256 signature headers."""

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    async def deliver(self, target_url: str, secret: str, event_type: str, payload: Dict[str, Any]) -> WebhookDeliveryResponse:
        """Sign and deliver a single webhook payload via HTTP POST."""
        body_dict = {
            "id": f"evt_{uuid.uuid4().hex[:12]}",
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }
        body_bytes = json.dumps(body_dict, sort_keys=True).encode("utf-8")
        signature = compute_hmac_signature(secret, body_bytes)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Nexus-Webhook-Dispatcher/1.0",
            "X-Nexus-Signature": signature,
            "X-Nexus-Event": event_type,
        }

        delivery_id = f"del_{uuid.uuid4().hex[:12]}"
        success = False
        status_code = None
        response_text = None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(target_url, content=body_bytes, headers=headers)
                status_code = res.status_code
                response_text = res.text[:200]
                success = (200 <= status_code < 300)
        except Exception as exc:
            response_text = f"Connection error: {str(exc)}"

        return WebhookDeliveryResponse(
            delivery_id=delivery_id,
            endpoint_id="direct",
            target_url=target_url,
            event_type=event_type,
            status_code=status_code,
            signature=signature,
            success=success,
            response_body=response_text,
            delivered_at=datetime.now(timezone.utc),
        )

    async def broadcast_event(self, event_type: str, payload: Dict[str, Any]) -> List[WebhookDeliveryResponse]:
        """Broadcast an event to all subscribed endpoints."""
        endpoints = await data_store.get_webhooks_for_event(event_type)
        deliveries = []
        for ep in endpoints:
            delivery = await self.deliver(
                target_url=ep["target_url"],
                secret=ep["secret"],
                event_type=event_type,
                payload=payload,
            )
            deliveries.append(delivery)
        return deliveries


webhook_dispatcher = WebhookDispatcher()
