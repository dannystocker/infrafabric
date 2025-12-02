# InfraFabric Alert Rules - Deployment Checklist

**Created by:** Agent A32
**Date:** 2025-11-30
**Status:** Ready for Deployment

---

## Pre-Deployment Verification

### File Existence Check
- [ ] `/home/setup/infrafabric/monitoring/prometheus/alerts/p0_critical.yml` (5.2K)
- [ ] `/home/setup/infrafabric/monitoring/prometheus/alerts/p1_high.yml` (5.3K)
- [ ] `/home/setup/infrafabric/monitoring/prometheus/alerts/p2_medium.yml` (4.4K)
- [ ] `/home/setup/infrafabric/monitoring/prometheus/alertmanager.yml` (4.9K)
- [ ] `/home/setup/infrafabric/monitoring/prometheus/alert_templates.tmpl` (3.8K)
- [ ] `/home/setup/infrafabric/monitoring/prometheus/prometheus.yml` (2.3K)
- [ ] `/home/setup/infrafabric/monitoring/prometheus/RUNBOOK_STRUCTURE.md` (9.7K)

### Syntax Validation
```bash
# Check alert rule syntax
promtool check rules /home/setup/infrafabric/monitoring/prometheus/alerts/p0_critical.yml
promtool check rules /home/setup/infrafabric/monitoring/prometheus/alerts/p1_high.yml
promtool check rules /home/setup/infrafabric/monitoring/prometheus/alerts/p2_medium.yml

# Check AlertManager config
amtool config routes < /home/setup/infrafabric/monitoring/prometheus/alertmanager.yml

# Check Prometheus config
promtool check config /home/setup/infrafabric/monitoring/prometheus/prometheus.yml
```

---

## Stage 1: Prepare Environment

### Set Environment Variables
```bash
# Add to ~/.bashrc or systemd service file
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/ID'
export PAGERDUTY_SERVICE_KEY='YOUR_SERVICE_KEY'
export ALERTS_EMAIL='alerts@infrafabric.local'
export ALERTMANAGER_FROM_EMAIL='prometheus@infrafabric.local'
export SMTP_HOST='mail.infrafabric.local'
export SMTP_PORT='587'
export SMTP_USER='alertmanager'
export SMTP_PASSWORD='YOUR_PASSWORD'
```

- [ ] Create Slack webhook: https://api.slack.com/messaging/webhooks
- [ ] Get PagerDuty service key from integration settings
- [ ] Configure SMTP relay credentials
- [ ] Export variables in /etc/systemd/system/alertmanager.service
- [ ] Test each integration independently

### Create Required Directories
```bash
sudo mkdir -p /etc/prometheus/rules
sudo mkdir -p /etc/alertmanager/templates
sudo mkdir -p /docs/runbooks
sudo chown prometheus:prometheus /etc/prometheus/rules
sudo chown alertmanager:alertmanager /etc/alertmanager
```

- [ ] All directories created with correct permissions
- [ ] Verified ownership and permissions

---

## Stage 2: Deploy Configuration Files

### Copy Alert Rules
```bash
sudo cp /home/setup/infrafabric/monitoring/prometheus/alerts/p0_critical.yml \
        /etc/prometheus/rules/
sudo cp /home/setup/infrafabric/monitoring/prometheus/alerts/p1_high.yml \
        /etc/prometheus/rules/
sudo cp /home/setup/infrafabric/monitoring/prometheus/alerts/p2_medium.yml \
        /etc/prometheus/rules/
sudo chown prometheus:prometheus /etc/prometheus/rules/*.yml
```

- [ ] p0_critical.yml copied
- [ ] p1_high.yml copied
- [ ] p2_medium.yml copied
- [ ] File permissions correct

### Copy AlertManager Configuration
```bash
sudo cp /home/setup/infrafabric/monitoring/prometheus/alertmanager.yml \
        /etc/alertmanager/alertmanager.yml
sudo chown alertmanager:alertmanager /etc/alertmanager/alertmanager.yml
sudo chmod 644 /etc/alertmanager/alertmanager.yml
```

- [ ] alertmanager.yml copied
- [ ] File ownership correct
- [ ] File permissions correct

### Copy Templates
```bash
sudo cp /home/setup/infrafabric/monitoring/prometheus/alert_templates.tmpl \
        /etc/alertmanager/templates/alerts.tmpl
sudo chown alertmanager:alertmanager /etc/alertmanager/templates/alerts.tmpl
```

- [ ] alert_templates.tmpl copied
- [ ] File ownership correct

### Copy Prometheus Config
```bash
# Backup existing config
sudo cp /etc/prometheus/prometheus.yml \
        /etc/prometheus/prometheus.yml.backup.$(date +%Y%m%d_%H%M%S)

# Copy new config
sudo cp /home/setup/infrafabric/monitoring/prometheus/prometheus.yml \
        /etc/prometheus/prometheus.yml
```

- [ ] Existing config backed up
- [ ] New prometheus.yml copied
- [ ] File ownership correct

---

