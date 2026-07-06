# Netcool Event Examples for EDA Testing

This directory contains example Netcool event messages and playbooks for testing Event-Driven Ansible with IBM Netcool/OMNIbus integration.

## Files Overview

### Event Message Examples

- **netcool_event_msg.json** - Single basic web service outage event
- **netcool_events_examples.json** - Comprehensive collection of 15 different outage scenarios

### Playbooks

- **query_netcool_for_status.yml** - Query Netcool ObjectServer to verify alert status after remediation

### Rulebooks

- **../rulebooks/netcool_kafka.yml** - Basic Kafka-based Netcool event consumer
- **../rulebooks/netcool_webhook.yml** - Basic webhook-based Netcool event receiver
- **../rulebooks/netcool_multi_scenario.yml** - Multi-scenario event handler with 14 different automation responses

## Event Scenarios Covered

### 1. Web Services
- **Severity**: Critical (5)
- **Scenario**: HTTP service down
- **Auto-Remediation**: Restart web server service

### 2. Database Issues
- **Severity**: Major (4)
- **Scenario**: Connection pool exhausted
- **Auto-Remediation**: Restart database connection pool

### 3. Storage Issues
- **Severity**: Critical (5)
- **Scenario**: Disk space at 95% full
- **Auto-Remediation**: Clean up logs and temporary files

### 4. System Resources
- **Severity**: Major (4)
- **Scenario**: Memory utilization >90%
- **Auto-Remediation**: Restart memory-intensive services or optimize

### 5. Security - Certificate Management
- **Severity**: Minor (3)
- **Scenario**: SSL certificate expiring in 7 days
- **Auto-Remediation**: Auto-renew certificate via Let's Encrypt/ACME

### 6. Network Infrastructure
- **Severity**: Critical (5)
- **Scenario**: Network interface down
- **Auto-Remediation**: Bounce network interface

### 7. Application Performance
- **Severity**: Major (4)
- **Scenario**: API response time >5s threshold
- **Auto-Remediation**: Scale application horizontally

### 8. Backup & Recovery
- **Severity**: Major (4)
- **Scenario**: Nightly backup job failed
- **Auto-Remediation**: Retry backup with error handling

### 9. Kubernetes/Container Platform
- **Severity**: Critical (5)
- **Scenario**: Pod in CrashLoopBackOff state
- **Auto-Remediation**: Delete and recreate pod, check dependencies

### 10. Messaging Systems
- **Severity**: Major (4)
- **Scenario**: Message queue depth exceeded
- **Auto-Remediation**: Scale consumers, alert on backlog

### 11. DNS Services
- **Severity**: Critical (5)
- **Scenario**: DNS server not responding
- **Auto-Remediation**: Restart DNS service (BIND9)

### 12. Load Balancing
- **Severity**: Major (4)
- **Scenario**: Multiple backend servers unhealthy
- **Auto-Remediation**: Remove unhealthy backends, investigate health

### 13. Hardware Monitoring
- **Severity**: Critical (5)
- **Scenario**: CPU temperature exceeds threshold
- **Auto-Remediation**: Emergency notification, potential shutdown

### 14. Licensing
- **Severity**: Minor (3)
- **Scenario**: Software license expiring in 14 days
- **Auto-Remediation**: Generate renewal ticket, notify procurement

### 15. Security - Firewall Events
- **Severity**: Major (4)
- **Type**: Security violation (13)
- **Scenario**: Multiple blocked connection attempts from suspicious IP
- **Auto-Remediation**: Add IP to permanent block list

## Netcool Event Field Reference

### Core Fields

| Field | Description | Example |
|-------|-------------|---------|
| `AlertGroup` | Category/domain of the alert | "Web Services", "Database", "Network" |
| `Severity` | Numeric severity (0=Clear, 1=Indeterminate, 2=Warning, 3=Minor, 4=Major, 5=Critical) | 5 |
| `Type` | Event type (1=Problem, 2=Resolution, 13=Security) | 1 |
| `Node` | Hostname/device generating the alert | "webserver01.company.internal" |
| `Summary` | Human-readable description | "HTTP service down on webserver01" |
| `FirstOccurrence` | Timestamp of first occurrence | "2026-06-16T10:15:30Z" |
| `LastOccurrence` | Timestamp of most recent occurrence | "2026-06-16T10:15:30Z" |
| `AlertKey` | Unique identifier for alert type | "HTTP_Service_Down" |
| `Identifier` | Unique identifier for specific alert instance | "webserver01:httpd" |
| `Class` | Event classification code | 15000 |
| `Manager` | Probe/manager name | "NetcoolProbe" |
| `ServerName` | ObjectServer name | "netcool-objectserver-01" |

### Extended Attributes

The `ExtendedAttr` object contains scenario-specific metadata.

## Testing with curl

### Test Webhook Listener

```bash
# Send basic web service down event
curl -X POST http://localhost:5000/endpoint \
  -H "Content-Type: application/json" \
  -d @netcool_event_msg.json

# Send specific scenario from examples file
curl -X POST http://localhost:5000/endpoint \
  -H "Content-Type: application/json" \
  -d "$(jq '.[] | select(.scenario == "Database Connection Pool Exhausted") | .event' netcool_events_examples.json)"
```

### Test All Scenarios

```bash
# Loop through all example scenarios
jq -c '.[] | .event' netcool_events_examples.json | while read event; do
  echo "Sending event: $(echo $event | jq -r '.Summary')"
  curl -X POST http://localhost:5000/endpoint \
    -H "Content-Type: application/json" \
    -d "$event"
  sleep 2
done
```

## Severity Levels Reference

| Level | Name | Value | Usage |
|-------|------|-------|-------|
| 0 | Clear | 0 | Alert has been cleared/resolved |
| 1 | Indeterminate | 1 | Unknown or uncertain condition |
| 2 | Warning | 2 | Potential issue, not yet impacting service |
| 3 | Minor | 3 | Low-impact issue, manual review needed |
| 4 | Major | 4 | Service degradation, auto-remediation triggered |
| 5 | Critical | 5 | Service down, immediate auto-remediation required |

## Event Type Reference

| Type | Description |
|------|-------------|
| 1 | Problem/Issue detected |
| 2 | Resolution/Clear event |
| 13 | Security violation or event |

## EDA Condition Examples

### Simple Severity Check
```yaml
condition: event.Severity == 5
```

### Multiple Field Match
```yaml
condition: >
  event.AlertGroup == "Database" and
  event.Severity >= 4 and
  event.Type == 1
```

### Using Extended Attributes
```yaml
condition: >
  event.AlertKey == "Disk_Space_Critical" and
  event.ExtendedAttr.usage_percent | int > 90
```

## Best Practices

1. **Always verify alert closure**: Use `query_netcool_for_status.yml` after remediation
2. **Set appropriate severity thresholds**: Not all issues require immediate automation
3. **Use ExtendedAttr for context**: Pass detailed metrics to remediation playbooks
4. **Implement idempotency**: Ensure remediation actions can be safely repeated
5. **Log all actions**: Include logging in remediation playbooks for audit trail
6. **Test in non-production first**: Validate conditions and actions before production deployment
7. **Monitor EDA activations**: Track success/failure rates of automated remediations

## References

- [IBM Netcool/OMNIbus Documentation](https://www.ibm.com/docs/en/netcoolomnibus)
- [Ansible EDA Documentation](https://ansible.readthedocs.io/projects/eda/)
- [AAP EDA Controller Guide](https://access.redhat.com/documentation/en-us/red_hat_ansible_automation_platform/)
