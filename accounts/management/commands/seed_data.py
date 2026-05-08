"""Seed Aluflow CRM with realistic demo data — accountability-first version.

Creates:
  - Company profile
  - 7 demo users covering every role
  - Customers, projects, leads (some with attachments)
  - One lead with a quote that's been approved (auto-converts the lead)
  - Jobs, a site-larger variation, an installation, an invoice with a deposit payment
"""
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, User
from company_settings.models import CompanyProfile
from customers.models import Customer, CustomerType, Project
from finance.models import Invoice, InvoiceLine, InvoiceStatus, Payment, PaymentMethod
from installations.models import Installation, InstallationStatus, InstallationTeam
from jobs.models import Job, JobStatus, JobVariation
from leads.models import Lead, LeadSource, LeadStatus, ProductInterest
from quotations.models import Quotation, QuotationItem, QuotationStatus
from site_visits.models import (
    Measurement,
    ProductCategory as PC,
    SiteVisit,
    SiteVisitStatus,
)


class Command(BaseCommand):
    help = "Seed Aluflow CRM with demo data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Aluflow CRM..."))

        company, _ = CompanyProfile.objects.get_or_create(
            pk=1,
            defaults=dict(
                name="Aluflow Investments",
                tagline="Pursuing Dreams, Building Quality",
                email="sales@aluflow.co.zw",
                phone="+263 78 984 2670",
                address="11691 Old SPCA Complex, Seke Road, Hatfield",
                city="Harare",
                country="Zimbabwe",
                tax_number="VAT-2023-001",
                bank_details=(
                    "ALUFLOW INVESTMENTS\n"
                    "CBZ\n"
                    "Account Number: 01127493360017\n"
                    "Kwame Nkrumah Branch"
                ),
                default_vat_percent=Decimal("0"),
                currency_symbol="$",
                currency_code="USD",
            ),
        )

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults=dict(
                email="admin@aluflow.co.zw",
                first_name="Tafadzwa",
                last_name="Makuwe",
                role=Role.ADMIN,
                is_staff=True,
                is_superuser=True,
                phone="+263 77 000 0001",
                job_title="System Administrator",
            ),
        )
        if created:
            admin.set_password("admin12345")
            admin.save()

        demo_users = [
            ("sarah", "Sarah", "Moyo", Role.SALES, "Senior Sales Consultant"),
            ("blessing", "Blessing", "Chirwa", Role.ESTIMATOR, "Estimator"),
            ("kuda", "Kuda", "Ncube", Role.INSTALLER, "Installation Lead"),
            ("rumbi", "Rumbidzai", "Dube", Role.STOREKEEPER, "Storekeeper"),
            ("tendai", "Tendai", "Banda", Role.FINANCE, "Finance Officer"),
            ("nigel", "Nigel", "Sibanda", Role.MANAGER, "Operations Manager"),
        ]
        users = {"admin": admin}
        for username, first, last, role, title in demo_users:
            u, c = User.objects.get_or_create(
                username=username,
                defaults=dict(
                    first_name=first,
                    last_name=last,
                    email=f"{username}@aluflow.co.zw",
                    role=role,
                    job_title=title,
                    is_staff=True,
                ),
            )
            if c:
                u.set_password("password123")
                u.save()
            users[username] = u

        # ------- Customers -------
        customer_seed = [
            ("Mr. Tinashe Madziva", CustomerType.INDIVIDUAL, "+263 77 200 1111", "tinashe@example.com", "12 Borrowdale Lane", "Harare"),
            ("Greenfield Properties Ltd", CustomerType.COMPANY, "+263 24 555 2222", "ops@greenfield.example", "Block C, Westgate", "Harare"),
            ("Royale Hotels Group", CustomerType.COMPANY, "+263 24 600 9988", "procurement@royale.example", "Industrial Drive 8", "Bulawayo"),
        ]
        customers = []
        for fullname, ctype, phone, email, addr, city in customer_seed:
            c, _ = Customer.objects.get_or_create(
                full_name=fullname,
                defaults=dict(
                    customer_type=ctype,
                    company_name=fullname if ctype != CustomerType.INDIVIDUAL else "",
                    phone=phone,
                    email=email,
                    address_line1=addr,
                    city=city,
                    created_by=admin,
                    updated_by=admin,
                ),
            )
            customers.append(c)

        projects = []
        for cust, name, addr in [
            (customers[0], "Madziva Residence Renovation", "12 Borrowdale Lane, Harare"),
            (customers[2], "Royale Hotel Lobby Glass Front", "Industrial Drive 8, Bulawayo"),
        ]:
            p, _ = Project.objects.get_or_create(
                customer=cust,
                name=name,
                defaults=dict(
                    site_address=addr,
                    expected_start=timezone.now().date(),
                    expected_completion=timezone.now().date() + timedelta(days=30),
                    status="active",
                    created_by=admin,
                    updated_by=admin,
                ),
            )
            projects.append(p)

        # ------- Leads (varied) -------
        lead_seed = [
            ("Brian Phiri", "+263 77 444 1212", LeadSource.WHATSAPP, ProductInterest.SLIDING_DOORS, LeadStatus.NEW, users["sarah"]),
            ("Pauline Garwe", "+263 71 333 2211", LeadSource.FACEBOOK, ProductInterest.WINDOWS, LeadStatus.CONTACTED, users["sarah"]),
            ("Innocent Moyo", "+263 24 555 8765", LeadSource.WALK_IN, ProductInterest.SHOPFRONT, LeadStatus.QUOTED, users["sarah"]),
            ("David Chitiyo", "+263 71 700 0007", LeadSource.WEBSITE, ProductInterest.SHOWER_DOORS, LeadStatus.LOST, users["sarah"]),
        ]
        leads = []
        for name, phone, source, interest, status, owner in lead_seed:
            lead, _ = Lead.objects.get_or_create(
                full_name=name,
                phone=phone,
                defaults=dict(
                    source=source,
                    product_interest=interest,
                    status=status,
                    assigned_to=owner,
                    estimated_value=Decimal("3500"),
                    notes="Imported demo lead.",
                    source_url="https://wa.me/263774441212" if source == LeadSource.WHATSAPP else "",
                    created_by=admin,
                    updated_by=admin,
                ),
            )
            leads.append(lead)

        # ------- Lead → Quote → Approval (auto-converts to customer) -------
        # We'll build this against the third lead (Innocent Moyo) so it
        # demonstrates the new lead-quote-approval flow end-to-end.
        plan_lead = leads[2]
        if not plan_lead.quotations.exists():
            quote = Quotation.objects.create(
                lead=plan_lead,
                status=QuotationStatus.DRAFT,
                issue_date=timezone.now().date(),
                valid_until=timezone.now().date() + timedelta(days=14),
                discount_percent=Decimal("0"),
                notes="Quotation prepared from house plans provided over WhatsApp.",
                additional_notes=(
                    "Final pricing subject to on-site verification of measurements. "
                    "Larger openings will be charged as a variation; smaller or equal "
                    "openings will not change the price."
                ),
                created_by=users["sarah"],
                updated_by=users["sarah"],
            )
            QuotationItem.objects.create(
                quotation=quote,
                description="Aluminium shopfront frame & sliding entry door",
                width_mm=4500, height_mm=2800, quantity=Decimal("1"),
                unit_price=Decimal("2400"), sort_order=1,
            )
            QuotationItem.objects.create(
                quotation=quote,
                description="6mm clear glass infill panels",
                quantity=Decimal("12.6"),
                unit_price=Decimal("65"), sort_order=2,
            )
            QuotationItem.objects.create(
                quotation=quote,
                description="On-site installation labour",
                quantity=Decimal("1"), unit_price=Decimal("450"), sort_order=3,
            )

        # ------- An already-approved scenario for the hotel customer -------
        royale = customers[2]
        royale_proj = projects[1]
        if not Quotation.objects.filter(customer=royale).exists():
            q2 = Quotation.objects.create(
                customer=royale,
                project=royale_proj,
                status=QuotationStatus.APPROVED,
                issue_date=timezone.now().date(),
                valid_until=timezone.now().date() + timedelta(days=14),
                discount_percent=Decimal("0"),
                notes="Lobby glass front with branded entrance.",
                created_by=admin,
                updated_by=admin,
            )
            QuotationItem.objects.create(
                quotation=q2,
                description="8mm Tempered Glass Front Panels",
                width_mm=3000, height_mm=2700,
                quantity=Decimal("8"), unit_price=Decimal("950"),
            )
            QuotationItem.objects.create(
                quotation=q2,
                description="Sliding Door Frame & Track System",
                quantity=Decimal("2"), unit_price=Decimal("1850"),
            )
            QuotationItem.objects.create(
                quotation=q2,
                description="On-site installation labour",
                quantity=Decimal("1"), unit_price=Decimal("1200"),
            )
            q2.approved_at = timezone.now()
            q2.save()

            # Job created by signal; but we'll also add a variation
            job = q2.job
            JobVariation.objects.create(
                job=job,
                description=(
                    "Lobby openings re-measured on site — actual size 5% larger "
                    "than the plans. Customer approved the variation by phone."
                ),
                amount=Decimal("750"),
                reason="site_larger",
                customer_acknowledged=True,
                approved_at=timezone.now(),
                approved_by=users["nigel"],
                created_by=users["blessing"],
                updated_by=users["nigel"],
            )

            team, _ = InstallationTeam.objects.get_or_create(
                name="Team A — Harare",
                defaults=dict(leader=users["kuda"], created_by=admin, updated_by=admin),
            )
            team.members.add(users["kuda"], users["rumbi"])
            Installation.objects.get_or_create(
                job=job,
                scheduled_date=timezone.now() + timedelta(days=15),
                defaults=dict(
                    site_address=royale_proj.site_address,
                    team=team,
                    lead_installer=users["kuda"],
                    status=InstallationStatus.SCHEDULED,
                    created_by=admin,
                    updated_by=admin,
                ),
            )

            # Site visit record post-approval (re-measurement)
            sv, _ = SiteVisit.objects.get_or_create(
                customer=royale,
                project=royale_proj,
                defaults=dict(
                    scheduled_date=timezone.now() + timedelta(days=2),
                    site_address=royale_proj.site_address,
                    contact_person=royale.full_name,
                    contact_phone=royale.phone,
                    assigned_to=users["blessing"],
                    status=SiteVisitStatus.SCHEDULED,
                    notes="Confirm measurements before fabrication.",
                    created_by=admin,
                    updated_by=admin,
                ),
            )
            if not sv.measurements.exists():
                Measurement.objects.bulk_create([
                    Measurement(site_visit=sv, location_label="Lobby left",  product_type=PC.SHOPFRONT, width_mm=3050, height_mm=2750, quantity=4, glass_type="8mm tempered", frame_color="charcoal"),
                    Measurement(site_visit=sv, location_label="Lobby right", product_type=PC.SHOPFRONT, width_mm=3050, height_mm=2750, quantity=4, glass_type="8mm tempered", frame_color="charcoal"),
                ])

            invoice, inv_created = Invoice.objects.get_or_create(
                job=job,
                issue_date=timezone.now().date(),
                defaults=dict(
                    customer=royale,
                    due_date=timezone.now().date() + timedelta(days=30),
                    status=InvoiceStatus.PARTIALLY_PAID,
                    subtotal=q2.subtotal,
                    tax_percent=Decimal("0"),
                    deposit_required=q2.grand_total * Decimal("0.75"),
                    created_by=admin,
                    updated_by=admin,
                ),
            )
            if inv_created:
                InvoiceLine.objects.create(invoice=invoice, description="75% Deposit – Royale Hotel Lobby", quantity=Decimal("1"), unit_price=q2.grand_total * Decimal("0.75"))
                InvoiceLine.objects.create(invoice=invoice, description="Balance on completion",          quantity=Decimal("1"), unit_price=q2.grand_total * Decimal("0.25"))
                Payment.objects.create(
                    invoice=invoice,
                    payment_date=timezone.now().date(),
                    amount=q2.grand_total * Decimal("0.75"),
                    method=PaymentMethod.BANK_TRANSFER,
                    reference="DEP-001",
                    is_deposit=True,
                    created_by=admin,
                )

        self.stdout.write(self.style.SUCCESS("✓ Seed data created."))
        self.stdout.write("Login as admin / admin12345")
        self.stdout.write("Other demo users (password: password123): sarah · blessing · kuda · rumbi · tendai · nigel")
