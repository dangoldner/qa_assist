
# Google Cloud setup:

**One-Time Project Setup:**
- [ ] Enable APIs: Cloud Run, Cloud Scheduler, Secret Manager, Gmail, Google Docs, Google Sheets, IAM Service Account Credentials
- [ ] Enable billing and set budget alert

**Service Account Configuration:**
- [ ] Create service account: `docs-updater@qa-assistant-458920.iam.gserviceaccount.com`
- [ ] Grant **Service Account Token Creator** role to itself (for keyless JWT signing)
- [ ] Configure domain-wide delegation in Google Workspace Admin Console with scopes: `gmail.readonly`, `documents`, `spreadsheets`

**Secret Management:**
- [ ] Create secret `anthropic-api-key` in Secret Manager
- [ ] Grant `docs-updater` service account **Secret Manager Secret Accessor** role

**Per-Function Deployment:**
- [ ] Deploy function with runtime service account set to `docs-updater`
- [ ] Reference `anthropic-api-key` as environment variable
- [ ] Grant `docs-updater` **Cloud Run Invoker** role on the deployed function

**Scheduler Setup:**
- [ ] Create job with OIDC auth using `docs-updater` service account
- [ ] Set schedule and timezone appropriately
