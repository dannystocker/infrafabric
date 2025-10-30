# Google Cloud CLI Setup for InfraFabric Verification

## ✅ Installation Complete

The Google Cloud CLI (gcloud) has been installed successfully at:
- **Install Location**: `~/google-cloud-sdk/`
- **Binary**: `~/google-cloud-sdk/bin/gcloud`
- **Version**: 545.0.0

The CLI has been added to your PATH in `~/.bashrc` permanently.

---

## Quick Start (5 Minutes)

### Step 1: Initialize gcloud

```bash
# Reload your bash profile
source ~/.bashrc

# Initialize gcloud (opens browser for authentication)
gcloud init
```

This will:
1. Authenticate you with your Google Cloud account
2. Let you select a project (or create new one)
3. Set default region/zone

### Step 2: Enable Required APIs

```bash
# Enable Custom Search API (for contact verification)
gcloud services enable customsearch.googleapis.com

# Check enabled services
gcloud services list --enabled
```

### Step 3: Create API Credentials

```bash
# Option A: Using gcloud CLI
gcloud services enable apikeys --project=YOUR_PROJECT_ID

# Then create API key via console (easier):
# https://console.cloud.google.com/apis/credentials
```

**Or use the Google Cloud Console** (recommended):

1. Go to [API Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **+ CREATE CREDENTIALS** → **API key**
3. Copy the key (starts with `AIza...`)
4. (Optional) Restrict to Custom Search API only

---

## For InfraFabric Contact Verification

### Enable Custom Search API

```bash
# 1. Enable the API
gcloud services enable customsearch.googleapis.com --project=YOUR_PROJECT_ID

# 2. Get your project ID
gcloud config get-value project

# 3. Create Custom Search Engine
# Go to: https://programmablesearchengine.google.com/
# - Click "Add" or "Get started"
# - Search entire web: Enable
# - Get the Search Engine ID
```

### Set Environment Variables

```bash
# Add to ~/.bashrc for persistence
echo 'export GOOGLE_API_KEY="AIzaSy..."' >> ~/.bashrc
echo 'export GOOGLE_CSE_ID="your-cse-id..."' >> ~/.bashrc
echo 'export GOOGLE_CLOUD_PROJECT="your-project-id"' >> ~/.bashrc

# Reload
source ~/.bashrc
```

### Test Your Setup

```bash
# Test API key
curl "https://www.googleapis.com/customsearch/v1?key=$GOOGLE_API_KEY&cx=$GOOGLE_CSE_ID&q=test"

# Should return JSON with search results
```

---

## Education/Student Account

If you have a Google Cloud Education account:

### Activate Education Credits

```bash
# 1. Go to: https://edu.google.com/programs/credits/
# 2. Sign up with your .edu email
# 3. Receive $50-300 in credits
# 4. Apply credits to your project

# Check billing account
gcloud billing accounts list

# Check remaining credits
# Go to: https://console.cloud.google.com/billing
```

### Benefits

With education credits you get:
- ✅ 100 Custom Search queries/day FREE (always)
- ✅ After free quota: ~$5 per 1000 queries
- ✅ $50-300 credits = 10,000-60,000 queries
- ✅ Perfect for InfraFabric verification (84 contacts = ~1000 queries)

---

## Common gcloud Commands

### Authentication

```bash
# Login
gcloud auth login

# List accounts
gcloud auth list

# Set active account
gcloud config set account ACCOUNT_EMAIL

# Application default credentials (for SDKs)
gcloud auth application-default login
```

### Projects

```bash
# List projects
gcloud projects list

# Get current project
gcloud config get-value project

# Set project
gcloud config set project PROJECT_ID

# Create new project
gcloud projects create NEW_PROJECT_ID --name="InfraFabric Verification"
```

### APIs & Services

```bash
# List enabled APIs
gcloud services list --enabled

# Enable an API
gcloud services enable customsearch.googleapis.com

# Disable an API
gcloud services disable customsearch.googleapis.com
```

### Billing

```bash
# List billing accounts
gcloud billing accounts list

# Link project to billing
gcloud billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT_ID

# Check billing status
gcloud billing projects describe PROJECT_ID
```

### Credentials & Keys

```bash
# List API keys
gcloud services api-keys list

# Create API key (if supported)
gcloud services api-keys create --display-name="InfraFabric Verifier"

# Note: For Custom Search, use console for key creation (easier)
```

---

## Quota & Usage Monitoring

### Check API Quota

```bash
# View quota for Custom Search API
gcloud services quota list \
  --service=customsearch.googleapis.com \
  --consumer=projects/YOUR_PROJECT_ID

# Monitor usage
gcloud logging read "resource.type=api" --limit 50
```

### Set Up Quota Alerts

1. Go to [Quotas](https://console.cloud.google.com/iam-admin/quotas)
2. Select **Custom Search API**
3. Click **Edit Quotas**
4. Set alert at 80% of daily limit (80 queries)

---

## InfraFabric Verification Setup Checklist

- [ ] gcloud installed ✅ (already done)
- [ ] Authenticated: `gcloud auth login`
- [ ] Project selected: `gcloud config set project PROJECT_ID`
- [ ] Custom Search API enabled: `gcloud services enable customsearch.googleapis.com`
- [ ] API key created: https://console.cloud.google.com/apis/credentials
- [ ] Custom Search Engine created: https://programmablesearchengine.google.com/
- [ ] Environment variables set: `GOOGLE_API_KEY`, `GOOGLE_CSE_ID`
- [ ] Tested: `python3 auto_verify_contacts.py --max 5`

---

## Next Steps

### 1. Complete Setup

```bash
# Initialize gcloud
gcloud init

# Enable Custom Search API
gcloud services enable customsearch.googleapis.com
```

### 2. Get Credentials

- API Key: https://console.cloud.google.com/apis/credentials
- CSE ID: https://programmablesearchengine.google.com/

### 3. Run Verification

```bash
cd /home/setup/infrafabric/marketing/page-zero

export GOOGLE_API_KEY="your-key"
export GOOGLE_CSE_ID="your-cse-id"

python3 auto_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified-test.csv \
  --max 5
```

---

## Troubleshooting

### Issue: "gcloud: command not found"

**Fix**: Reload bash configuration
```bash
source ~/.bashrc
# Or restart terminal
```

### Issue: "API not enabled"

**Fix**: Enable the API
```bash
gcloud services enable customsearch.googleapis.com
```

### Issue: "Quota exceeded"

**Check usage**:
```bash
# View recent API calls
gcloud logging read "resource.type=api AND resource.labels.service=customsearch.googleapis.com" --limit 100 --format=json
```

**Fix**: Wait until tomorrow (quota resets at midnight PST) or enable billing

### Issue: "Invalid API key"

**Fix**: Verify key restrictions
1. Go to https://console.cloud.google.com/apis/credentials
2. Click on your API key
3. Check "API restrictions" - should allow Custom Search API
4. Check "Application restrictions" - should allow all or your IP

---

## Cost Management

### Monitor Spending

```bash
# Check billing
gcloud billing accounts list

# View cost estimate
# Go to: https://console.cloud.google.com/billing/reports
```

### Set Budget Alerts

1. Go to [Budgets & Alerts](https://console.cloud.google.com/billing/budgets)
2. Click **CREATE BUDGET**
3. Set budget: $10/month (covers 2000 verification queries)
4. Set alerts at: 50%, 75%, 90%, 100%

### Free Tier Optimization

To stay in free tier (100 queries/day):
- Verify ~9 contacts/day (11 queries each)
- Process 84 contacts over 10 days
- Total cost: $0

---

## Additional Resources

**Google Cloud Console**: https://console.cloud.google.com/
**Custom Search API Docs**: https://developers.google.com/custom-search/v1/overview
**gcloud CLI Docs**: https://cloud.google.com/sdk/gcloud
**Education Credits**: https://edu.google.com/programs/credits/

**InfraFabric Docs**:
- `VERIFICATION-SETUP-GUIDE.md` - Complete verification setup
- `QUICKSTART.md` - 30-minute launch guide
- `auto_verify_contacts.py --help` - Script usage

---

## Current Status

✅ **gcloud CLI installed** (version 545.0.0)
✅ **Added to PATH** (in ~/.bashrc)
✅ **Ready to initialize** (run `gcloud init`)

**Next**: Run `gcloud init` to authenticate and set up your project.