## Stage 3: Validate Configuration

### Validate Alert Rules
```bash
promtool check rules /etc/prometheus/rules/p0_critical.yml
promtool check rules /etc/prometheus/rules/p1_high.yml
promtool check rules /etc/prometheus/rules/p2_medium.yml

# Expected output: "SUCCESS"
```

- [ ] p0_critical.yml validates
- [ ] p1_high.yml validates
- [ ] p2_medium.yml validates

### Validate AlertManager Config
```bash
amtool config routes
amtool config receivers
amtool test-notification -a MyAlert -s firing

# Expected: No errors in output
```

- [ ] AlertManager routes valid
- [ ] AlertManager receivers valid
- [ ] Test notification sent

### Validate Prometheus Config
```bash
promtool check config /etc/prometheus/prometheus.yml

# Expected output: "SUCCESS"
```

- [ ] prometheus.yml validates
- [ ] No syntax errors

---

## Stage 4: Deploy & Reload Services

### Reload Prometheus
```bash
sudo systemctl reload prometheus

# Monitor for errors
sudo journalctl -u prometheus -f
# Should show: "Completed loading of configuration file"
```

- [ ] Prometheus reloaded successfully
- [ ] No errors in logs
- [ ] Rules loaded in Prometheus UI: http://localhost:9090/rules

### Reload AlertManager
```bash
sudo systemctl reload alertmanager

# Monitor for errors
sudo journalctl -u alertmanager -f
# Should show: "config reloaded successfully"
```

- [ ] AlertManager reloaded successfully
- [ ] No errors in logs
- [ ] AlertManager UI accessible: http://localhost:9093

### Verify Service Health
```bash
# Prometheus health
curl http://localhost:9090/-/healthy
# Expected: 200 OK

# AlertManager health
curl http://localhost:9093/-/healthy
# Expected: 200 OK
```

- [ ] Prometheus health check passes
- [ ] AlertManager health check passes

---

## Stage 5: Integration Testing

### Test Alert Routing (P0)
```bash
# Manually fire a P0 alert
amtool alert add AgentDeathDetected severity=critical component=agent_swarm

# Monitor notifications:
# - Check #incidents Slack channel (should appear in <10 sec)
# - Check PagerDuty (should trigger page in <30 sec)
# - Check email inbox (should arrive in <5 min)
```

- [ ] Slack notification received in #incidents
- [ ] PagerDuty page triggered
- [ ] Email received in critical alerts list
- [ ] Acknowledge page in PagerDuty

### Test Alert Routing (P1)
```bash
# Manually fire a P1 alert
amtool alert add HighErrorRate severity=high component=api_reliability

# Monitor notifications:
# - Check #alerts Slack channel (should appear in <10 sec)
# - Check email (should arrive in <5 min)
```

- [ ] Slack notification received in #alerts
- [ ] Email received

### Test Alert Routing (P2)
```bash
# Manually fire a P2 alert
amtool alert add HighLoadCondition severity=medium component=api_load

# Monitor notifications:
# - Check #monitoring Slack channel (batched every 30 min)
# - Should NOT trigger email
```

- [ ] Slack notification received in #monitoring
- [ ] No immediate email sent

### Test Inhibition Rules
```bash
# Fire P0 and P1 alerts for same component
amtool alert add AgentDeathDetected severity=critical
amtool alert add EscalateSpikeSpeechAct severity=medium

# Verify: P2 alert should be inhibited
# Only P0 notification should appear
```

- [ ] P0 alerts page/notify
- [ ] P2 alerts inhibited when P0 fires
- [ ] Noise reduction working

### Test Runbook Links
```bash
# Verify runbook links in alerts
curl http://localhost:9090/api/v1/alerts | jq '.data[].annotations.runbook_url'

# Expected: URLs pointing to /docs/runbooks/...
```

- [ ] All alerts have runbook_url annotations
- [ ] URLs format correct

---

## Stage 6: Create Runbook Files

### Generate Runbook Template
```bash
# Copy template for each alert
for alert in agent_restart redis_recovery chromadb_recovery api_recovery \
             consensus_recovery memory_recovery latency_investigation \
             error_rate_investigation queue_management conflict_resolution \
             cache_optimization disk_expansion load_balancing query_optimization \
             agent_diagnostics consensus_tuning redis_tuning; do
  cp /home/setup/infrafabric/monitoring/prometheus/RUNBOOK_TEMPLATE.md \
     /docs/runbooks/${alert}.md
done
```

- [ ] All 17 runbook template files created

### Fill in Runbook Content
For each runbook file:
- [ ] Add quick diagnosis commands
- [ ] Write 3-5 remediation steps
- [ ] Add verification procedures
- [ ] Define escalation criteria
- [ ] Include prevention recommendations
- [ ] Get peer review from team leads

---

## Stage 7: Documentation & Training

### Update Documentation
- [ ] Create RUNBOOK_INDEX.md with all 17 runbooks
- [ ] Update on-call documentation
- [ ] Create alert escalation flowchart
- [ ] Document SLA response times by severity
- [ ] Create FAQ for common false positives

