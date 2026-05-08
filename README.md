# Aluflow Sales & Operations CRM

Accountability-first Django CRM for **Aluflow Investments** — glass and aluminium fabrication, fitting and aftercare. The system has been deliberately shaped around the way the business actually works:

```
Lead  →  Plan-based Quote  →  Approval (auto-creates Customer + Job)
                                    ↓
       On-site re-measurement  →  optional Variation (only if larger)
                                    ↓
              Fabrication  →  Installation  →  Invoice  →  Payment
```

A lead becomes a customer **only when they accept a quote** — there is no separate "convert lead" step in the normal flow. The original quote stands unless on-site measurements come back **larger** than the plans, in which case a Variation is logged and approved.

Every meaningful action — every save, every status change, every webhook hit, every login — is written to a tamper-resistant **audit trail** so management can see exactly who did what and when.

Built with Django + PostgreSQL (SQLite for dev) + Django Templates + Tailwind CSS.

---

## 📦 Apps

| App | Purpose |
|---|---|
| `accounts` | Custom user model, 7 roles (Admin / Manager / Sales / Estimator / Installer / Storekeeper / Finance), authentication |
| `audit` | **Audit trail** — every create/update/delete + status change + login/logout, plus a public webhook endpoint for inbound leads |
| `dashboard` | KPI dashboard with live activity feed |
| `leads` | Leads pipeline with **proof-of-source attachments** (WhatsApp / Facebook screenshots, house plans) and a `source_url` field |
| `customers` | Customers + multiple Projects per customer |
| `quotations` | Quotations to **leads or customers**, single-version, PDF export, approval auto-creates customer + job |
| `site_visits` | Visit scheduling, measurements, image uploads — used to verify plan-based estimates after approval |
| `jobs` | Job lifecycle, **price variations** (with reason + manager approval), status history, team assignment |
| `installations` | Installation scheduling, teams, completion photos, customer signoff |
| `finance` | Invoices, multiple payments (deposit / partial / paid), balance tracking, PDF export |
| `reports` | Sales · Jobs · Finance · **Staff Activity** (per-user accountability) reports |
| `company_settings` | Company profile, branding, currency |

Cross-cutting:
- `core/` — shared `AuditModel` (created_by / updated_by / timestamps), `RoleRequiredMixin`, `AuditMixin`, plus shared PDF utilities.
- **Django signals** auto-write audit entries on every save/delete to any AuditModel-derived model, plus auth signals for logins.
- **Quote approval signal** automatically creates the linked Job.
- **Lead-quote approval** automatically converts the lead into a Customer in one click.
- **Webhook endpoint** (`/api/leads/webhook/`) accepts inbound leads from Meta Lead Ads / Zapier / Make.com / WhatsApp Business so leads can land in the system without ever passing through a salesperson's phone.

---

## 🛡️ Accountability features

| Feature | What it gives you |
|---|---|
| Audit log on every model | Field-level diffs (`old → new`) on every update; full snapshots on create/delete |
| Login / failed-login tracking | Captures username, IP and timestamp of every authentication attempt |
| Lead **proof attachments** | Every lead requires WhatsApp/Facebook screenshots or house-plan files; sales can't fabricate or hide enquiries |
| Lead `source_url` | The actual link to the original conversation (`wa.me/...`, `m.me/...`) is stored on the lead |
| Public webhook | Inbound leads from Facebook ads / WhatsApp Business / website forms land directly in the system, bypassing salesperson hands |
| Activity timeline on every record | The detail page of every lead, quote, job and invoice shows who touched it and when |
| **Staff Activity report** | Manager-only report summarising per-user counts of leads created, quotes sent, approvals, payments logged, deletes, logins — for the period |
| Variation approval | Job price changes after the original quote require a manager to approve before they take effect |

---

## 🚀 Quick start

```bash
# 1. clone & enter
git clone <repo> && cd makuwetafadzwa

# 2. virtual env + deps
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. environment (optional — leave USE_SQLITE=True for dev)
cp .env.example .env

# 4. migrate
python manage.py makemigrations
python manage.py migrate

# 5. seed demo data
python manage.py seed_data

# 6. run
python manage.py runserver
```

Visit http://127.0.0.1:8000/. Sign in as `admin / admin12345`.

### Demo accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin12345` | Admin (superuser) |
| `sarah` | `password123` | Sales |
| `blessing` | `password123` | Estimator |
| `kuda` | `password123` | Installer |
| `rumbi` | `password123` | Storekeeper |
| `tendai` | `password123` | Finance |
| `nigel` | `password123` | Manager |

---

## 🌐 Lead webhook (Facebook / WhatsApp / Zapier integration)

Set an API key in your environment:

```bash
export ALUFLOW_LEAD_API_KEY=some-long-random-secret
```

Then point any source that can send a webhook (Zapier, Make.com, n8n, your website's contact form, Meta Lead Ads via Zapier) at:

```
POST https://your-aluflow-host/api/leads/webhook/
X-Api-Key: <your secret>
Content-Type: application/json

{
  "full_name": "Lerato Banda",
  "phone": "+263 71 222 9999",
  "email": "lerato@example.com",
  "source": "facebook",          // whatsapp | facebook | instagram | website | walk_in | referral | phone | email | other
  "product_interest": "folding_doors",
  "notes": "Saw your folding doors ad",
  "source_url": "https://m.me/aluflowzw/t/abc123"
}
```

Successful posts return `{"ok": true, "id": <lead_id>, "lead_code": "LEAD-00012", "status": "new"}` and create an audit entry tagged `Created via webhook`. Failed authentication is logged as `failed login` so brute-forcing the endpoint is detectable.

The lead lands directly in the **Leads** list under status **NEW**, ready for a salesperson to attach proof and prepare a quote — but its provenance (Facebook ad, WhatsApp Business message, etc.) is captured automatically and cannot be tampered with.

---

## 🗄️ Switching to PostgreSQL

Edit `.env`:

```dotenv
USE_SQLITE=False
DB_NAME=aluflow_crm
DB_USER=aluflow
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
```

Then `createdb aluflow_crm && python manage.py migrate`.

---

## 🧱 Project layout

```
.
├── aluflow/             # Django project (settings, urls, wsgi)
├── accounts/            # custom user, roles, auth
├── audit/               # audit log + lead webhook
├── company_settings/    # company profile + settings hub
├── core/                # shared abstract models + mixins + pdf base
├── customers/           # customers & projects
├── dashboard/           # KPI dashboard
├── finance/             # invoices & payments
├── installations/       # installations & teams
├── jobs/                # jobs / orders / variations
├── leads/               # leads + attachments + activities
├── quotations/          # quotations + PDF
├── reports/             # sales / jobs / finance / staff-activity reports
├── site_visits/         # site visits & measurements
├── templates/           # Tailwind-based templates
├── manage.py
└── requirements.txt
```

---

## 🧪 Useful commands

```bash
python manage.py createsuperuser
python manage.py seed_data           # idempotent — safe to re-run
python manage.py shell
python manage.py collectstatic       # for production
```

---

## 🗒️ Notes for production

- Replace the `SECRET_KEY`, set `DEBUG=False`, configure `ALLOWED_HOSTS`.
- Switch to PostgreSQL.
- Set `ALUFLOW_LEAD_API_KEY` to a long random secret.
- Serve static via WhiteNoise (already configured) or a CDN.
- Put HTTPS in front (e.g. nginx) and run a real WSGI process (`gunicorn aluflow.wsgi`).
- Configure email backend for sending quotations/invoices.

---

Internal tool — adapt freely.
