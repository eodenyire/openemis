"""Phase 6 seed — Library, Hostel, Transport, Health enrichment."""
import sys, random
from datetime import date, timedelta

import app.db.registry  # noqa

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.people import Student
from app.models.core import AcademicYear
from app.models.library import Media, MediaMovement, MediaMovementState
from app.models.hostel import HostelRoom, HostelAllocation, HostelAllocationState, HostelRoomType
from app.models.transportation import Vehicle, TransportRoute, TransportRouteStop, StudentTransport
from app.models.health import (
    MedicalCondition, Vaccination, StudentHealth,
    ClinicVisit, VaccinationRecord, VisitType, VisitDisposition,
)

Base.metadata.create_all(bind=engine)
db = SessionLocal()
print("=== Phase 6 Seed ===")

students = db.query(Student).limit(50).all()
year = db.query(AcademicYear).first()
print(f"[INFO] {len(students)} students, year={year.name if year else 'N/A'}")

# ── Library: additional movements (issue/return/overdue) ─────────────────────
books = db.query(Media).filter(Media.available_copies > 0).limit(20).all()
movement_count = 0
today = date.today()

for i, student in enumerate(students[:25]):
    if not books: break
    book = books[i % len(books)]
    if book.available_copies < 1:
        continue
    # Check not already issued
    existing = db.query(MediaMovement).filter_by(
        media_id=book.id, student_id=student.id,
        state=MediaMovementState.ISSUED).first()
    if existing:
        continue
    # Mix of: returned, overdue, currently issued
    scenario = i % 4
    if scenario == 0:
        # Returned on time
        issue = today - timedelta(days=20)
        due = today - timedelta(days=7)
        ret = today - timedelta(days=10)
        db.add(MediaMovement(
            media_id=book.id, student_id=student.id,
            issue_date=issue, due_date=due, return_date=ret,
            state=MediaMovementState.RETURNED, fine=0,
        ))
    elif scenario == 1:
        # Overdue — not yet returned
        issue = today - timedelta(days=30)
        due = today - timedelta(days=10)
        overdue_days = (today - due).days
        db.add(MediaMovement(
            media_id=book.id, student_id=student.id,
            issue_date=issue, due_date=due,
            state=MediaMovementState.OVERDUE,
            fine=overdue_days * 5,
        ))
        book.available_copies = max(0, book.available_copies - 1)
    elif scenario == 2:
        # Currently issued, due in future
        issue = today - timedelta(days=5)
        due = today + timedelta(days=9)
        db.add(MediaMovement(
            media_id=book.id, student_id=student.id,
            issue_date=issue, due_date=due,
            state=MediaMovementState.ISSUED, fine=0,
        ))
        book.available_copies = max(0, book.available_copies - 1)
    else:
        # Returned late with fine
        issue = today - timedelta(days=25)
        due = today - timedelta(days=15)
        ret = today - timedelta(days=5)
        fine = (ret - due).days * 5
        db.add(MediaMovement(
            media_id=book.id, student_id=student.id,
            issue_date=issue, due_date=due, return_date=ret,
            state=MediaMovementState.RETURNED, fine=fine,
        ))
    movement_count += 1

db.commit()
print(f"[OK] {movement_count} library movements created")

# ── Hostel: fix room states based on actual occupancy ────────────────────────
rooms = db.query(HostelRoom).all()
for room in rooms:
    occupied = db.query(HostelAllocation).filter_by(
        room_id=room.id, state=HostelAllocationState.CONFIRMED).count()
    if occupied >= room.capacity:
        room.state = "occupied"
    elif occupied > 0:
        room.state = "available"
db.commit()
print(f"[OK] Hostel room states updated for {len(rooms)} rooms")

