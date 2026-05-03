# Aluflow Sales & Operations CRM

A professional, modular Django CRM for a glass & aluminium business. It models the full operational lifecycle:

> **Lead → Customer → Site Visit → Measurement → Quotation → Approval → Job → Fabrication → Installation → Invoice → Payment → After-Sales**

Built with Django + PostgreSQL (SQLite for dev) + Django Templates + Tailwind CSS.

---

## 📦 Apps

| App | Purpose |
|---|---|
| `accounts` | Custom user model, roles (Admin / Manager / Sales / Estimator / Installer / Storekeeper / Finance), authentication, user CRUD |
| `dashboard` | KPI dashboard (leads, jobs, revenue, outstanding payments, low stock) |
| `leads` | Leads with source/status pipeline, activity log, lead → customer conversion |
| `customers` | Customers + multiple Projects per customer |
| `site_visits` | Site visit scheduling, measurements, image uploads |
| `quotations` | Multi-version quotations, line items, VAT/discount, PDF export, approval workflow |
| `jobs` | Job/order lifecycle, bill-of-materials, status history, team assignment |
| `inventory` | Products, categories, suppliers, stock movements, purchase orders, low-stock alerts |
| `installations` | Installation scheduling, teams, site/completion photos, customer signoff |
| `finance` | Invoices, multiple payments, deposits, balance tracking |
| `reports` | Sales / Jobs / Finance / Inventory reports with date filters |
| `company_settings` | Company profile, currency, VAT, branding |

Cross-cutting:
- `core/` — `AuditModel` (created_by / updated_by / timestamps), `RoleRequiredMixin`, `AuditMixin`.
- Django **signals** auto-create a Job when a quotation is approved.
- Stock auto-deducts when a job's materials are committed; auto-increases when a PO is received.

---

## 🚀 Quick start (local)

```bash
# 1. clone & enter
git clone <repo> && cd makuwetafadzwa

# 2. virtual env
python -m venv .venv
source .venv/bin/activate     # on Windows: .venv\Scripts\activate

# 3. dependencies
pip install -r requirements.txt

# 4. environment (optional)
cp .env.example .env
# leave USE_SQLITE=True for dev, or set False + Postgres credentials

# 5. migrate
python manage.py makemigrations
python manage.py migrate

# 6. seed demo data
python manage.py seed_data

# 7. run
python manage.py runserver
```

Visit http://127.0.0.1:8000/.

### Demo accounts (after `seed_data`)

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

Then create the database and run migrations:

```bash
createdb aluflow_crm
python manage.py migrate
```

---

## 🧱 Project layout

```
.
├── aluflow/                 # Django project (settings, urls, wsgi)
├── accounts/                # custom user, roles, auth
├── company_settings/        # Company profile + settings hub
├── core/                    # shared abstract models + mixins
├── customers/               # customers & projects
├── dashboard/               # KPI dashboard
├── finance/                 # invoices & payments
├── installations/           # installations & teams
├── inventory/               # products, suppliers, POs, stock
├── jobs/                    # jobs / orders / BOM
├── leads/                   # leads pipeline
├── quotations/              # quotations + PDF
├── reports/                 # reports
├── site_visits/             # site visits & measurements
├── templates/               # Tailwind-based templates
├── manage.py
└── requirements.txt
```

### Key features

- 🔐 **Role-based auth** — restricted CBVs via `RoleRequiredMixin`; `post_migrate` signal auto-creates Django Groups for each role.
- 📄 **PDF quotations** generated via ReportLab (`/quotations/<id>/pdf/`).
- 🔁 **Quotation versioning** — revise an existing quote into a new version, preserving history.
- 🔧 **Job auto-creation** on quote approval via `post_save` signal.
- 📦 **Stock auto-deduction** on job material commit; auto-increase on PO receive — both with `StockMovement` audit log.
- 💵 **Payment lifecycle** — partial / deposit payments, balance, status auto-refresh.
- 📊 **Dashboard** — total leads, conversion rate, active/completed jobs, monthly revenue, outstanding receivables, low-stock items.
- 📈 **Reports** — sales, jobs, finance, inventory with custom date ranges.
- 🧱 **Modular** — each domain is a Django app with its own models / forms / views / urls / admin / templates.
- 🪪 **Audit logging** on every significant model (`created_by`, `updated_by`, timestamps).

---

## 🎨 Styling

Uses **Tailwind via CDN** (no Node build step required) plus a custom `brand` colour palette tuned to indigo. Templates live in `templates/<app>/` with shared partials in `templates/partials/` (sidebar, topbar, page header, form card, empty state, pagination, confirm-delete).

If you want a production build (PurgeCSS optimised), swap the CDN script in `templates/base.html` for a compiled CSS file.

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
- Serve static via WhiteNoise (already configured) or a CDN.
- Add HTTPS (e.g. behind nginx) and a real WSGI runner (`gunicorn aluflow.wsgi`).
- Configure email backend for sending quotations/invoices.

---

## License

Internal company tool — adapt freely.
