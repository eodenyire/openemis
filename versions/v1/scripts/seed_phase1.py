"""Phase 1 seed: permissions for 15 roles + CBC grade levels + learning areas."""
import sys
sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models.user import UserRole, Permission, RolePermission
from app.models.cbc import CBCGradeLevel, LearningArea, GradeBand
from app.core.cbc_utils import ROLE_PERMISSIONS

CBC_GRADE_LEVELS = [
    ("PP1",     "PP1",  GradeBand.PRE_PRIMARY,       1),
    ("PP2",     "PP2",  GradeBand.PRE_PRIMARY,       2),
    ("Grade 1", "G1",   GradeBand.LOWER_PRIMARY,     3),
    ("Grade 2", "G2",   GradeBand.LOWER_PRIMARY,     4),
    ("Grade 3", "G3",   GradeBand.LOWER_PRIMARY,     5),
    ("Grade 4", "G4",   GradeBand.UPPER_PRIMARY,     6),
    ("Grade 5", "G5",   GradeBand.UPPER_PRIMARY,     7),
    ("Grade 6", "G6",   GradeBand.UPPER_PRIMARY,     8),
    ("Grade 7", "G7",   GradeBand.JUNIOR_SECONDARY,  9),
    ("Grade 8", "G8",   GradeBand.JUNIOR_SECONDARY, 10),
    ("Grade 9", "G9",   GradeBand.JUNIOR_SECONDARY, 11),
    ("Grade 10","G10",  GradeBand.SENIOR_SECONDARY, 12),
    ("Grade 11","G11",  GradeBand.SENIOR_SECONDARY, 13),
    ("Grade 12","G12",  GradeBand.SENIOR_SECONDARY, 14),
]

# Learning areas per grade band (MoE Kenya CBC curriculum)
LEARNING_AREAS = {
    GradeBand.PRE_PRIMARY: [
        ("Literacy Activities", "LIT", True),
        ("Kiswahili Language Activities", "KIS", True),
        ("Mathematical Activities", "MATH", True),
        ("Environmental Activities", "ENV", True),
        ("Psychomotor & Creative Activities", "PCA", True),
        ("Religious Education Activities", "REL", False),
    ],
    GradeBand.LOWER_PRIMARY: [
        ("English", "ENG", True),
        ("Kiswahili / KSL", "KIS", True),
        ("Mathematics", "MATH", True),
        ("Environmental & Social Studies", "ESS", True),
        ("Creative Arts & Sports", "CAS", True),
        ("Religious Education", "REL", False),
    ],
    GradeBand.UPPER_PRIMARY: [
        ("English", "ENG", True),
        ("Kiswahili / KSL", "KIS", True),
        ("Mathematics", "MATH", True),
        ("Integrated Science", "SCI", True),
        ("Social Studies", "SST", True),
        ("Creative Arts & Sports", "CAS", True),
        ("Agriculture & Nutrition", "AGR", False),
        ("Religious Education", "REL", False),
    ],
    GradeBand.JUNIOR_SECONDARY: [
        ("English", "ENG", True),
        ("Kiswahili / KSL", "KIS", True),
        ("Mathematics", "MATH", True),
        ("Integrated Science", "SCI", True),
        ("Social Studies", "SST", True),
        ("Creative Arts & Sports", "CAS", True),
        ("Pre-Technical & Pre-Career Education", "PTE", True),
        ("Agriculture & Nutrition", "AGR", False),
        ("Religious Education", "REL", False),
    ],
    GradeBand.SENIOR_SECONDARY: [
        ("English", "ENG", True),
        ("Kiswahili / KSL", "KIS", True),
        ("Mathematics", "MATH", True),
        ("Biology", "BIO", False),
        ("Chemistry", "CHEM", False),
        ("Physics", "PHY", False),
        ("History & Citizenship", "HIST", False),
        ("Geography", "GEO", False),
        ("Business Studies", "BST", False),
        ("Computer Science", "CS", False),
        ("Agriculture", "AGR", False),
        ("Religious Education", "REL", False),
    ],
}


def main():
    db = SessionLocal()
    try:
        # ── 1. Permissions ────────────────────────────────────────────────────
        existing_perms = {p.code for p in db.query(Permission).all()}
        new_perms = {}
        for role_key, perm_codes in ROLE_PERMISSIONS.items():
            for code in perm_codes:
                if code not in existing_perms and code not in new_perms:
                    parts = code.split(":")
                    resource, action, scope = parts[0], parts[1], parts[2]
                    p = Permission(code=code, resource=resource, action=action, scope=scope,
                                   description=f"{action} {resource} at {scope} level")
                    db.add(p)
                    new_perms[code] = p
        db.flush()
        print(f"✓ Created {len(new_perms)} permissions")

        # ── 2. Role → Permission mappings ─────────────────────────────────────
        all_perms = {p.code: p for p in db.query(Permission).all()}
        existing_rp = {
            (rp.role, rp.permission_id)
            for rp in db.query(RolePermission).all()
        }
        rp_count = 0
        for role_key, perm_codes in ROLE_PERMISSIONS.items():
            for code in perm_codes:
                perm = all_perms.get(code)
                if perm and (role_key, perm.id) not in existing_rp:
                    db.add(RolePermission(role=role_key, permission_id=perm.id))
                    rp_count += 1
        db.flush()
        print(f"✓ Created {rp_count} role-permission mappings")

        # ── 3. CBC Grade Levels ───────────────────────────────────────────────
        existing_grades = {g.code for g in db.query(CBCGradeLevel).all()}
        grade_objs = {}
        for name, code, band, order in CBC_GRADE_LEVELS:
            if code not in existing_grades:
                g = CBCGradeLevel(name=name, code=code, grade_band=band, order=order)
                db.add(g)
                grade_objs[code] = g
        db.flush()
        # Reload all grades
        all_grades = {g.code: g for g in db.query(CBCGradeLevel).all()}
        print(f"✓ CBC grade levels: {len(all_grades)} total")

        # ── 4. Learning Areas ─────────────────────────────────────────────────
        la_count = 0
        for name, code, band, order in CBC_GRADE_LEVELS:
            grade = all_grades.get(code)
            if not grade:
                continue
            areas = LEARNING_AREAS.get(band, [])
            existing_la = {
                la.code for la in db.query(LearningArea)
                .filter(LearningArea.grade_level_id == grade.id).all()
            }
            for la_name, la_code, is_core in areas:
                if la_code not in existing_la:
                    db.add(LearningArea(
                        name=la_name, code=la_code,
                        grade_level_id=grade.id, is_core=is_core,
                    ))
                    la_count += 1
        db.flush()
        print(f"✓ Created {la_count} learning areas")

        db.commit()
        print("\n✅ Phase 1 seed complete!")

    except Exception as e:
        db.rollback()
        import traceback; traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