# ── Transport: add more stops to existing routes ──────────────────────────────
routes = db.query(TransportRoute).all()
STOP_NAMES = [
    ["Town Centre", "Market Junction", "Hospital Road", "School Gate"],
    ["Westlands", "Parklands", "Highridge", "School Gate"],
    ["Eastleigh", "Pangani", "Ngara", "School Gate"],
    ["Karen", "Langata", "Rongai", "School Gate"],
    ["Thika Road", "Roysambu", "Kasarani", "School Gate"],
]
stop_count = 0
for i, route in enumerate(routes):
    existing_stops = db.query(TransportRouteStop).filter_by(route_id=route.id).count()
    if existing_stops >= 3:
        continue
    stops = STOP_NAMES[i % len(STOP_NAMES)]
    for seq, name in enumerate(stops, 1):
        if not db.query(TransportRouteStop).filter_by(
                route_id=route.id, name=name).first():
            hour = 6 + seq
            db.add(TransportRouteStop(
                route_id=route.id, name=name, sequence=seq,
                pickup_time=f"0{hour}:{'00' if seq % 2 == 0 else '30'}",
                location=f"{name}, Nairobi",
            ))
            stop_count += 1
db.commit()
print(f"[OK] {stop_count} transport stops added")

# ── Health: medical conditions ────────────────────────────────────────────────
CONDITIONS = [
    ("Asthma", "Chronic respiratory condition requiring inhaler"),
    ("Diabetes Type 1", "Insulin-dependent diabetes"),
    ("Epilepsy", "Seizure disorder — has emergency medication"),
    ("Sickle Cell Anaemia", "Genetic blood disorder"),
    ("Hypertension", "High blood pressure"),
    ("Allergic Rhinitis", "Seasonal allergies"),
    ("Eczema", "Chronic skin condition"),
    ("Visual Impairment", "Requires corrective lenses"),
    ("Hearing Impairment", "Partial hearing loss"),
    ("Physical Disability", "Mobility assistance required"),
]
cond_count = 0
for name, desc in CONDITIONS:
    if not db.query(MedicalCondition).filter_by(name=name).first():
        db.add(MedicalCondition(name=name, description=desc))
        cond_count += 1
db.commit()
print(f"[OK] {cond_count} medical conditions created")

# ── Health: vaccinations ──────────────────────────────────────────────────────
VACCINATIONS = [
    ("BCG", "Bacillus Calmette-Guérin — tuberculosis", 1),
    ("OPV", "Oral Polio Vaccine", 4),
    ("DPT-HepB-Hib", "Diphtheria, Pertussis, Tetanus, Hepatitis B, Hib", 3),
    ("PCV", "Pneumococcal Conjugate Vaccine", 3),
    ("Rotavirus", "Rotavirus gastroenteritis vaccine", 2),
    ("Measles-Rubella", "Measles and Rubella combined vaccine", 2),
    ("Yellow Fever", "Yellow fever vaccine", 1),
    ("HPV", "Human Papillomavirus — girls aged 10+", 2),
    ("Tetanus Toxoid", "Tetanus booster", 5),
    ("COVID-19", "COVID-19 vaccine", 2),
]
vacc_count = 0
for name, desc, doses in VACCINATIONS:
    if not db.query(Vaccination).filter_by(name=name).first():
        db.add(Vaccination(name=name, description=desc, doses_required=doses))
        vacc_count += 1
db.commit()
print(f"[OK] {vacc_count} vaccinations created")

# ── Health: student health records ───────────────────────────────────────────
conditions = db.query(MedicalCondition).all()
vaccinations = db.query(Vaccination).all()
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
health_count = 0
visit_count = 0
vacc_record_count = 0

