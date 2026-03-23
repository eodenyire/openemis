"""Phase 6 verification."""
import app.db.registry  # noqa
from app.db.session import SessionLocal
from app.models.library import Media, MediaMovement, MediaMovementState
from app.models.hostel import HostelRoom, HostelAllocation, HostelAllocationState
from app.models.transportation import TransportRouteStop, StudentTransport, TransportRoute
from app.models.health import MedicalCondition, Vaccination, StudentHealth, ClinicVisit, VaccinationRecord
from app.api.v1.router import api_router

db = SessionLocal()
print("=== Phase 6 Verification ===\n")

print("--- Library ---")
print(f"  Total movements : {db.query(MediaMovement).count()}")
print(f"  Issued          : {db.query(MediaMovement).filter_by(state=MediaMovementState.ISSUED).count()}")
print(f"  Overdue         : {db.query(MediaMovement).filter_by(state=MediaMovementState.OVERDUE).count()}")
print(f"  Returned        : {db.query(MediaMovement).filter_by(state=MediaMovementState.RETURNED).count()}")
total_fines = sum(m.fine or 0 for m in db.query(MediaMovement).all())
print(f"  Total fines KES : {total_fines}")

print("\n--- Hostel ---")
print(f"  Total rooms     : {db.query(HostelRoom).count()}")
print(f"  Occupied        : {db.query(HostelRoom).filter_by(state='occupied').count()}")
print(f"  Available       : {db.query(HostelRoom).filter_by(state='available').count()}")
print(f"  Allocations     : {db.query(HostelAllocation).count()}")
confirmed = db.query(HostelAllocation).filter_by(state=HostelAllocationState.CONFIRMED).count()
print(f"  Active (confirmed): {confirmed}")

print("\n--- Transport ---")
print(f"  Routes          : {db.query(TransportRoute).count()}")
print(f"  Stops           : {db.query(TransportRouteStop).count()}")
print(f"  Student assigns : {db.query(StudentTransport).count()}")

print("\n--- Health ---")
print(f"  Medical conditions : {db.query(MedicalCondition).count()}")
print(f"  Vaccinations       : {db.query(Vaccination).count()}")
print(f"  Health records     : {db.query(StudentHealth).count()}")
print(f"  Vaccination records: {db.query(VaccinationRecord).count()}")
print(f"  Clinic visits      : {db.query(ClinicVisit).count()}")

from app.models.health import VisitDisposition
referred = db.query(ClinicVisit).filter_by(disposition=VisitDisposition.REFERRED_HOSPITAL).count()
sent_home = db.query(ClinicVisit).filter_by(disposition=VisitDisposition.SENT_HOME).count()
print(f"  Referred to hosp   : {referred}")
print(f"  Sent home          : {sent_home}")

print("\n--- API Routes ---")
p6 = sorted(set(
    r.path for r in api_router.routes
    if any(x in r.path for x in ["/library/", "/hostel/", "/transport/", "/health/"])
))
print(f"  Phase 6 routes: {len(p6)}")
for r in p6:
    print(f"    {r}")

print("\n=== RESULT ===")
checks = [
    db.query(MediaMovement).count() > 0,
    db.query(MedicalCondition).count() > 0,
    db.query(Vaccination).count() > 0,
    db.query(StudentHealth).count() > 0,
    db.query(ClinicVisit).count() > 0,
    len(p6) > 0,
]
if all(checks):
    print("[PASS] Phase 6 fully implemented and seeded.")
else:
    print("[ISSUES] Some checks failed.")
db.close()
