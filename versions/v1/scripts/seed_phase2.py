"""Phase 2 seed: Tenants, TenantGroups, M-Pesa test transactions, finance data."""
import sys
sys.path.insert(0, ".")

import app.db.registry  # noqa — must be first to register all models
from app.db.session import SessionLocal
from app.models.tenant import Tenant, TenantGroup, SchoolType, SubscriptionPlan
from app.models.mpesa import MpesaTransaction, MpesaTransactionStatus
from app.models.fees import StudentFeeInvoice, FeePayment, PaymentState
from app.models.people import Student
import random
from datetime import date, timedelta

COUNTIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
    "Thika", "Machakos", "Nyeri", "Meru", "Kakamega",
]

SCHOOL_NAMES = [
    ("Nairobi CBC Academy", "nairobi-cbc", "Nairobi", SchoolType.PRIVATE, SubscriptionPlan.PREMIUM),
    ("Mombasa Coastal School", "mombasa-coastal", "Mombasa", SchoolType.PUBLIC, SubscriptionPlan.STANDARD),
    ("Kisumu Lakeside Primary", "kisumu-lakeside", "Kisumu", SchoolType.PUBLIC, SubscriptionPlan.BASIC),
    ("Nakuru Hills Academy", "nakuru-hills", "Nakuru", SchoolType.PRIVATE, SubscriptionPlan.STANDARD),
    ("Eldoret Highlands School", "eldoret-highlands", "Uasin Gishu", SchoolType.PUBLIC, SubscriptionPlan.BASIC),
]


def main():
    db = SessionLocal()
    try:
        # ── Idempotency ───────────────────────────────────────────────────────
        if db.query(Tenant).first():
            print("Phase 2 already seeded. Exiting.")
            return

        # ── 1. Tenant Groups (county clusters) ────────────────────────────────
        groups = {}
        for county in ["Nairobi", "Coast", "Nyanza", "Rift Valley"]:
            g = TenantGroup(
                name=f"{county} Schools Network",
                code=county.lower().replace(" ", "-"),
                county=county,
                contact_email=f"admin@{county.lower().replace(' ', '')}.schools.ke",
                contact_phone=f"07{random.randint(10000000, 99999999)}",
            )
            db.add(g)
            groups[county] = g
        db.flush()
        print(f"✓ Created {len(groups)} tenant groups")

        # ── 2. Tenants (schools) ──────────────────────────────────────────────
        group_list = list(groups.values())
        tenants = []
        for name, slug, county, stype, plan in SCHOOL_NAMES:
            t = Tenant(
                name=name,
                slug=slug,
                school_type=stype,
                subscription_plan=plan,
                county=county,
                email=f"info@{slug}.ac.ke",
                phone=f"07{random.randint(10000000, 99999999)}",
                nemis_code=f"NEMIS{random.randint(10000, 99999)}",
                group_id=random.choice(group_list).id,
                is_active=True,
            )
            db.add(t)
            tenants.append(t)
        db.flush()
        print(f"✓ Created {len(tenants)} tenant schools")

        # ── 3. M-Pesa test transactions ───────────────────────────────────────
        students = db.query(Student).limit(20).all()
        invoices = db.query(StudentFeeInvoice).filter(
            StudentFeeInvoice.state == PaymentState.PENDING
        ).limit(20).all()

        mpesa_count = 0
        for i, invoice in enumerate(invoices[:15]):
            student = students[i % len(students)] if students else None
            status = random.choice([
                MpesaTransactionStatus.SUCCESS,
                MpesaTransactionStatus.SUCCESS,
                MpesaTransactionStatus.SUCCESS,
                MpesaTransactionStatus.FAILED,
                MpesaTransactionStatus.PENDING,
            ])
            receipt = f"QHX{random.randint(1000000, 9999999)}" if status == MpesaTransactionStatus.SUCCESS else None
            txn = MpesaTransaction(
                checkout_request_id=f"ws_CO_TEST_{random.randint(100000000, 999999999)}",
                merchant_request_id=f"MR_{random.randint(10000, 99999)}",
                phone_number=f"2547{random.randint(10000000, 99999999)}",
                amount=invoice.total_amount,
                account_reference=f"INV{invoice.id}",
                transaction_desc="School Fee Payment",
                status=status,
                result_code="0" if status == MpesaTransactionStatus.SUCCESS else "1032",
                result_desc="The service request is processed successfully." if status == MpesaTransactionStatus.SUCCESS else "Request cancelled by user",
                mpesa_receipt_number=receipt,
                invoice_id=invoice.id,
                student_id=invoice.student_id,
            )
            db.add(txn)

            # Update invoice if payment succeeded
            if status == MpesaTransactionStatus.SUCCESS:
                payment = FeePayment(
                    invoice_id=invoice.id,
                    amount=invoice.total_amount,
                    payment_date=date.today() - timedelta(days=random.randint(0, 30)),
                    payment_method="mpesa",
                    reference=receipt,
                    note=f"M-Pesa: {receipt}",
                )
                db.add(payment)
                invoice.paid_amount = invoice.total_amount
                invoice.state = PaymentState.PAID
            mpesa_count += 1

        db.flush()
        print(f"✓ Created {mpesa_count} M-Pesa test transactions")

        db.commit()
        print("\n✅ Phase 2 seed complete!")
        print("   Tenants: 5 schools across 4 county groups")
        print("   M-Pesa: 15 test transactions (mix of success/failed/pending)")

    except Exception as e:
        db.rollback()
        import traceback; traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
