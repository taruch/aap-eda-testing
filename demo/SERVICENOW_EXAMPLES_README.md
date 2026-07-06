# ServiceNow Incident Examples for EDA Testing

Complete guide for ServiceNow ITSM integration with Event-Driven Ansible.

## Quick Start

```bash
# Set credentials
export SN_HOST="dev12345.service-now.com"
export SN_USERNAME="admin"
export SN_PASSWORD="your_password"

# Create test incidents
ansible-playbook test_servicenow_create_incidents.yml -e scenario_filter="Critical"

# Query incident status
ansible-playbook servicenow_query_incident.yml -e incident_number="INC0010001"
```

## Files

- **servicenow_incident_examples.json** - 15 incident scenarios
- **servicenow_query_incident.yml** - Query incident status
- **test_servicenow_create_incidents.yml** - Create test incidents
- **ServiceNow_Update_Incident.yml** - Update incidents
- **../rulebooks/servicenow_incidents_multi_scenario.yml** - Multi-scenario automation

## Incident Scenarios (15 Total)

1. **Critical Application Outage** (P1) - E-commerce app down, 5000+ users affected
2. **Database Performance Degradation** (P2) - PostgreSQL slow queries, 95% CPU
3. **Network Connectivity Loss** (P1) - Datacenter network outage
4. **Storage Capacity Critical** (P2) - NAS at 95%, log cleanup needed
5. **Security - Brute Force Attack** (P2) - 300+ failed SSH attempts
6. **Backup Job Failure** (P3) - Oracle backup failed, RPO violation
7. **API Rate Limiting** (P3) - Payment API 429 errors
8. **Certificate Expiration** (P2) - SSL cert expires in 3 days
9. **Kubernetes Pod CrashLoop** (P1) - 8 pods ImagePullBackOff
10. **Message Queue Backlog** (P3) - RabbitMQ 25K messages queued
11. **Monitoring System Down** (P2) - Prometheus cluster unreachable
12. **DNS Service Degradation** (P2) - 30% DNS query failure
13. **Load Balancer Health** (P2) - 4 of 6 backends unhealthy
14. **Critical Vulnerability** (P2) - OpenSSL CVE CVSS 9.8
15. **Maintenance Window** (P4) - Scheduled DB maintenance reminder

## ServiceNow Field Reference

### Core Fields
- `number` - Incident number (INC0010001)
- `sys_id` - Unique system ID
- `state` - 1=New, 2=In Progress, 6=Resolved, 7=Closed
- `priority` - 1=Critical, 2=High, 3=Moderate, 4=Low
- `category` / `subcategory` - Classification
- `configuration_item` - CMDB CI
- `assignment_group` / `assigned_to` - Ownership

### Custom Fields (u_*)
- `u_automated_remediation` - Auto-fix enabled (true/false)
- `u_affected_users` - Impact count
- `u_revenue_impact` - Financial impact level
- `u_technical_details` - Error details
- `u_cvss_score` - Vulnerability score
- `u_threat_level` - Security threat level
- Plus 10+ more scenario-specific fields

## Testing

### Create Test Incidents

```bash
# List available scenarios
ansible-playbook test_servicenow_create_incidents.yml -e list_scenarios=true

# Create all incidents
ansible-playbook test_servicenow_create_incidents.yml

# Create specific scenario
ansible-playbook test_servicenow_create_incidents.yml -e scenario_filter="Database"
```

### Start EDA Polling

```bash
ansible-rulebook -i localhost \
  --rulebook ../rulebooks/servicenow_incidents_multi_scenario.yml
```

## EDA Condition Examples

```yaml
# Critical incidents only
condition: >
  event.priority == "1" and
  event.u_automated_remediation == "true"

# Database issues
condition: >
  event.category == "Database" and
  event.priority | int <= 2

# Security incidents with high CVSS
condition: >
  event.category == "Security" and
  event.u_cvss_score | float >= 9.0

# New incidents only (prevent duplicate processing)
condition: >
  event.sys_mod_count == "0" and
  event.active == "true"
```

## Workflow Pattern

1. **EDA Detects New Incident** (state=1, sys_mod_count=0)
2. **Update to In Progress** (state=2, add work notes)
3. **Execute Remediation** (run job template/workflow)
4. **Validate Success** (health check, alert closure)
5. **Update to Resolved** (state=6, close notes) OR Escalate (state=3)

## Best Practices

✅ Use `u_automated_remediation` flag for opt-in  
✅ Check `sys_mod_count == "0"` to avoid duplicates  
✅ Update work_notes for audit trail  
✅ Never auto-close (state=7) - let humans verify  
✅ Validate remediation before resolving  
✅ Set appropriate priority thresholds  

## ServiceNow API Queries

```bash
# Active priority 1 incidents
curl "https://${SN_HOST}/api/now/table/incident?sysparm_query=active=true^priority=1" \
  -u "${SN_USERNAME}:${SN_PASSWORD}"

# Incidents ready for automation
curl "https://${SN_HOST}/api/now/table/incident?sysparm_query=active=true^u_automated_remediation=true^state=1" \
  -u "${SN_USERNAME}:${SN_PASSWORD}"
```

## Integration with AAP

Required Job Templates:
- Application Emergency Restart
- Database Performance Tuning
- Storage Cleanup and Archival
- Firewall Block Malicious IP
- Certificate Auto Renewal
- Kubernetes Pod Recovery
- Message Queue Consumer Scaling
- Emergency Security Patching
- ServiceNow Update Incident

## Troubleshooting

**EDA not polling?**
- Check credentials: `SN_HOST`, `SN_USERNAME`, `SN_PASSWORD`
- Test API: `curl -u user:pass https://${SN_HOST}/api/now/table/incident?sysparm_limit=1`
- Check EDA activation logs

**Conditions not matching?**
- Use `print_event` to see actual event structure
- Field names are case-sensitive
- States are strings: "1" not 1
- Use filters: `event.priority | int`

**Duplicate processing?**
- Add condition: `event.sys_mod_count == "0"`
- Track processed incidents externally
- Use ServiceNow assignment to prevent re-trigger

## References

- [ServiceNow REST API](https://developer.servicenow.com/dev.do#!/reference/api/latest/rest)
- [ServiceNow ITSM Collection](https://github.com/ansible-collections/servicenow.itsm)
- [Ansible EDA Docs](https://ansible.readthedocs.io/projects/eda/)
