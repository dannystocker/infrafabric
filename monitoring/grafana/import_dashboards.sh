#!/bin/bash

###############################################################################
# InfraFabric Grafana Dashboard Import Script
#
# Purpose: Automated bulk import of all 5 Grafana dashboards
# Usage: ./import_dashboards.sh <grafana_url> <api_key>
# Example: ./import_dashboards.sh http://localhost:3000 your_api_key_here
#
# Prerequisites:
#   - jq: JSON query tool (apt-get install jq)
#   - curl: HTTP client (pre-installed on most systems)
#   - Grafana admin API key (Settings → API Keys → New API Key)
#
###############################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GRAFANA_URL="${1:-http://localhost:3000}"
GRAFANA_API_KEY="${2:-}"
DASHBOARD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/dashboards"

# Dashboards to import
DASHBOARDS=(
    "swarm_overview.json"
    "redis_performance.json"
    "chromadb_performance.json"
    "agent_health.json"
    "api_ux.json"
)

###############################################################################
# Functions
###############################################################################

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check jq
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed"
        echo "Install with: sudo apt-get install jq"
        exit 1
    fi
    print_success "jq found"

    # Check curl
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed"
        exit 1
    fi
    print_success "curl found"

    # Check dashboard directory
    if [ ! -d "$DASHBOARD_DIR" ]; then
        print_error "Dashboard directory not found: $DASHBOARD_DIR"
        exit 1
    fi
    print_success "Dashboard directory found: $DASHBOARD_DIR"
}

validate_grafana() {
    print_header "Validating Grafana Connection"

    print_info "Testing connection to: $GRAFANA_URL"

    # Test API connectivity
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $GRAFANA_API_KEY" \
        "$GRAFANA_URL/api/health")

    if [ "$response" -eq 200 ]; then
        print_success "Connected to Grafana"
    else
        print_error "Failed to connect to Grafana (HTTP $response)"
        echo "Verify:"
        echo "  1. Grafana URL is correct: $GRAFANA_URL"
        echo "  2. API key is valid (Settings → API Keys → New API Key)"
        echo "  3. Grafana service is running"
        exit 1
    fi

    # Get Grafana version
    version=$(curl -s -H "Authorization: Bearer $GRAFANA_API_KEY" \
        "$GRAFANA_URL/api/health" | jq -r '.version')
    print_info "Grafana version: $version"

    # Validate Prometheus datasource exists
    ds_response=$(curl -s -H "Authorization: Bearer $GRAFANA_API_KEY" \
        "$GRAFANA_URL/api/datasources" | jq '.[] | select(.type=="prometheus") | .id')

    if [ -z "$ds_response" ]; then
        print_warning "No Prometheus datasource found in Grafana"
        print_info "Create one at: $GRAFANA_URL/connections/datasources/prometheus"
        echo "Configure:"
        echo "  Name: Prometheus"
        echo "  URL: http://prometheus:9090"
        echo "  Access: Server"
    else
        print_success "Prometheus datasource found (ID: $ds_response)"
    fi
}

import_dashboard() {
    local dashboard_file="$1"
    local dashboard_name="${dashboard_file%.json}"

    print_info "Importing: $dashboard_name"

    # Read dashboard JSON
    if [ ! -f "$DASHBOARD_DIR/$dashboard_file" ]; then
        print_error "Dashboard file not found: $DASHBOARD_DIR/$dashboard_file"
        return 1
    fi

    # Prepare dashboard payload (wrap in 'dashboard' object for API)
    payload=$(jq -n \
        --slurpfile dashboard "$DASHBOARD_DIR/$dashboard_file" \
        '{
            dashboard: $dashboard[0],
            overwrite: true
        }')

    # Make API request
    response=$(curl -s \
        -X POST \
        -H "Authorization: Bearer $GRAFANA_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$GRAFANA_URL/api/dashboards/db")

    # Check response
    error=$(echo "$response" | jq -r '.message // empty')
    dashboard_id=$(echo "$response" | jq -r '.id // empty')
    dashboard_uid=$(echo "$response" | jq -r '.uid // empty')

    if [ -n "$error" ] && [ "$error" != "null" ]; then
        print_error "Failed to import $dashboard_name: $error"
        return 1
    fi

    if [ -n "$dashboard_id" ] && [ "$dashboard_id" != "null" ]; then
        print_success "Imported: $dashboard_name (ID: $dashboard_id, UID: $dashboard_uid)"
        echo "  URL: $GRAFANA_URL/d/$dashboard_uid"
        return 0
    else
        print_error "Unknown error importing $dashboard_name"
        echo "Response: $response"
        return 1
    fi
}

