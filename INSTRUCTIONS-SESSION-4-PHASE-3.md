# Session 4 (SIP) - Phase 3

**Status:** Phase 2 Complete ✅
**Next:** Production Deployment

## Task 1: Production Deployment (Sonnet)
- Deploy Kamailio SIP proxy to production
- Enable TLS on port 5061
- Configure firewall rules, rate limiting
- **File:** deploy/kamailio-production.yml

## Task 2: Real External Expert Test (Sonnet)
- Schedule real external SIP call with actual expert
- Validate full flow: SIP→H.323→WebRTC→NDI
- Success: <2s setup, <100ms latency, all IF.witness logs
- **File:** tests/production/real_expert_test.py

## Task 3: Production Runbook (Haiku)
- Emergency procedures, restart commands
- Monitoring dashboards, alert thresholds
- **File:** docs/SIP-PRODUCTION-RUNBOOK.md

**Completion:** Commit, STATUS-PHASE-3.md, auto-poll Phase 4

**Estimated:** 6 hours, $12
**GO NOW**
