"""
datadog_poll.py
An Ansible EDA source plugin that polls Datadog for active monitor alerts.
"""

import asyncio
import logging
from typing import Any, Dict
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi

async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    logger = logging.getLogger("datadog_poll")
    
    # Argument parsing
    api_key = args.get("api_key")
    app_key = args.get("app_key")
    delay = int(args.get("delay", 60))  # Poll every 60s by default
    tags = args.get("tags", "")         # Filter by tags (e.g., "env:prod")

    if not api_key or not app_key:
        logger.error("Datadog API and App keys are required.")
        return

    # Datadog Client Configuration
    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = api_key
    configuration.api_key["appKeyAuth"] = app_key

    # Track seen alerts to avoid duplicates
    seen_alerts = set()

    while True:
        try:
            async with ApiClient(configuration) as api_client:
                api_instance = MonitorsApi(api_client)
                
                # Fetch active alerts (group_states='Alert')
                response = api_instance.search_monitor_groups(
                    query=f"status:alert {tags}"
                )

                if response.groups:
                    for group in response.groups:
                        # Create a unique ID for the alert instance
                        alert_id = f"{group.monitor_id}-{group.result_groups}"
                        
                        if alert_id not in seen_alerts:
                            # New Alert Found!
                            event = {
                                "monitor_name": group.monitor_name,
                                "monitor_id": group.monitor_id,
                                "status": group.status,
                                "tags": group.tags,
                                "last_triggered": str(group.last_triggered_ts),
                                "meta": {"hosts": "localhost"}
                            }
                            
                            await queue.put(event)
                            seen_alerts.add(alert_id)
                            logger.info(f"Triggered event for {group.monitor_name}")

        except Exception as e:
            logger.error(f"Error polling Datadog: {e}")

        # Wait for next poll cycle
        await asyncio.sleep(delay)