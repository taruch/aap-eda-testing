# AAP Event-Driven Ansible (EDA) Testing Examples

Comprehensive examples for testing EDA with Netcool and ServiceNow integrations.

## Quick Links

- [Netcool/OMNIbus Examples](NETCOOL_EXAMPLES_README.md) - IBM Netcool monitoring integration
- [ServiceNow Examples](SERVICENOW_EXAMPLES_README.md) - ServiceNow ITSM incident management

## Overview

Event-Driven Ansible enables automation to respond to events from monitoring systems, ITSM platforms, webhooks, and message queues. These examples demonstrate real-world scenarios and auto-remediation patterns.

## Directory Structure

```
demo/
├── README.md                                    # This file
│
├── NETCOOL_EXAMPLES_README.md                  # Netcool guide
├── netcool_event_msg.json                      # Single Netcool event
├── netcool_events_examples.json                # 15 Netcool scenarios
├── query_netcool_for_status.yml                # Verify alert closure
│
├── SERVICENOW_EXAMPLES_README.md               # ServiceNow guide
├── servicenow_incident_examples.json           # 15 ServiceNow scenarios
├── servicenow_query_incident.yml               # Query incident status
├── test_servicenow_create_incidents.yml        # Create test incidents
└── ServiceNow_Update_Incident.yml              # Update incidents
```

## Event Sources

### 1. Netcool/OMNIbus (15 scenarios)
- Application failures, database issues, storage problems
- Network outages, security events, performance degradation
- Kubernetes issues, message queues, hardware failures

**Sources:** Kafka (`ansible.eda.kafka`), Webhook (`ansible.eda.webhook`)

### 2. ServiceNow ITSM (15 scenarios)
- Critical outages, database performance, network loss
- Security incidents, backup failures, API rate limiting
- Certificate expiration, K8s pods, message queues
- Monitoring failures, DNS issues, load balancers, vulnerabilities

**Source:** ServiceNow polling (`servicenow.itsm.records`)

## Common Automation Patterns

### Pattern 1: Detect → Remediate → Verify
```yaml
- name: Detect Issue
  condition: event.severity == "critical"
  action:
    run_workflow_template:
      name: Remediation Workflow
```

### Pattern 2: Severity-Based Routing
```yaml
- name: Critical - Immediate
  condition: event.priority == "1"
  action: run_workflow_template

- name: High - Automated
  condition: event.priority == "2"
  action: run_job_template

- name: Medium - Ticket
  condition: event.priority == "3"
  action: create_ticket
```

### Pattern 3: Multi-Stage with Escalation
```yaml
- name: Try Quick Fix
  condition: event.remediation_attempts == 0
  action: run_job_template: Quick Fix

- name: Escalate on Failure
  condition: event.remediation_attempts >= 1
  action: run_workflow_template: Full Recovery
```

## Quick Start

### Test Netcool Webhook

```bash
# Start EDA
ansible-rulebook -i localhost --rulebook ../rulebooks/netcool_webhook.yml

# Send test event (in another terminal)
curl -X POST http://localhost:5000/endpoint \
  -H "Content-Type: application/json" \
  -d @netcool_event_msg.json
```

### Test ServiceNow Polling

```bash
# Set credentials
export SN_HOST="dev12345.service-now.com"
export SN_USERNAME="admin"
export SN_PASSWORD="your_password"

# Create test incidents
ansible-playbook test_servicenow_create_incidents.yml -e scenario_filter="Critical"

# Start EDA polling
ansible-rulebook -i localhost --rulebook ../rulebooks/servicenow_incidents_multi_scenario.yml
```

## Field Mapping Reference

### Netcool → EDA Event
```python
event.AlertGroup      # "Web Services", "Database"
event.Severity        # 1-5 (Critical=5)
event.Type            # 1=Problem, 2=Resolution, 13=Security
event.Node            # Hostname
event.Summary         # Description
event.ExtendedAttr.*  # Custom attributes
```

### ServiceNow → EDA Event
```python
event.number          # INC0010001
event.state           # 1=New, 2=In Progress, 6=Resolved
event.priority        # 1=Critical, 2=High, 3=Moderate
event.category        # "Software", "Database", "Network"
event.u_*             # Custom fields
```

## Integration with AAP EDA Controller

### Prerequisites
1. AAP EDA Controller installed
2. Event source credentials configured
3. Job templates created in AAP Controller
4. Decision environments with required collections

### Deployment Steps
1. Create Project (Git repo with rulebooks)
2. Create Decision Environment (`ansible.eda`, `servicenow.itsm`)
3. Create Rulebook Activation
4. Monitor via EDA Controller UI

## Best Practices

### Safety
✅ Use opt-in flags (`u_automated_remediation`)  
✅ Test in non-production first  
✅ Implement validation after remediation  
✅ Include rollback procedures  
❌ Don't auto-delete resources  
❌ Don't skip approval for destructive actions  

### Observability
✅ Log all actions to source system  
✅ Track success/failure metrics  
✅ Preserve audit trail  
✅ Alert on repeated failures  

### Reliability
✅ Make actions idempotent  
✅ Handle partial failures gracefully  
✅ Set realistic timeouts  
✅ Implement retry with backoff  
✅ Escalate after N failures  

## Customization Guide

1. Add event example to JSON file
2. Create matching rule in rulebook
3. Create remediation job template in AAP
4. Test end-to-end
5. Monitor and iterate

## Troubleshooting

### Rulebook not firing
- Check activation is running
- Verify event source connectivity
- Inspect event structure with `print_event`
- Check field types (string vs int)

### Remediation job fails
- Verify job template exists
- Check credentials attached
- Confirm inventory has hosts
- Review extra vars passing
- Check job output in Controller

### Events not reaching EDA
- **Netcool**: Firewall allows port, Kafka credentials valid
- **ServiceNow**: API credentials correct, query returns results

## Support

- [Ansible EDA Docs](https://ansible.readthedocs.io/projects/eda/)
- [AAP Documentation](https://access.redhat.com/documentation/en-us/red_hat_ansible_automation_platform/)
- [Community Forum](https://forum.ansible.com/c/eda/)

## Contributing

Add new examples by:
1. Adding event/incident to JSON file
2. Creating rule in multi-scenario rulebook
3. Documenting in README
4. Testing end-to-end