for student in students[:40]:
    if db.query(StudentHealth).filter_by(student_id=student.id).first():
        continue
    height = round(random.uniform(140, 175), 1)
    weight = round(random.uniform(35, 70), 1)
    bmi = round(weight / ((height / 100) ** 2), 1)
    record = StudentHealth(
        student_id=student.id,
        blood_group=random.choice(BLOOD_GROUPS),
        height=height, weight=weight, bmi=bmi,
        allergies=random.choice([None, None, None, "Peanuts", "Dust", "Pollen"]),
        emergency_contact_name=f"Parent of {student.first_name}",
        emergency_contact_phone=f"07{random.randint(10000000, 99999999)}",
        emergency_contact_relation=random.choice(["Mother", "Father", "Guardian"]),
        doctor_name=random.choice(["Dr. Kamau", "Dr. Odhiambo", "Dr. Wanjiku", "Dr. Mwangi"]),
        doctor_phone=f"07{random.randint(10000000, 99999999)}",
        insurance_provider=random.choice(["NHIF", "AAR", "Jubilee", "CIC", None]),
        last_checkup_date=date.today() - timedelta(days=random.randint(30, 365)),
    )
    db.add(record); db.flush()
    health_count += 1

    # Add 1-2 conditions to some students
    if random.random() < 0.2:
        cond = random.choice(conditions)
        if cond not in record.conditions:
            record.conditions.append(cond)

    # Add vaccination records
    for vacc in random.sample(vaccinations, min(3, len(vaccinations))):
        db.add(VaccinationRecord(
            health_id=record.id,
            student_id=student.id,
            vaccination_id=vacc.id,
            dose_number=1,
            date_given=date.today() - timedelta(days=random.randint(180, 1800)),
            administered_by="School Nurse",
            batch_number=f"BN{random.randint(10000, 99999)}",
        ))
        vacc_record_count += 1

db.commit()
print(f"[OK] {health_count} health records, {vacc_record_count} vaccination records")

# ── Clinic visits ─────────────────────────────────────────────────────────────
COMPLAINTS = [
    ("Headache and fever", "Malaria suspected", "Artemether-Lumefantrine given", "treated_sent_back"),
    ("Stomach pain", "Gastroenteritis", "ORS and antispasmodics", "sent_home"),
    ("Injury — fell during PE", "Sprained ankle", "Ice pack and bandage applied", "treated_sent_back"),
    ("Persistent cough", "Upper respiratory tract infection", "Cough syrup and antibiotics", "treated_sent_back"),
    ("Dizziness and weakness", "Anaemia suspected", "Referred for blood test", "referred_hospital"),
    ("Eye pain", "Conjunctivitis", "Eye drops prescribed", "treated_sent_back"),
    ("Toothache", "Dental caries", "Referred to dentist", "referred_hospital"),
    ("Asthma attack", "Bronchospasm", "Salbutamol inhaler administered", "treated_sent_back"),
]
VISIT_TYPES = ["sick", "sick", "sick", "injury", "routine", "follow_up"]

health_records = db.query(StudentHealth).all()
for record in health_records[:30]:
    num_visits = random.randint(1, 3)
    for _ in range(num_visits):
        complaint, diagnosis, treatment, disposition = random.choice(COMPLAINTS)
        visit_date = date.today() - timedelta(days=random.randint(0, 90))
        db.add(ClinicVisit(
            health_id=record.id,
            student_id=record.student_id,
            visit_date=visit_date,
            visit_type=VisitType(random.choice(VISIT_TYPES)),
            complaint=complaint,
            diagnosis=diagnosis,
            treatment=treatment,
            disposition=VisitDisposition(disposition),
            attended_by=random.choice(["Nurse Achieng", "Nurse Kamau", "Dr. Wanjiku"]),
            follow_up_date=(visit_date + timedelta(days=7)) if random.random() < 0.3 else None,
        ))
        visit_count += 1

db.commit()
print(f"[OK] {visit_count} clinic visits created")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n=== Phase 6 Seed Complete ===")
print(f"  Library movements   : {movement_count}")
print(f"  Medical conditions  : {cond_count}")
print(f"  Vaccinations        : {vacc_count}")
print(f"  Health records      : {health_count}")
print(f"  Vaccination records : {vacc_record_count}")
print(f"  Clinic visits       : {visit_count}")
print(f"  Transport stops     : {stop_count}")
db.close()
