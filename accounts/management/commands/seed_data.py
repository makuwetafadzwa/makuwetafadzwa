"""Management command to seed Aluflow CRM with realistic demo data."""
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, User
from company_settings.models import CompanyProfile
from customers.models import Customer, CustomerType, Project
from finance.models import Invoice, InvoiceLine, InvoiceStatus, Payment, PaymentMethod
from installations.models import Installation, InstallationStatus, InstallationTeam
from inventory.models import (
    Product,
    ProductCategory,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseOrderStatus,
    Supplier,
    UnitOfMeasure,
)
from jobs.models import Job, JobMaterial, JobStatus
from leads.models import Lead, LeadSource, LeadStatus, ProductInterest
from quotations.models import Quotation, QuotationItem, QuotationStatus
from site_visits.models import Measurement, ProductCategory as PC, SiteVisit, SiteVisitStatus


class Command(BaseCommand):
    help = "Seed Aluflow CRM with demo data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Aluflow CRM..."))

        # ------- Company profile -------
        company, _ = CompanyProfile.objects.get_or_create(
            pk=1,
            defaults=dict(
                name="Aluflow Glass & Aluminium",
                tagline="Folding doors · Sliding doors · Windows · Shopfronts",
                email="info@aluflow.example",
                phone="+263 77 123 4567",
                address="14 Industrial Way",
                city="Harare",
                country="Zimbabwe",
                tax_number="VAT-2023-001",
                bank_details="CBZ Bank · 1234567890 · Branch: Avondale",
                default_vat_percent=Decimal("15.00"),
                currency_symbol="$",
                currency_code="USD",
            ),
        )

        # ------- Users -------
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults=dict(
                email="admin@aluflow.example",
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
                    email=f"{username}@aluflow.example",
                    role=role,
                    job_title=title,
                    is_staff=True,
                ),
            )
            if c:
                u.set_password("password123")
                u.save()
            users[username] = u

        # ------- Suppliers -------
        suppliers = []
        for name, contact, phone in [
            ("Saint-Gobain Glass SA", "James K.", "+27 11 555 0101"),
            ("AluPro Extrusions", "Linda M.", "+263 24 234 5678"),
            ("HardwareDirect (Pvt) Ltd", "Peter D.", "+263 77 987 1122"),
        ]:
            s, _ = Supplier.objects.get_or_create(
                name=name,
                defaults=dict(
                    contact_person=contact,
                    phone=phone,
                    email=f"sales@{name.split()[0].lower()}.example",
                    city="Johannesburg" if "Saint" in name else "Harare",
                    payment_terms="30 days",
                    created_by=admin,
                    updated_by=admin,
                ),
            )
            suppliers.append(s)

        # ------- Categories & products -------
        cat_names = ["Aluminium Profiles", "Glass Panels", "Hardware & Accessories", "Services"]
        cats = {}
        for name in cat_names:
            c, _ = ProductCategory.objects.get_or_create(name=name)
            cats[name] = c

        product_seed = [
            ("ALU-FD-100", "Folding Door Profile (silver)", "Aluminium Profiles", UnitOfMeasure.METER, 12, 22, 200, 50, suppliers[1], "material"),
            ("ALU-SLD-120", "Sliding Door Track Profile", "Aluminium Profiles", UnitOfMeasure.METER, 15, 26, 180, 40, suppliers[1], "material"),
            ("ALU-WIN-80", "Casement Window Profile", "Aluminium Profiles", UnitOfMeasure.METER, 10, 18, 320, 60, suppliers[1], "material"),
            ("GLA-CLR-6", "6mm Clear Float Glass", "Glass Panels", UnitOfMeasure.SQM, 28, 55, 80, 20, suppliers[0], "material"),
            ("GLA-TMP-8", "8mm Tempered Glass", "Glass Panels", UnitOfMeasure.SQM, 55, 95, 40, 10, suppliers[0], "material"),
            ("GLA-LAM-10", "10mm Laminated Glass", "Glass Panels", UnitOfMeasure.SQM, 70, 140, 25, 8, suppliers[0], "material"),
            ("HW-HDL-001", "Stainless Steel Door Handle", "Hardware & Accessories", UnitOfMeasure.EACH, 12, 28, 150, 30, suppliers[2], "material"),
            ("HW-LCK-001", "Multi-point Lock System", "Hardware & Accessories", UnitOfMeasure.SET, 35, 80, 60, 15, suppliers[2], "material"),
            ("HW-RUB-001", "EPDM Rubber Gasket (per metre)", "Hardware & Accessories", UnitOfMeasure.METER, 1.5, 4, 9, 20, suppliers[2], "material"),
            ("SVC-INST-001", "Standard Installation (per opening)", "Services", UnitOfMeasure.EACH, 0, 75, 0, 0, None, "service"),
        ]
        products = {}
        for sku, name, cat, unit, cost, sell, stock, reorder, supplier, kind in product_seed:
            p, _ = Product.objects.get_or_create(
                sku=sku,
                defaults=dict(
                    name=name,
                    category=cats[cat],
                    unit=unit,
                    cost_price=Decimal(cost),
                    selling_price=Decimal(sell),
                    stock_quantity=Decimal(stock),
                    reorder_level=Decimal(reorder),
                    preferred_supplier=supplier,
                    kind=kind,
                    created_by=admin,
                    updated_by=admin,
                ),
            )
            products[sku] = p

        # ------- Customers & projects -------
        customer_seed = [
            ("Mr. Tinashe Madziva", CustomerType.INDIVIDUAL, "+263 77 200 1111", "tinashe@example.com", "12 Borrowdale Lane", "Harare"),
            ("Greenfield Properties Ltd", CustomerType.COMPANY, "+263 24 555 2222", "ops@greenfield.example", "Block C, Westgate", "Harare"),
            ("Mrs. Faith Sibanda", CustomerType.INDIVIDUAL, "+263 71 300 4567", "faith@example.com", "5 Avondale Crescent", "Harare"),
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

        # Projects
        projects = []
        for cust, name, addr in [
            (customers[0], "Madziva Residence Renovation", "12 Borrowdale Lane, Harare"),
            (customers[1], "Westgate Office Block – Curtain Wall", "Block C, Westgate"),
            (customers[2], "Sibanda Bathroom Shower Doors", "5 Avondale Crescent, Harare"),
            (customers[3], "Royale Hotel Lobby Glass Front", "Industrial Drive 8, Bulawayo"),
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

        # ------- Leads -------
        lead_seed = [
            ("Brian Phiri", "+263 77 444 1212", LeadSource.WHATSAPP, ProductInterest.SLIDING_DOORS, LeadStatus.NEW, users["sarah"]),
            ("Pauline Garwe", "+263 71 333 2211", LeadSource.FACEBOOK, ProductInterest.WINDOWS, LeadStatus.CONTACTED, users["sarah"]),
            ("Innocent Moyo", "+263 24 555 8765", LeadSource.WALK_IN, ProductInterest.SHOPFRONT, LeadStatus.QUOTED, users["sarah"]),
            ("Chipo Mhembere", "+263 77 999 1010", LeadSource.REFERRAL, ProductInterest.FOLDING_DOORS, LeadStatus.WON, users["sarah"]),
            ("David Chitiyo", "+263 71 700 0007", LeadSource.WEBSITE, ProductInterest.SHOWER_DOORS, LeadStatus.LOST, users["sarah"]),
        ]
        for name, phone, source, interest, status, owner in lead_seed:
            Lead.objects.get_or_create(
                full_name=name,
                phone=phone,
                defaults=dict(
                    source=source,
                    product_interest=interest,
                    status=status,
                    assigned_to=owner,
                    estimated_value=Decimal("3500"),
                    notes="Imported demo lead.",
                    created_by=admin,
                    updated_by=admin,
                ),
            )

        # ------- Site visit + measurements -------
        sv, _ = SiteVisit.objects.get_or_create(
            customer=customers[0],
            project=projects[0],
            defaults=dict(
                scheduled_date=timezone.now() + timedelta(days=2),
                site_address="12 Borrowdale Lane, Harare",
                contact_person=customers[0].full_name,
                contact_phone=customers[0].phone,
                assigned_to=users["blessing"],
                status=SiteVisitStatus.SCHEDULED,
                notes="Confirm sliding door & window dimensions in main bedroom.",
                created_by=admin,
                updated_by=admin,
            ),
        )
        if not sv.measurements.exists():
            Measurement.objects.bulk_create([
                Measurement(site_visit=sv, location_label="Master bedroom window", product_type=PC.WINDOW_SLIDING, width_mm=1800, height_mm=1200, quantity=1, glass_type="6mm clear", frame_color="silver"),
                Measurement(site_visit=sv, location_label="Lounge sliding door", product_type=PC.SLIDING_DOOR, width_mm=2400, height_mm=2100, quantity=1, glass_type="8mm tempered", frame_color="charcoal"),
            ])

        # ------- Quotation -------
        quote, q_created = Quotation.objects.get_or_create(
            customer=customers[3],
            project=projects[3],
            issue_date=timezone.now().date(),
            defaults=dict(
                valid_until=timezone.now().date() + timedelta(days=14),
                status=QuotationStatus.APPROVED,
                discount_percent=Decimal("0"),
                tax_percent=Decimal("15.00"),
                notes="Lobby glass front with branded entrance.",
                created_by=admin,
                updated_by=admin,
            ),
        )
        if q_created:
            QuotationItem.objects.create(
                quotation=quote,
                product=products["GLA-TMP-8"],
                description="8mm Tempered Glass Front Panels",
                width_mm=3000, height_mm=2700,
                quantity=Decimal("8"),
                unit_price=Decimal("950"),
            )
            QuotationItem.objects.create(
                quotation=quote,
                product=products["ALU-SLD-120"],
                description="Sliding Door Frame & Track System",
                quantity=Decimal("2"),
                unit_price=Decimal("1850"),
            )
            QuotationItem.objects.create(
                quotation=quote,
                product=products["SVC-INST-001"],
                description="On-site installation labour",
                quantity=Decimal("1"),
                unit_price=Decimal("1200"),
            )
            quote.approved_at = timezone.now()
            quote.save()

        # ------- Job (auto-created via signal on approve, but ensure exists) -------
        job, _ = Job.objects.get_or_create(
            quotation=quote,
            defaults=dict(
                title="Royale Hotel Lobby Glass Front",
                customer=quote.customer,
                project=quote.project,
                status=JobStatus.FABRICATION,
                contract_value=quote.grand_total,
                start_date=timezone.now().date(),
                target_completion=timezone.now().date() + timedelta(days=21),
                project_manager=users["nigel"],
                created_by=admin,
                updated_by=admin,
            ),
        )
        if not job.materials.exists():
            JobMaterial.objects.create(job=job, product=products["GLA-TMP-8"], quantity_required=Decimal("65"), created_by=admin)
            JobMaterial.objects.create(job=job, product=products["ALU-SLD-120"], quantity_required=Decimal("30"), created_by=admin)
            JobMaterial.objects.create(job=job, product=products["HW-LCK-001"], quantity_required=Decimal("4"), created_by=admin)

        # ------- Installation team & schedule -------
        team, _ = InstallationTeam.objects.get_or_create(
            name="Team A — Harare",
            defaults=dict(leader=users["kuda"], created_by=admin, updated_by=admin),
        )
        team.members.add(users["kuda"], users["rumbi"])
        Installation.objects.get_or_create(
            job=job,
            scheduled_date=timezone.now() + timedelta(days=15),
            defaults=dict(
                site_address=projects[3].site_address,
                team=team,
                lead_installer=users["kuda"],
                status=InstallationStatus.SCHEDULED,
                created_by=admin,
                updated_by=admin,
            ),
        )

        # ------- Invoice + payment -------
        invoice, inv_created = Invoice.objects.get_or_create(
            job=job,
            issue_date=timezone.now().date(),
            defaults=dict(
                customer=job.customer,
                due_date=timezone.now().date() + timedelta(days=30),
                status=InvoiceStatus.PARTIALLY_PAID,
                subtotal=quote.subtotal,
                tax_percent=Decimal("15.00"),
                deposit_required=quote.grand_total / Decimal("2"),
                created_by=admin,
                updated_by=admin,
            ),
        )
        if inv_created:
            InvoiceLine.objects.create(invoice=invoice, description="50% Deposit – Royale Hotel Lobby", quantity=Decimal("1"), unit_price=quote.grand_total / Decimal("2"))
            InvoiceLine.objects.create(invoice=invoice, description="Balance on completion", quantity=Decimal("1"), unit_price=quote.grand_total / Decimal("2"))
            Payment.objects.create(
                invoice=invoice,
                payment_date=timezone.now().date(),
                amount=quote.grand_total / Decimal("2"),
                method=PaymentMethod.BANK_TRANSFER,
                reference="DEP-001",
                is_deposit=True,
                created_by=admin,
            )

        # ------- Purchase Order -------
        po, po_created = PurchaseOrder.objects.get_or_create(
            supplier=suppliers[0],
            order_date=timezone.now().date(),
            defaults=dict(
                expected_date=timezone.now().date() + timedelta(days=10),
                status=PurchaseOrderStatus.ORDERED,
                notes="Restock tempered glass for fabrication runs.",
                created_by=admin,
                updated_by=admin,
            ),
        )
        if po_created:
            PurchaseOrderLine.objects.create(purchase_order=po, product=products["GLA-TMP-8"], quantity=Decimal("60"), unit_cost=Decimal("52"))
            PurchaseOrderLine.objects.create(purchase_order=po, product=products["GLA-CLR-6"], quantity=Decimal("100"), unit_cost=Decimal("26"))

        self.stdout.write(self.style.SUCCESS("✓ Seed data created."))
        self.stdout.write("Login as admin / admin12345")
        self.stdout.write("Other demo users: sarah / blessing / kuda / rumbi / tendai / nigel  (password: password123)")
