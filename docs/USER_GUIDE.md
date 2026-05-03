# Aluflow Sales & Operations CRM — User Training Guide

**Version 1.0 · For staff at all levels**

This guide walks you through every role, screen and workflow in the Aluflow CRM. It is written for sales reps, estimators, installers, storekeepers, finance officers, managers and admins. No technical background required.

---

## Table of contents

1. [About the system](#1-about-the-system)
2. [Getting started](#2-getting-started)
3. [Understanding your role](#3-understanding-your-role)
4. [Navigating the interface](#4-navigating-the-interface)
5. [The complete sales-to-installation workflow](#5-the-complete-sales-to-installation-workflow)
6. [Module-by-module guide](#6-module-by-module-guide)
   - [6.1 Leads](#61-leads)
   - [6.2 Customers & Projects](#62-customers--projects)
   - [6.3 Site Visits & Measurements](#63-site-visits--measurements)
   - [6.4 Quotations](#64-quotations)
   - [6.5 Jobs / Orders](#65-jobs--orders)
   - [6.6 Inventory](#66-inventory)
   - [6.7 Suppliers & Purchase Orders](#67-suppliers--purchase-orders)
   - [6.8 Installations](#68-installations)
   - [6.9 Invoices & Payments](#69-invoices--payments)
   - [6.10 Reports](#610-reports)
   - [6.11 Settings](#611-settings)
7. [End-to-end worked example](#7-end-to-end-worked-example)
8. [Tips & best practices](#8-tips--best-practices)
9. [Troubleshooting & FAQ](#9-troubleshooting--faq)
10. [Glossary](#10-glossary)

---

## 1. About the system

**Aluflow CRM** is a single workplace that follows every customer enquiry from the very first WhatsApp message all the way through to the final payment after installation. It replaces scattered notebooks, WhatsApp screenshots, Excel quotes, paper receipts and printed worksheets.

The big idea is one continuous record:

```
Lead  →  Customer  →  Site Visit  →  Measurement  →  Quotation  →  Approval
                                                                      ↓
After-Sales  ←  Payment  ←  Invoice  ←  Installation  ←  Fabrication  ←  Job
```

Every step is linked to the previous one. When you open a job, you can see the quotation that created it; when you open the invoice, you can see the job; when you open the customer, you can see every project, quotation, invoice and visit at once.

---

## 2. Getting started

### 2.1 Logging in

1. Open your browser and go to your Aluflow CRM URL (your administrator will share this — typically `https://crm.aluflow.example` or `http://<office-ip>:8000` on the LAN).
2. Type your **username** and **password** on the sign-in screen.
3. Click **Sign in**. You'll land on the **Dashboard**.

> **First time?** Your administrator gave you a temporary password. Change it immediately by clicking your name in the bottom-left corner → **My Profile**.

### 2.2 Updating your profile

- Click your name/initials in the **bottom-left** of the sidebar.
- Update first/last name, phone, email, job title and avatar.
- Click **Save profile**.

### 2.3 Signing out

Click **Sign out** in the **top-right** corner of any page.

> Always sign out on shared computers — your account is your fingerprint on every record you touch.

---

## 3. Understanding your role

Every user is given exactly one role. Your role decides which buttons and menus you see.

| Role | What you typically do | Key screens you live on |
|---|---|---|
| **Admin** | System owner. Manages users, settings and has full access. | Settings, Users, every module |
| **Manager** | Operational oversight. Approves big quotes, assigns staff, runs reports. | Dashboard, Reports, Jobs |
| **Sales** | Captures leads, quotes customers, follows up, closes deals. | Leads, Customers, Quotations |
| **Estimator** | Visits sites, takes measurements, prepares accurate quote line items. | Site Visits, Quotations, Inventory |
| **Installer** | Performs on-site fitting; updates installation progress. | Installations, Jobs |
| **Storekeeper** | Receives stock, issues materials, tracks low stock, raises purchase orders. | Inventory, Suppliers, Purchase Orders |
| **Finance** | Issues invoices, records payments, chases outstanding balances. | Invoices, Payments, Finance Report |

> **Don't see a button described in this guide?** Your role probably doesn't have permission for it. Ask your manager.

---

## 4. Navigating the interface

The screen has three areas:

```
┌─────────────────────────────────────────────────────────────┐
│ Sidebar │ Top bar (page title · actions · sign out)         │
│         ├───────────────────────────────────────────────────┤
│  📊 Dash│                                                   │
│  🎯 Leads                  Main content area                │
│  👤 Cust│                  (lists, forms, dashboards)       │
│  📐 Site│                                                   │
│  📄 Quot│                                                   │
│  🔧 Jobs│                                                   │
│   ...   │                                                   │
└─────────────────────────────────────────────────────────────┘
```

### 4.1 The sidebar (left)

Grouped into four sections:
- **Sales** — Leads, Customers, Site Visits, Quotations
- **Operations** — Jobs, Installations, Inventory, Suppliers, Purchase Orders
- **Finance** — Invoices, Payments
- **Insights** — Reports
- **Admin** (only Admins/Managers) — Settings, Users

### 4.2 The top bar

- The **page title** tells you where you are.
- The **action buttons** (right side) are the things you can do here — usually `+ New …`, `Edit`, or status-changing buttons.
- **Sign out** is always at the far right.

### 4.3 Lists

Almost every module starts with a **list page**. Lists support:

- **Search** (`q=` parameter or the search box) — type a name, phone, SKU.
- **Filters** — drop-downs at the top (status, source, category…).
- **Click any row** to open the detail page.
- **Pagination** at the bottom for long lists.

### 4.4 Detail pages

Detail pages always follow the same pattern:

- **Top:** identifying info + action buttons (Edit, Delete, Status changes).
- **Middle:** key facts in a grid.
- **Right column:** quick actions and related links.
- **Below:** related records (line items, history, files, photos).

### 4.5 Forms

- Required fields are marked with a red `*`.
- Date and time fields use your browser's native date picker — click and choose.
- The **Save** button is always at the bottom-left of the form.
- **Cancel** beside it returns to the previous list without saving.

---

## 5. The complete sales-to-installation workflow

Below is the journey of a single customer enquiry. Every stage links to the next, and the system enforces the order.

### Stage 1 — Lead (Sales)

A WhatsApp message arrives: *"Hi, I'm interested in folding doors for my lounge."*

You log into Aluflow and click **Leads → + New Lead**, fill in name, phone, source = WhatsApp, product interest = Folding Doors. Status starts as **New**.

### Stage 2 — Qualify & schedule (Sales / Estimator)

You phone the lead, decide it's serious, change status to **Contacted** and book a site visit. From the lead's page click **Convert to Customer**, which creates a Customer record (and an empty Project for them).

### Stage 3 — Site visit (Estimator)

In **Site Visits → + Schedule Visit**, choose the customer and project, set the date, and assign the estimator. On the day, the estimator opens the visit and clicks **Measurements**, recording every opening (location, width × height in mm, glass type, frame colour, quantity). They upload site photos. Click **Mark Completed**.

### Stage 4 — Quotation (Sales / Estimator)

In **Quotations → + New Quotation**, link to the customer, project and site visit. Add line items (one per opening), set discount % and VAT % (defaults to 15%). The system calculates subtotal, VAT and total automatically. Click **Save → Items** to add lines, then back on the detail page click **Mark as Sent**, then download the PDF and email/WhatsApp it to the customer.

### Stage 5 — Approval (Sales)

Customer says yes. You click **Approve & Create Job**. A Job is automatically created, linked to this quotation, in status **Confirmed**.

### Stage 6 — Materials & fabrication (Storekeeper / Manager)

The Job's **Bill of Materials (BOM)** is built — list every aluminium profile, glass panel and accessory needed. When materials are committed (Storekeeper clicks **Deduct Materials**), stock is automatically reduced. Status moves through **Awaiting Materials → Fabrication → Ready for Installation**.

### Stage 7 — Installation (Installer)

From the Job, click **Schedule Installation**. Pick the date, team and lead installer. The installation team go on-site, do the fitting, upload completion photos and click **Mark Complete**. The Job auto-moves to **Installed**.

### Stage 8 — Invoice (Finance)

From the Job, click **+ Invoice**. The system pre-fills customer, job and contract value. Add line items if needed (e.g. 50% deposit / 50% balance), click **Issue Invoice**.

### Stage 9 — Payment (Finance)

When money arrives (bank transfer, EcoCash, cash), open the invoice and use **Record Payment** on the right. The invoice's balance updates automatically. When the balance hits zero, status flips to **Paid**.

### Stage 10 — After-sales (Manager / Sales)

The manager moves the Job to **Completed**. Future warranty visits can be logged as new Site Visits against the same customer.

---

## 6. Module-by-module guide

### 6.1 Leads

**Where:** Sidebar → 🎯 Leads · **Who uses it:** Sales, Manager

#### What it tracks

Every potential customer who has shown interest but hasn't bought yet.

#### List page

| Column | Meaning |
|---|---|
| Lead | Full name and email |
| Phone | Primary contact number |
| Source | How they found us (WhatsApp, Facebook, Walk-in, Referral, Website, Phone, Email) |
| Interest | Product category they want |
| Status | New / Contacted / Qualified / Quoted / Won / Lost |
| Assigned | Sales rep responsible |
| Created | When the lead was logged |

**Filters at the top:** search box (matches name/phone/email/company), status drop-down, source drop-down.

#### Creating a lead — step-by-step

1. Click **+ New Lead** (top right).
2. **Full name** — required.
3. **Phone** — required (it's how we follow up).
4. **Email** — optional but useful for sending quotes.
5. **Company** — fill in if it's a business enquiry.
6. **Source** — choose the channel they came through.
7. **Product interest** — what they're asking about.
8. **Status** — leave as **New** unless you've already spoken to them.
9. **Estimated value** — your gut feel, in $. Helps with reporting.
10. **Assigned to** — the salesperson responsible.
11. **Next follow-up** — date you'll call them back.
12. **Notes** — paste the WhatsApp message, anything they said, special requirements.
13. Click **Save lead**.

#### Working a lead

Open any lead. You'll see:

- **Top right buttons:** **Edit** / **Convert to Customer** (only if not yet converted).
- **Activities:** every call, email, WhatsApp or note you log. Use the small form on the lead detail page to add a new activity (drop-down + text + Log).
- **Right sidebar:** shows whether the lead is still open or has already been converted.

#### Status flow

```
New  →  Contacted  →  Qualified  →  Quoted  →  Won  ✅
                                            ↘  Lost ❌
```

You move the status by editing the lead and changing the **Status** field.

#### Converting to customer

When the lead is serious:

1. Open the lead.
2. Click **Convert to Customer** (top right or right column).
3. Optionally tick **Create initial project** and give it a name.
4. Click **Convert**. The system:
   - Creates a Customer record using the lead's contact details.
   - Optionally creates a first Project for them.
   - Sets the lead's status to **Won**.
   - Links the lead to the new customer (you'll see a green banner on the lead from now on).

> **Don't convert too early.** A lead becomes a customer when they've agreed to engage seriously — usually after the site visit or once they accept the quote.

---

### 6.2 Customers & Projects

**Where:** Sidebar → 👤 Customers · **Who uses it:** Sales, Estimator, Manager, Finance

#### Customers

A Customer is anyone who has bought from us or is in the process of buying.

**To add a customer manually** (e.g. a walk-in who didn't go through a lead):

1. Customers → **+ New Customer**.
2. Choose **Customer type:** Individual / Company / Government / Property Developer.
3. Fill in **Full name** and (if a company) **Company name**.
4. Add phone, email, address, city, country.
5. Optional: tax number for VAT-invoiced customers.
6. **Save**.

The system auto-generates a customer code like `CUST-00007`.

#### Customer detail page

Three areas:

- **Contact details** — everything we know about them.
- **Projects** — list of projects under this customer (residential renovation, commercial fit-out, etc.).
- **Quotations** — every quote we've issued them.
- **Quick Actions** (right column) — schedule a site visit, create a quote, add a project, delete the customer.

#### Projects

A Project is a single physical site or contract. One customer can have many projects (e.g. a property developer with multiple buildings).

**To add a project:**

1. From the customer page, click **+ Project**.
2. **Name** — descriptive (e.g. "Lounge folding-door upgrade").
3. **Description** — context for the team.
4. **Site address & city** — where the work happens.
5. **Expected start / completion** — your best estimate.
6. **Status** — Planning / Active / On Hold / Completed / Cancelled.
7. **Save**.

> Always link site visits and quotations to the project, not just the customer. It keeps multi-site customers organised.

---

### 6.3 Site Visits & Measurements

**Where:** Sidebar → 📐 Site Visits · **Who uses it:** Estimator, Sales, Installer

#### Why we use it

A site visit is a formal record of an estimator going to the customer's premises. It captures:

- The exact dimensions of every opening (in millimetres).
- Photos of the site as it currently is.
- Any installation challenges (access, height, existing fittings).

This becomes the source of truth for the quotation.

#### Scheduling a visit

1. Site Visits → **+ Schedule Visit**.
2. **Customer** — pick from drop-down.
3. **Project** — pick the relevant project (optional but recommended).
4. **Scheduled date** — date and time (use the date-time picker).
5. **Site address** — pre-fill from project if known.
6. **Contact person on site / phone** — who lets you in.
7. **Assigned to** — estimator.
8. **Status** — leave as **Scheduled**.
9. **Notes** — anything the estimator should know in advance.
10. **Save visit**.

#### Recording measurements

Open the visit. Click **📐 Measurements** (top right).

You'll see a table where each row is one opening:

| Field | Tip |
|---|---|
| Location | "Master bedroom window", "Lounge sliding door" — be specific |
| Product type | Casement window, Sliding door, Folding door, Shower door, Shopfront, Balustrade, etc. |
| Width (mm) | Internal frame width |
| Height (mm) | Internal frame height |
| Quantity | How many identical units |
| Glass type | "6mm clear", "8mm tempered", "10mm laminated" |
| Frame colour | "Silver", "Charcoal", "Bronze" |
| Notes | Anything unusual |

- Click in the bottom row to add another measurement.
- Tick **Delete** on any row you want removed when you save.
- Click **Save measurements**.

> **Always measure in millimetres.** The system uses mm everywhere — quotations, jobs and PDFs.

#### Uploading site photos

On the visit detail page, scroll to **Photos**:

1. Click the file picker, select a photo.
2. Add an optional caption (e.g. "view from inside lounge").
3. Click **Upload**. The photo appears in the gallery.

Take **at least one photo per opening** plus a wide shot of the room.

#### Marking the visit complete

When you leave the site and have entered everything, click **Mark Completed** (top right). The visit's status becomes **Completed** and `completed_at` is stamped to the current time.

---

### 6.4 Quotations

**Where:** Sidebar → 📄 Quotations · **Who uses it:** Sales, Estimator, Manager

#### Lifecycle

```
Draft  →  Sent  →  Approved  → (Job auto-created)
                ↘  Rejected
                ↘  Expired
```

Only **Draft** and **Sent** quotations can be edited. Once approved or rejected they're locked — but you can always **revise** a quotation, which creates a new version.

#### Creating a quotation

1. Quotations → **+ New Quotation**.
2. **Customer** — required.
3. **Project** — link if available.
4. **Site visit** — link the visit you used to take measurements.
5. **Issue date** — defaults to today.
6. **Valid until** — recommended 14 days from issue.
7. **Discount %** — leave 0 unless approved.
8. **VAT %** — defaults to your company's setting (e.g. 15%).
9. **Notes** — anything the customer should know.
10. **Terms** — pre-filled with standard terms (deposit, lead time). Edit if needed.
11. Click **Save & continue**. You'll be taken to the items screen.

#### Adding line items

On the items page, each row is one billable item:

| Field | Tip |
|---|---|
| Product | (optional) link to a product from inventory — auto-fills price |
| Description | What appears on the customer's PDF — be clear |
| W (mm) / H (mm) | Optional, but highly recommended for door/window items |
| Qty | How many |
| Unit price | Price each |
| Order | Sort order on the PDF |

- Add as many rows as you need.
- Tick **Delete** on rows to remove.
- Click **Save items**.

The detail page now shows the full breakdown:

```
Subtotal:                $7,150.00
Discount (5%):            -$357.50
VAT (15%):               $1,018.88
─────────────────────────────────
Grand total:             $7,811.38
```

#### Sending the quote

1. From the quote detail page, click **Mark as Sent** (right column).
2. Click **Download PDF** — opens a professionally formatted PDF.
3. Email or WhatsApp the PDF to the customer.

#### Approval / rejection

When the customer responds:

- **They accept** → click **Approve & Create Job**. The system:
  - Sets status to **Approved**.
  - Stamps `approved_at`.
  - Auto-creates a Job linked to this quotation, with the contract value pre-populated.
  - Redirects you to confirm.
- **They reject** → click **Reject**. Optionally type a reason (price, lead time, competitor). This is invaluable feedback for sales.

#### Versions

Customer wants changes? Click **+ New version** on the quote detail page. The system clones the current quote into a new draft (e.g. v2), preserving all line items. Edit the new version, send it. The original v1 stays in the system for history. The detail page shows all versions in the right column.

> Always issue a new version rather than editing a quote that's already been sent. It keeps a clear audit trail of what was promised when.

---

### 6.5 Jobs / Orders

**Where:** Sidebar → 🔧 Jobs / Orders · **Who uses it:** Manager, Estimator, Storekeeper, Installer

#### What is a Job?

A Job is the operational record of producing and installing what was sold. Most Jobs are auto-created when a quote is approved, but you can also create them manually for ad-hoc work.

#### Status flow

```
Confirmed
   ↓
Awaiting Materials
   ↓
Fabrication
   ↓
Ready for Installation
   ↓
Installed
   ↓
Completed
```

Plus a **Cancelled** branch for jobs that fall through.

#### Job detail page

You'll see:

- Customer, project, linked quotation
- Project manager and assigned team
- Start date, target completion, contract value
- Whether materials have been deducted
- **Bill of Materials** — what's needed for fabrication
- Linked **Installations** and **Invoices**
- **Status history** — every change with who, when and any note

#### Setting up the Bill of Materials (BOM)

Click **📦 BOM** on the job detail page. For each row:

| Field | Meaning |
|---|---|
| Product | The inventory item (aluminium profile, glass, hardware) |
| Required | Quantity needed |
| Used | Quantity actually committed (auto-fills when you click Deduct Materials) |
| Notes | Any specifics (cut sizes, batch numbers) |

Save the BOM. Now the Storekeeper knows exactly what to issue.

#### Deducting materials

When fabrication starts, the storekeeper clicks **Deduct Materials** on the job page. The system:

1. Checks the outstanding quantity for each BOM line.
2. Reduces the corresponding product's stock by that amount.
3. Logs a `StockMovement` record with reason **Job Consumption** and reference = job number.
4. Sets the BOM line's `quantity_used` = `quantity_required`.
5. Marks the job's `materials_deducted` flag = True.

If you click **Deduct Materials** twice, nothing extra happens — the system is idempotent.

#### Updating job status

In the right column there's a **Status** card with a drop-down and a note field. Change the status, optionally write a comment ("Glass arrived from supplier"), and click **Update status**. A line is added to the **Status history** below.

When you set status to **Completed**, the system stamps `completed_at` to today.

#### Assigning the team

Edit the job and use:
- **Project manager** — single user accountable for delivery.
- **Assigned team** — multi-select of users who'll work on it.

These users will see this job under their workload (future feature).

---

### 6.6 Inventory

**Where:** Sidebar → 📦 Inventory · **Who uses it:** Storekeeper, Estimator, Manager

#### Products

Every aluminium profile, glass panel, hardware accessory and even labour service is a **Product** with a unique SKU.

**Kinds:**
- **Raw Material** — aluminium, glass, gaskets (consumed during jobs).
- **Finished Product** — pre-made stock items.
- **Service / Labour** — installation labour, callout fees (no stock movements).

#### Adding a product

1. Inventory → **+ New Product**.
2. **SKU** — short unique code (e.g. `ALU-FD-100`).
3. **Name** — full product name.
4. **Kind** — material / finished / service.
5. **Category** — optional but recommended (Aluminium Profiles, Glass Panels, Hardware, Services).
6. **Unit** — Each / Meter / Square Meter / Kg / Liter / Sheet / Set.
7. **Description** — specs, manufacturer info.
8. **Cost price** — what we pay.
9. **Selling price** — what we charge.
10. **Stock quantity** — current quantity on hand.
11. **Reorder level** — minimum threshold; below this, the product appears in low-stock alerts.
12. **Preferred supplier** — auto-populates on purchase orders.
13. **Save**.

#### Product detail & stock adjustment

On any product page you can:

- See current stock, reorder level, and the running list of stock movements.
- Adjust stock manually — useful for opening stock counts, returns, damage:
  1. Right column → **Adjust Stock** form.
  2. **Change** — positive number to add, negative to remove.
  3. **Reason** — Adjustment / Opening Stock / Return.
  4. **Reference** — optional (e.g. "stock count Q1 2026").
  5. Click **Apply**.

Every adjustment creates a `StockMovement` record so we can audit later.

#### Low-stock alerts

On the Dashboard, the **Low-Stock Items** card lists every active product where `stock_quantity ≤ reorder_level`. You can also filter the product list by ticking **Low stock only** at the top of the page.

#### Categories

Inventory → **Categories** (top right). Use these to group products on reports. Add, edit or delete from a single page.

---

### 6.7 Suppliers & Purchase Orders

**Where:** Sidebar → 🚚 Suppliers / 🧾 Purchase Orders · **Who uses it:** Storekeeper, Manager, Finance

#### Suppliers

Add every vendor we buy from. Fields: name, contact person, phone, email, address, payment terms.

Suppliers can be set as **preferred supplier** on each product so future POs auto-populate.

#### Creating a Purchase Order

1. Purchase Orders → **+ New PO**.
2. **Supplier** — pick from drop-down.
3. **Order date** — today.
4. **Expected date** — when the supplier promised delivery.
5. **Status** — leave as **Draft**.
6. **Notes** — internal use.
7. Click **Save** — you'll go to the **Lines** screen.

#### Adding PO lines

For each row:
- **Product** — from inventory.
- **Quantity** — how many you're ordering.
- **Unit cost** — what the supplier is charging.
- **Received quantity** — leave blank (filled when stock arrives).

Save lines. You'll see the PO total auto-calculated.

#### Receiving stock

When the goods arrive:

1. Open the PO.
2. Click **Receive Stock** (top right).
3. The system increases each line's product stock by the outstanding quantity (= `quantity` − `received_quantity`).
4. Each adjustment is logged as a `StockMovement` with reason **Purchase Received** and reference = PO number.
5. The PO status changes to **Received**.

If you only got a partial delivery, instead manually edit each line's **Received quantity** and the rest will be picked up next time you click **Receive Stock**.

---

### 6.8 Installations

**Where:** Sidebar → 🏗️ Installations · **Who uses it:** Installer (lead), Manager

#### Scheduling an installation

You can start from the Job (recommended) or from the Installations list:

- **From the Job:** click **Schedule Installation** at the top.
- **From the list:** Installations → **+ Schedule**, then choose the Job.

Fill in:
- **Scheduled date** (date + time).
- **Site address** — pre-fills from job's customer address.
- **Team** — pick from defined Installation Teams.
- **Lead installer** — accountable person.
- **Notes** — access instructions, parking, on-site contact.

#### On the day of installation

Open the installation on a phone or tablet. The team should:

1. Take **before** photos (use the upload form).
2. Do the work.
3. Take **after** photos and tick **Completion photo** when uploading.
4. Have the customer sign off — fill in **Customer signoff name** and tick the box.
5. Add **Completion notes** describing anything noteworthy.
6. Click **Mark Complete**.

When marked complete, the linked Job auto-moves to status **Installed**.

#### Installation Teams

Settings → **Installation Teams** (or Installations → **Teams** at the top).

A team has:
- A name (e.g. "Team A — Harare").
- A leader (one user).
- Members (multiple users).

Use teams to track who actually did the install — helps with payroll, performance reviews and warranty work.

---

### 6.9 Invoices & Payments

**Where:** Sidebar → 💵 Invoices / 💳 Payments · **Who uses it:** Finance, Manager

#### Issuing an invoice

Best practice: create the invoice from the Job page (the system pre-fills everything).

1. Open the relevant Job.
2. Click **+ Invoice** (top right).
3. The form is pre-populated with customer, job and contract value.
4. Fill in:
   - **Issue date** — today.
   - **Due date** — typically 30 days.
   - **Tax %** — defaults to company VAT.
   - **Discount amount** — flat $ amount.
   - **Deposit required** — typically 50% of total.
   - **Notes** — banking details, payment instructions.
5. Click **Save & continue**.

#### Invoice lines

On the Lines screen, add at least one line per billable item:

- **Description** — what the customer is paying for.
- **Quantity** & **Unit price**.

Common patterns:
- Two lines: "50% Deposit" + "Balance on completion".
- One line per item from the quotation.
- One line for goods + one for installation labour.

Save lines. The invoice subtotal is auto-calculated from the lines.

#### Issuing the invoice

On the detail page, click **Issue Invoice**. The status moves from **Draft** to **Issued**. The invoice now appears on the customer's statement.

#### Recording payments

When money arrives:

1. Open the invoice.
2. Right column → **Record payment** form.
3. **Date** — when the payment was made.
4. **Amount** — exact amount received.
5. **Method** — Cash / Bank Transfer / EcoCash / Card / Cheque / Other.
6. **Reference** — bank ref, EcoCash ref, cheque number.
7. **Receipt** — optional file upload (PDF, photo).
8. **Notes** — any context.
9. **Is deposit?** — tick if it's the deposit (helps reporting).
10. Click **Save payment**.

The system:
- Adds the payment to the invoice's payment list.
- Recalculates **Paid amount** and **Balance**.
- Updates the invoice status:
  - All paid → **Paid**.
  - Some paid, balance > 0 → **Partially Paid**.
  - Nothing paid → unchanged.

#### Outstanding payments

The Invoices list shows total outstanding at the top. The Dashboard also surfaces this number prominently. Use the Finance Report (next section) for detailed analysis.

---

### 6.10 Reports

**Where:** Sidebar → 📈 Reports · **Who uses it:** Manager, Finance, Admin

The Reports hub gives you four pre-built reports, each with a date filter.

#### Sales report

- Total leads created in period.
- Leads won vs lost.
- Quotations issued and approved.
- Job value approved.
- Leads by source (WhatsApp vs Facebook vs Walk-in…).

Use this to evaluate marketing channels and individual sales performance.

#### Jobs report

- Open vs completed jobs.
- Total contract value.
- Breakdown by status.

Use this for production-floor planning.

#### Finance report

- Payments collected in period.
- Invoices issued and total invoiced value.
- Outstanding balance across all invoices.
- Payments by method (which channels customers prefer).

#### Inventory report

- Total SKUs.
- Low-stock items (urgent action list).
- Total stock value at cost.
- Recent stock movements.

#### Date filters

Most reports have **From** and **To** date fields at the top. Pick a range and click **Apply**. Default is the last 30 days.

---

### 6.11 Settings

**Where:** Sidebar → ⚙️ Settings (Admin / Manager only)

The Settings hub has four cards:

#### Company Profile

The company info that appears on every PDF (quote, invoice). Set:
- Name, tagline, logo.
- Email, phone, address, city, country.
- Tax number.
- Bank details (printed on invoices).
- Default VAT % (defaults all new quotes to this rate).
- Currency symbol and code.

> **Update this first** when you set up the system. The currency symbol shows on every page that displays money.

#### Product Categories

Add the categories your business uses. Recommended: Aluminium Profiles, Glass Panels, Hardware & Accessories, Services. You can add more (e.g. Tools, Consumables).

#### Users & Roles

Add staff accounts:
1. Settings → **Users** or sidebar → 👥 **Users**.
2. **+ New User**.
3. Pick a username (lowercase, no spaces).
4. Fill in name, email, phone, role, job title.
5. Set a temporary password and ask the user to change it on first login.
6. **Save user**.

Edit any user to change their role, deactivate them (untick **Is active**) or upload an avatar.

#### Installation Teams

(Already covered in §6.8.) Define your installer crews here.

---

## 7. End-to-end worked example

Let's walk through a complete real scenario.

### Day 1 — Lead

Sarah (Sales) gets a WhatsApp from **Brian Phiri**: *"Hi, I need a sliding door for my balcony. Can you quote me?"*

Sarah:
1. Logs into Aluflow.
2. Leads → **+ New Lead**.
3. Fills in:
   - Full name: *Brian Phiri*
   - Phone: *+263 77 444 1212*
   - Source: *WhatsApp*
   - Product interest: *Sliding Doors*
   - Status: *New*
   - Assigned to: *Sarah*
   - Estimated value: *$2,000*
   - Notes: *Wants frameless aluminium for 1st-floor balcony*
4. Saves.

Sarah calls Brian, agrees a site visit. Edits the lead → status **Contacted**, next follow-up date set.

### Day 3 — Site visit

Brian agrees a price band. Sarah converts the lead:

1. Opens the lead → **Convert to Customer**.
2. Tick **Create initial project**, name it *"Phiri Balcony Sliding Door"*.
3. Convert. New customer **CUST-00008** is created.

Sarah schedules a site visit:
1. Site Visits → **+ Schedule Visit**.
2. Customer: *Brian Phiri*. Project: *Phiri Balcony Sliding Door*.
3. Date: *Day 4, 14:00*. Assigned to: *Blessing* (estimator).
4. Saves.

### Day 4 — Site visit

Blessing arrives at Brian's flat. From his phone:
1. Opens the visit.
2. Clicks **📐 Measurements**, adds one row:
   - Location: *Balcony*. Product type: *Sliding Door*. Width: *2400*. Height: *2200*. Quantity: *1*. Glass: *8mm tempered*. Frame: *charcoal*.
3. Saves.
4. Uploads two photos (existing balcony + the wall).
5. Notes: *Tight fit, will need angle grinder*.
6. Clicks **Mark Completed**.

### Day 5 — Quotation

Sarah builds the quote:
1. Quotations → **+ New Quotation**. Customer: *Brian Phiri*. Project: *Phiri Balcony Sliding Door*. Site visit: linked. VAT: 15%. Saves.
2. Items page → adds three rows:
   - *8mm Tempered Glass Sliding Panels (2400×2200)* — qty 1 @ $1,200
   - *Sliding Door Track System* — qty 2 @ $180
   - *Standard Installation* — qty 1 @ $200
3. Saves items. Total: *$1,560 + 15% VAT = $1,794*.
4. Back on detail page → **Mark as Sent** → **Download PDF** → WhatsApps the PDF to Brian.

### Day 8 — Approval

Brian replies: "Yes, let's do it." Sarah opens the quote → **Approve & Create Job**. Job **JOB-00009** is auto-created with contract value $1,794, linked to the quote.

### Day 9 — Materials

Rumbi (Storekeeper) opens the new job:
1. Clicks **📦 BOM** and adds:
   - *8mm Tempered Glass* — required: 5.28 sqm
   - *Sliding Door Track Profile* — required: 9 m
   - *EPDM Rubber Gasket* — required: 18 m
2. Saves.
3. Confirms stock is available, clicks **Deduct Materials**. Stock auto-decreases. Stock movement records created.
4. Updates job status to **Fabrication** with note *"Cutting started"*.

### Day 14 — Installation scheduled

Blessing books the installation:
1. From the job → **Schedule Installation**.
2. Date: Day 16, 09:00. Team: *Team A — Harare*. Lead installer: *Kuda*.
3. Saves.

### Day 16 — Install

Kuda arrives, fits the door, takes 4 photos (2 before, 2 after with door installed):
1. Opens the installation. Uploads each photo, tick **Completion photo** for the after shots.
2. Customer signoff: *Brian Phiri*. Tick the box. Completion notes: *"Customer happy, demo of sliding & locking done"*.
3. Clicks **Mark Complete**. Job auto-moves to **Installed**.

### Day 16 — Invoice

Tendai (Finance) creates the invoice:
1. From the job → **+ Invoice**. Customer and total pre-fill.
2. Issue date: today. Due date: +30 days. Deposit required: $897.
3. Saves and goes to lines:
   - *Phiri Balcony Sliding Door* — qty 1 @ $1,560.
4. Saves lines. Detail page now shows total $1,794, balance $1,794.
5. Clicks **Issue Invoice** → status becomes **Issued**.

### Day 17 — Deposit

Brian pays $900 deposit by EcoCash. Tendai:
1. Opens INV-00006. **Record payment**: amount $900, method EcoCash, reference *EC-XYZ123*, tick **Is deposit**, save.
2. Invoice now shows: Paid $900, Balance $894, Status **Partially Paid**.

### Day 23 — Final payment

Brian pays balance by bank transfer. Tendai records $894. Invoice status flips to **Paid**.

### Day 24 — Job complete

Nigel (Manager) opens the job → updates status to **Completed** with note *"All paid, customer happy"*.

The full lifecycle — from WhatsApp message to closed job — is now in the system, traceable in seconds. The dashboard shows the job in completed metrics, the customer file holds the entire history, and the finance report includes the $1,794 of revenue for the period.

---

## 8. Tips & best practices

### General

- **Log everything.** Even if a customer cancels, record it. Lost-lead reasons are gold for marketing.
- **Use real measurements.** Approximate measurements cost money in re-fabrication.
- **Take photos.** They protect us in disputes and help future installers.
- **Don't share accounts.** Every record is timestamped to a user — your accountability matters.

### Sales

- Convert leads to customers only when serious — keeps the lead pipeline clean.
- Always link a quotation to a site visit. It signals that we measured before pricing.
- Create a new version of a quote rather than editing one already sent.

### Estimator

- Take measurements in **mm**, not cm or inches.
- Add a note for any tricky access or unusual fittings.
- Upload at least one wide-angle photo per opening.

### Storekeeper

- Set realistic **reorder levels** so the dashboard surfaces problems before fabrication is blocked.
- Receive every PO promptly — late receipt = inaccurate stock = wrong dashboard.
- Use **Stock Adjustment** with **Reason: Adjustment** for stocktake corrections.

### Installer

- Tick **Completion photo** for after-shots — these are referenced in disputes and warranty claims.
- Always capture customer signoff name on the day of install.

### Finance

- Issue the invoice the same day the job is delivered — speeds up payment.
- Always attach the bank-confirmation receipt or EcoCash slip when recording a payment.
- Run the **Finance Report** weekly to spot ageing receivables.

### Manager

- Run the Sales Report monthly to evaluate channels and reps.
- Use **status updates with notes** when changing job status — they form an audit trail.
- Review low-stock alerts daily.

---

## 9. Troubleshooting & FAQ

### "I can't see the **Settings** menu."
You need the **Admin** or **Manager** role. Ask your administrator.

### "I clicked **Approve** on a quote but no job was created."
The system auto-creates a Job via a signal. If it didn't appear:
1. Refresh the page (job list).
2. Check whether you have permission.
3. If still missing, ask the admin to check the application logs.

### "Stock didn't decrease after I clicked **Deduct Materials**."
- Check the Job's BOM has rows. If the BOM is empty, nothing is deducted.
- Check the **Materials deducted** flag on the job — if already True, the system won't deduct again.

### "The PDF total doesn't match what I see on screen."
The PDF reads live data. If the figures differ:
1. Refresh the quote detail page.
2. Re-download the PDF.
3. If still wrong, check whether the items have changed since you last saved.

### "I deleted a customer by mistake."
Customer deletion is allowed only when there are no linked quotations, jobs or invoices. If you managed to delete one, ask the admin — they can restore it from the database backup.

### "I can't log in."
- Caps Lock?
- Username spelled exactly right?
- Password is case-sensitive.
- Three failed attempts → ask the admin to reset your password.

### "I see a 403 / Forbidden message."
You're trying to access a page above your role's permission. This is by design.

### "The page won't load / spinning forever."
1. Check your internet (CRM may be hosted off-site).
2. Refresh.
3. Try a different browser.
4. Tell the admin if persistent — they can check server status.

---

## 10. Glossary

| Term | Meaning |
|---|---|
| **Lead** | Potential customer; not yet committed to buy. |
| **Customer** | Person or organisation we have a relationship with. |
| **Project** | A single physical site or contract under a customer. |
| **Site visit** | A formal estimator visit to take measurements and assess. |
| **Measurement** | One opening on a site — width × height + product type. |
| **Quotation** | A formal price offer to a customer. |
| **Quote version** | A revised quotation that supersedes the previous one. |
| **Job (Order)** | The operational record of producing & installing what was sold. |
| **Bill of Materials (BOM)** | List of products and quantities needed for a job. |
| **PO (Purchase Order)** | A formal order placed with a supplier. |
| **Stock movement** | Any change in stock (purchase, job use, adjustment, return). |
| **Reorder level** | The threshold below which stock is "low" and needs replenishing. |
| **Installation** | The on-site fitting work for a job. |
| **Invoice** | A bill issued to a customer for goods/services. |
| **Payment** | Money received against an invoice. |
| **Deposit** | Up-front payment, typically 50% of contract. |
| **Balance** | Outstanding amount on an invoice = total − paid. |
| **VAT / Tax %** | Value-added tax applied to invoices and quotes. |
| **Audit log** | Every record stores who created it, who last updated it, and when. |
| **Role** | Determines which menus and buttons you see (Admin, Manager, Sales, Estimator, Installer, Storekeeper, Finance). |
| **Status** | The current stage of a record's lifecycle (e.g. Lead status, Job status). |
| **SKU** | Stock-keeping unit — unique code identifying a product. |

---

*End of guide. For technical setup or admin-only operations see **README.md** in the project root.*
