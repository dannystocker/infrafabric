# Session Report: SSL Configuration for us-mid.digital-lab.ca

**Date:** 2025-11-30
**Session Type:** Infrastructure - SSL/TLS Configuration
**Status:** COMPLETED

## Summary

Successfully configured SSL/TLS for `us-mid.digital-lab.ca` on Proxmox container 200 (85.239.243.227).

## What Was Done

### 1. SSL Certificate Acquisition (acme.sh)
- **Tool Used:** acme.sh (pure shell ACME client) instead of certbot
- **Reason:** certbot had Python urllib3 dependency conflicts in the container, and snap wasn't available in LXC
- **CA:** ZeroSSL (default CA for acme.sh)
- **Certificate Type:** ECC (ECDSA)
- **Validity:** Nov 30, 2025 - Feb 28, 2026 (90 days)

**Installation command:**
```bash
curl https://get.acme.sh | sh -s email=danny@digital-lab.ca
/root/.acme.sh/acme.sh --issue -d us-mid.digital-lab.ca --nginx
```

### 2. Certificate Installation
Certificates installed to:
- **Key:** `/etc/ssl/private/us-mid.digital-lab.ca.key`
- **Full Chain:** `/etc/ssl/certs/us-mid.digital-lab.ca.fullchain.pem`

Auto-renewal configured via acme.sh cron job.

### 3. Nginx Configuration
Updated `/etc/nginx/sites-available/if-emotion` with:
- HTTP to HTTPS redirect (301)
- SSL with TLS 1.2/1.3
- HTTP/2 enabled
- HSTS (max-age=63072000)
- Strong cipher suite (ECDHE-ECDSA/RSA-AES-GCM)

### 4. Port Forwarding (Proxmox NAT)
Added DNAT rules on Proxmox host to forward traffic to container 200:
```bash
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 85.239.243.230:80
iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 85.239.243.230:443
```

**Rules saved to:** `/etc/iptables.rules` with restoration via `/etc/rc.local`

## Architecture

```
Internet
    |
    v
us-mid.digital-lab.ca (DNS -> 85.239.243.227)
    |
    v
Proxmox Host (85.239.243.227)
    | NAT DNAT: 80->85.239.243.230:80, 443->85.239.243.230:443
    v
Container 200 (85.239.243.230)
    |
    v
nginx (ports 80, 443)
    | HTTP -> 301 redirect to HTTPS
    | HTTPS -> proxy to backend
    v
Claude Max API (127.0.0.1:3001)
```

## Verification

```bash
# HTTPS responds with HTTP/2 and HSTS
curl -sI https://us-mid.digital-lab.ca
HTTP/2 200
strict-transport-security: max-age=63072000

# HTTP redirects to HTTPS
curl -sI http://us-mid.digital-lab.ca
HTTP/1.1 301 Moved Permanently
Location: https://us-mid.digital-lab.ca/

# Certificate details
openssl s_client -connect us-mid.digital-lab.ca:443 -servername us-mid.digital-lab.ca
issuer=C = AT, O = ZeroSSL, CN = ZeroSSL ECC Domain Secure Site CA
subject=CN = us-mid.digital-lab.ca
```

## Important Files (Container 200)

| Path | Purpose |
|------|---------|
| `/etc/nginx/sites-available/if-emotion` | Nginx config with SSL |
| `/etc/ssl/certs/us-mid.digital-lab.ca.fullchain.pem` | SSL certificate |
| `/etc/ssl/private/us-mid.digital-lab.ca.key` | SSL private key |
| `/root/.acme.sh/` | acme.sh installation and renewal scripts |
| `/var/www/html/` | if.emotion React app build |

## Important Files (Proxmox Host)

| Path | Purpose |
|------|---------|
| `/etc/iptables.rules` | Saved NAT rules |
| `/etc/rc.local` | Restores iptables rules on boot |

## Certificate Renewal

acme.sh automatically renews certificates via cron. Manual renewal:
```bash
/root/.acme.sh/acme.sh --renew -d us-mid.digital-lab.ca --force
```

## Known Issues / Gotchas

1. **certbot broken:** Do NOT use apt certbot - urllib3 conflicts in Python 3.13
2. **snap unavailable:** LXC containers can't run snapd
3. **Port forwarding required:** Traffic to ports 80/443 on Proxmox host must be DNAT'd to container
4. **nginx reload vs restart:** After SSL config changes, use `systemctl restart nginx` not just reload to pick up new listeners

## Related Documents

- IF.guard Debate: `/home/setup/infrafabric/docs/debates/IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30.md`
- Claude Max Wrapper Design: `/home/setup/if-emotion-ux/CLAUDE_MAX_OPENWEBUI_WRAPPER_DESIGN.md`
- E2E Test Suite: `/home/setup/if-emotion-ux/e2e-test.cjs`

## Live URLs

- **HTTPS (production):** https://us-mid.digital-lab.ca
- **API endpoint:** https://us-mid.digital-lab.ca/api/

## Next Steps (For Future Sessions)

1. Connect Claude Max backend to if.emotion frontend (API integration incomplete)
2. Start Sergio Personality DNA ChromaDB service
3. Test chat functionality end-to-end
4. Consider adding www subdomain to SSL certificate
5. Set up monitoring for certificate expiration (Feb 28, 2026)