import_all_dashboards() {
    print_header "Importing Dashboards"

    local success_count=0
    local fail_count=0

    for dashboard in "${DASHBOARDS[@]}"; do
        if import_dashboard "$dashboard"; then
            ((success_count++))
        else
            ((fail_count++))
        fi
        echo ""
    done

    # Summary
    print_header "Import Summary"
    print_success "$success_count dashboards imported"

    if [ $fail_count -gt 0 ]; then
        print_error "$fail_count dashboards failed"
        exit 1
    fi

    print_info "All dashboards imported successfully!"
}

configure_alerts() {
    print_header "Optional: Configure Alerts"

    read -p "Configure alert rules? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping alert configuration"
        return
    fi

    print_info "Alert configuration would require:"
    echo "  1. Grafana Alerting (Settings → Alerting)"
    echo "  2. Notification channels (Slack, Email, PagerDuty, etc.)"
    echo "  3. Alert rules linked to dashboard panels"
    echo ""
    echo "See README.md section 'Advanced: Custom Alerts' for details"
}

print_next_steps() {
    print_header "Next Steps"

    echo "1. Verify dashboards imported:"
    echo "   Visit: $GRAFANA_URL/dashboards"
    echo ""
    echo "2. Configure metrics exporter:"
    echo "   - Implement Prometheus exporter (Python, Go, etc.)"
    echo "   - Reference: ../prometheus/METRICS_EXPORTER_SPEC.md"
    echo ""
    echo "3. Update Prometheus scrape config:"
    echo "   - Edit: /etc/prometheus/prometheus.yml"
    echo "   - Add job for swarm metrics (port 9091)"
    echo "   - Add job for API metrics (port 9092)"
    echo ""
    echo "4. View dashboards:"
    echo "   - Swarm Overview: $GRAFANA_URL/d/swarm_overview"
    echo "   - Redis Performance: $GRAFANA_URL/d/redis_performance"
    echo "   - ChromaDB Performance: $GRAFANA_URL/d/chromadb_performance"
    echo "   - Agent Health: $GRAFANA_URL/d/agent_health"
    echo "   - API & UX: $GRAFANA_URL/d/api_ux"
    echo ""
    echo "5. Create alert rules (optional):"
    echo "   - Configure notification channels first"
    echo "   - Set thresholds per README.md 'Advanced: Custom Alerts'"
}

###############################################################################
# Main
###############################################################################

main() {
    print_header "InfraFabric Grafana Dashboard Importer"

    # Validate inputs
    if [ -z "$GRAFANA_API_KEY" ]; then
        print_error "Usage: $0 <grafana_url> <api_key>"
        echo ""
        echo "Example:"
        echo "  $0 http://localhost:3000 glsa_your_api_key_here"
        echo ""
        echo "To create an API key in Grafana:"
        echo "  1. Go to: Configuration → API Keys"
        echo "  2. Click 'New API Key'"
        echo "  3. Set Role to 'Admin'"
        echo "  4. Copy the generated key"
        exit 1
    fi

    # Run checks
    check_prerequisites
    echo ""
    validate_grafana
    echo ""
    import_all_dashboards
    echo ""
    configure_alerts
    echo ""
    print_next_steps
}

# Run main if script is executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