### Team Training
- [ ] Conduct alert system overview (30 min)
- [ ] Walk through P0 alert response (hands-on, 30 min)
- [ ] Walk through P1 alert response (hands-on, 30 min)
- [ ] Review runbook procedures (15 min)
- [ ] Test page acknowledgment workflow (15 min)
- [ ] Review false positive tuning process (15 min)

### Schedule
- [ ] Training session for primary on-call
- [ ] Training session for backup on-call
- [ ] Training session for platform team
- [ ] Training session for DevOps team
- [ ] All team members sign-off on procedures

---

## Stage 8: Monitoring & Tuning

### Week 1: Monitor for False Positives
```bash
# Check alert firing rate
curl http://localhost:9090/api/v1/alerts?state=firing | jq '.data | length'

# Review PagerDuty incident history
# Review Slack #incidents for pattern

# Identify false positive alerts (high SNR)
# Document threshold adjustments needed
```

- [ ] Review all fired alerts for validity
- [ ] Document any false positives
- [ ] Identify threshold tuning needs

### Week 2-4: Baseline Metrics
```bash
# Collect 2-week baseline of:
# - Normal request latency (for P95 threshold)
# - Normal error rate
# - Normal cache hit ratio
# - Normal queue depth
# - Normal disk usage pattern

# Adjust thresholds based on baseline
```

- [ ] Collected baseline metrics
- [ ] Adjusted thresholds if needed
- [ ] Documented baseline values

### Month 2: Operational Metrics
- [ ] Mean time to detect (MTTD) per alert
- [ ] Mean time to acknowledge (MTTA)
- [ ] Mean time to resolution (MTTR) per alert
- [ ] False positive rate per alert
- [ ] Runbook effectiveness rating

---

## Stage 9: Production Hardening

### Performance Testing
```bash
# Test with 100x normal alert load
# Verify AlertManager handles batching
# Check memory usage under load
# Monitor Prometheus CPU during heavy evaluation
```

- [ ] Alerting system handles 100x load
- [ ] No memory leaks observed
- [ ] No performance degradation

### Security Hardening
- [ ] Restrict AlertManager API access (firewall rules)
- [ ] Enable HTTPS for AlertManager UI
- [ ] Rotate SMTP credentials
- [ ] Audit PagerDuty integration keys
- [ ] Implement alert audit logging

### Backup & Recovery
```bash
# Backup configurations
sudo tar czf /backup/prometheus_configs_$(date +%Y%m%d).tar.gz \
  /etc/prometheus /etc/alertmanager /docs/runbooks

# Test recovery procedure
```

- [ ] Configurations backed up
- [ ] Recovery tested
- [ ] Disaster recovery plan documented

---

## Stage 10: Go-Live

### Pre-Flight Checklist
- [ ] All configurations deployed
- [ ] All integrations tested
- [ ] All runbooks created and reviewed
- [ ] Team trained and signed off
- [ ] Baselines established
- [ ] Escalation paths verified
- [ ] Incident response tested

### Go-Live Steps
1. [ ] Schedule maintenance window (non-business hours)
2. [ ] Notify stakeholders
3. [ ] Deploy to production
4. [ ] Monitor alerts for first 24 hours
5. [ ] Document any issues
6. [ ] Adjust based on initial observations
7. [ ] Hold post-deployment review meeting

### Post-Deployment (Week 1)
- [ ] Daily review of alert metrics
- [ ] Tune any false positives
- [ ] Document lessons learned
- [ ] Update runbooks based on actual use
- [ ] Celebrate successful deployment!

---

## Troubleshooting

### Alerts not firing?
```bash
# Check rule evaluation
curl http://localhost:9090/api/v1/rules

# Check AlertManager status
amtool status

# Check logs
sudo journalctl -u prometheus -n 50
sudo journalctl -u alertmanager -n 50
```

### Notifications not arriving?
```bash
# Test Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -d '{"text":"test"}' \
  -H 'Content-Type: application/json'

# Check SMTP configuration
echo "test" | mail -S smtp=smtp://user@host:587 -S smtp-use-starttls recipient@example.com

# Check email logs
sudo grep alertmanager /var/log/mail.log
```

### High false positive rate?
- Increase threshold values gradually
- Extend evaluation window (for)
- Review baseline metrics
- Document exceptions for specific circumstances
- Consider adding more specific label selectors

---

## Sign-Off

**Deployment Lead:** _____________________ Date: _________

**SRE Team Lead:** _____________________ Date: _________

**Platform Lead:** _____________________ Date: _________

**Security Review:** _____________________ Date: _________

---

## References

- Alert Rules Summary: `/home/setup/infrafabric/monitoring/prometheus/ALERT_RULES_SUMMARY.md`
- Runbook Structure: `/home/setup/infrafabric/monitoring/prometheus/RUNBOOK_STRUCTURE.md`
- Delivery Report: `/home/setup/infrafabric/AGENT_A32_ALERT_RULES_DELIVERY.md`

