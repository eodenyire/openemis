"""
Kenya CBC Seed Script
Run from project root: python scripts/seed_kenya.py
"""
import sys
import os
import random
from datetime import date, datetime, timedelta, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db import registry  # ensures all models are registered
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.core import (
    Department, ProgramLevel, Program, Course, Batch, Subject,
    AcademicYear, AcademicTerm, StudentCategory, EvaluationType,
    SubjectType, SubjectCategory, course_subjects, teacher_subjects
)
from app.models.people import Teacher, Student, StudentCourse, Parent, ParentRelationship
from app.models.fees import FeesTerm, FeesTermLine, FeesElement, StudentFeeInvoice, FeePayment, PaymentState
from app.models.attendance import AttendanceRegister, AttendanceSheet, AttendanceLine, AttendanceStatus, AttendanceSheetState
from app.models.exam import ExamSession, Exam, ExamAttendees, GradingConfig, GradingRule, ExamState
from app.models.assignment import Assignment, AssignmentSubmission, AssignmentState
from app.models.timetable import Timing, Classroom, Session as TimetableSession, DayOfWeek, SessionState
from app.models.library import MediaType, Author, Publisher, LibraryTag, Media, MediaMovement, MediaMovementState
from app.models.hostel import HostelBlock, HostelRoomType, HostelRoom, HostelAllocation, HostelAllocationState
from app.models.transportation import Vehicle, TransportRoute, TransportRouteStop, StudentTransport
from app.models.extras import (
    AchievementType, Achievement, ActivityType, Activity,
    BlogCategory, BlogPost, EventType, Event, EventRegistration,
    DisciplineAction, InventoryCategory, InventoryItem,
    NoticeBoard, ScholarshipType, Scholarship, FoodCategory
)
from app.models.core import Gender, BloodGroup

random.seed(42)

# ── Name pools ────────────────────────────────────────────────────────────────
FIRST_NAMES_MALE = [
    "Kamau", "Njoroge", "Mwangi", "Kariuki", "Gitau", "Waweru", "Kimani", "Mugo",
    "Ndung'u", "Gichuki", "Omondi", "Otieno", "Owino", "Achieng", "Odhiambo",
    "Mutua", "Musyoka", "Muthama", "Kioko", "Ndeti", "Korir", "Kipchoge", "Ruto",
    "Bett", "Cheruiyot", "Hassan", "Omar", "Abdi", "Farah", "Ahmed", "Wekesa",
    "Simiyu", "Barasa", "Wafula", "Khisa", "Ngugi", "Kinyua", "Mureithi", "Njenga", "Macharia"
]
FIRST_NAMES_FEMALE = [
    "Wanjiku", "Njeri", "Wambui", "Wairimu", "Nyambura", "Akinyi", "Adhiambo",
    "Atieno", "Awino", "Akoth", "Muthoni", "Wangari", "Wanjiru", "Mumbi", "Waceera",
    "Chebet", "Jepkoech", "Rotich", "Jelimo", "Chepkemoi", "Fatuma", "Amina",
    "Halima", "Zainab", "Maryam", "Nafula", "Nekesa", "Nasimiyu", "Nanjala",
    "Nabwire", "Zawadi", "Imani", "Amani", "Furaha", "Neema"
]
LAST_NAMES = [
    "Kamau", "Njoroge", "Mwangi", "Kariuki", "Gitau", "Waweru", "Kimani", "Mugo",
    "Omondi", "Otieno", "Owino", "Mutua", "Musyoka", "Korir", "Kipchoge", "Hassan",
    "Omar", "Wekesa", "Simiyu", "Barasa", "Ngugi", "Kinyua", "Mureithi", "Njenga",
    "Macharia", "Auma", "Anyango", "Ogola", "Odinga", "Obiero", "Nzomo", "Ndolo",
    "Mwenda", "Kilonzo", "Makau", "Mbatha", "Mbithi", "Nthenge", "Muema"
]
BLOOD_GROUPS = list(BloodGroup)


def pick_name(i, pool_male, pool_female):
    """Alternate male/female by index."""
    if i % 2 == 0:
        return random.choice(pool_male), Gender.MALE
    return random.choice(pool_female), Gender.FEMALE


def make_email(first, last, suffix=""):
    clean_first = first.lower().replace("'", "")
    slug = f"{clean_first}.{last.lower()}{suffix}"
    return f"{slug}@kenyacbc.ac.ke"


def main():
    db = SessionLocal()
    try:
        # ── Idempotency check ─────────────────────────────────────────────────
        existing = db.query(User).filter(User.username == "teacher001").first()
        if existing:
            print("Database already seeded. Exiting.")
            return

        # ── 0. Admin user (upsert — may already exist) ────────────────────────
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            # Update existing admin to match expected state
            admin.email = "admin@kenyacbc.ac.ke"
            admin.first_name = "System"
            admin.last_name = "Administrator"
            admin.is_superuser = True
            db.flush()
            print("✓ Updated existing admin user")
        else:
            admin = User(
                email="admin@kenyacbc.ac.ke",
                username="admin",
                hashed_password=get_password_hash("Admin@1234"),
                first_name="System",
                last_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True,
            )
            db.add(admin)
            db.flush()
            print("✓ Created admin user")

        # ── 1. StudentCategory ────────────────────────────────────────────────
        cat_data = [
            ("Day Scholar", "DAY", "Student who commutes daily"),
            ("Boarder", "BOARD", "Student who lives in school hostel"),
            ("Needy", "NEEDY", "Student on bursary / financial support"),
        ]
        categories = {}
        for name, code, desc in cat_data:
            c = StudentCategory(name=name, code=code, description=desc)
            db.add(c)
            categories[name] = c
        db.flush()
        print("✓ Created student categories")

        # ── 2. ProgramLevel ───────────────────────────────────────────────────
        pl_data = [
            ("Pre-Primary", "PP", "CBC Pre-Primary level (PP1-PP2)"),
            ("Lower Primary", "LP", "CBC Lower Primary (Grade 1-3)"),
            ("Upper Primary", "UP", "CBC Upper Primary (Grade 4-6)"),
            ("Junior Secondary", "JS", "CBC Junior Secondary (Grade 7-9)"),
            ("Senior Secondary", "SS", "CBC Senior Secondary (Grade 10-12)"),
        ]
        prog_levels = {}
        for name, code, desc in pl_data:
            pl = ProgramLevel(name=name, code=code, description=desc)
            db.add(pl)
            prog_levels[name] = pl
        db.flush()
        print("✓ Created program levels")

        # ── 3. Departments ────────────────────────────────────────────────────
        dept_data = [
            ("Pre-Primary", "DEPT-PP"),
            ("Lower Primary", "DEPT-LP"),
            ("Upper Primary", "DEPT-UP"),
            ("Junior Secondary", "DEPT-JS"),
            ("Senior Secondary", "DEPT-SS"),
            ("Administration", "DEPT-ADM"),
        ]
        depts = {}
        for name, code in dept_data:
            d = Department(name=name, code=code)
            db.add(d)
            depts[name] = d
        db.flush()
        print("✓ Created departments")

        # ── 4. Programs ───────────────────────────────────────────────────────
        prog_data = [
            ("CBC Pre-Primary", "PROG-PP", "Pre-Primary", "Pre-Primary"),
            ("CBC Lower Primary", "PROG-LP", "Lower Primary", "Lower Primary"),
            ("CBC Upper Primary", "PROG-UP", "Upper Primary", "Upper Primary"),
            ("CBC Junior Secondary", "PROG-JS", "Junior Secondary", "Junior Secondary"),
            ("CBC Senior Secondary", "PROG-SS", "Senior Secondary", "Senior Secondary"),
        ]
        programs = {}
        for name, code, dept_key, pl_key in prog_data:
            p = Program(
                name=name, code=code,
                department_id=depts[dept_key].id,
                program_level_id=prog_levels[pl_key].id,
            )
            db.add(p)
            programs[name] = p
        db.flush()
        print("✓ Created programs")

        # ── 5. AcademicYear ───────────────────────────────────────────────────
        ay2024 = AcademicYear(
            name="2024", code="AY2024",
            start_date=date(2024, 1, 1), end_date=date(2024, 12, 31),
            is_current=True,
        )
        ay2025 = AcademicYear(
            name="2025", code="AY2025",
            start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
            is_current=False,
        )
        db.add_all([ay2024, ay2025])
        db.flush()
        print("✓ Created academic years")

        # ── 6. AcademicTerms ──────────────────────────────────────────────────
        term_defs = [
            ("Term 1 2024", "T1-2024", date(2024, 1, 8), date(2024, 4, 5), True, ay2024.id),
            ("Term 2 2024", "T2-2024", date(2024, 5, 6), date(2024, 8, 9), False, ay2024.id),
            ("Term 3 2024", "T3-2024", date(2024, 9, 2), date(2024, 11, 29), False, ay2024.id),
            ("Term 1 2025", "T1-2025", date(2025, 1, 6), date(2025, 4, 4), False, ay2025.id),
            ("Term 2 2025", "T2-2025", date(2025, 5, 5), date(2025, 8, 8), False, ay2025.id),
            ("Term 3 2025", "T3-2025", date(2025, 9, 1), date(2025, 11, 28), False, ay2025.id),
        ]
        terms = {}
        for name, code, sd, ed, is_cur, ay_id in term_defs:
            t = AcademicTerm(name=name, code=code, start_date=sd, end_date=ed,
                             is_current=is_cur, academic_year_id=ay_id)
            db.add(t)
            terms[code] = t
        db.flush()
        print("✓ Created academic terms")

        # ── 7. Courses (CBC grade levels) ─────────────────────────────────────
        course_defs = [
            ("PP1",     "PP1",     "Pre-Primary",    "CBC Pre-Primary"),
            ("PP2",     "PP2",     "Pre-Primary",    "CBC Pre-Primary"),
            ("Grade 1", "GR1",     "Lower Primary",  "CBC Lower Primary"),
            ("Grade 2", "GR2",     "Lower Primary",  "CBC Lower Primary"),
            ("Grade 3", "GR3",     "Lower Primary",  "CBC Lower Primary"),
            ("Grade 4", "GR4",     "Upper Primary",  "CBC Upper Primary"),
            ("Grade 5", "GR5",     "Upper Primary",  "CBC Upper Primary"),
            ("Grade 6", "GR6",     "Upper Primary",  "CBC Upper Primary"),
            ("Grade 7", "GR7",     "Junior Secondary", "CBC Junior Secondary"),
            ("Grade 8", "GR8",     "Junior Secondary", "CBC Junior Secondary"),
            ("Grade 9", "GR9",     "Junior Secondary", "CBC Junior Secondary"),
            ("Grade 10","GR10",    "Senior Secondary", "CBC Senior Secondary"),
            ("Grade 11","GR11",    "Senior Secondary", "CBC Senior Secondary"),
            ("Grade 12","GR12",    "Senior Secondary", "CBC Senior Secondary"),
        ]
        courses = {}
        for name, code, dept_key, prog_key in course_defs:
            c = Course(
                name=name, code=code,
                department_id=depts[dept_key].id,
                program_id=programs[prog_key].id,
                evaluation_type=EvaluationType.NORMAL,
                duration_years=1,
            )
            db.add(c)
            courses[name] = c
        db.flush()
        print("✓ Created courses (grade levels)")

        # ── 8. Subjects ───────────────────────────────────────────────────────
        subject_defs = [
            # (code, name, type, category, dept_key)
            ("MATH",  "Mathematics",              SubjectType.THEORY,     SubjectCategory.COMPULSORY, "Lower Primary"),
            ("ENG",   "English",                  SubjectType.THEORY,     SubjectCategory.COMPULSORY, "Lower Primary"),
            ("KIS",   "Kiswahili",                SubjectType.THEORY,     SubjectCategory.COMPULSORY, "Lower Primary"),
            ("SCI",   "Science & Technology",     SubjectType.BOTH,       SubjectCategory.COMPULSORY, "Upper Primary"),
            ("SST",   "Social Studies",           SubjectType.THEORY,     SubjectCategory.COMPULSORY, "Upper Primary"),
            ("CRE",   "Christian Religious Education", SubjectType.THEORY, SubjectCategory.ELECTIVE,  "Upper Primary"),
            ("IRE",   "Islamic Religious Education",   SubjectType.THEORY, SubjectCategory.ELECTIVE,  "Upper Primary"),
            ("CAC",   "Creative Arts & Crafts",   SubjectType.PRACTICAL,  SubjectCategory.COMPULSORY, "Lower Primary"),
            ("PHE",   "Physical & Health Education", SubjectType.PRACTICAL, SubjectCategory.COMPULSORY, "Lower Primary"),
            ("AGR",   "Agriculture",              SubjectType.BOTH,       SubjectCategory.ELECTIVE,   "Junior Secondary"),
            ("HSC",   "Home Science",             SubjectType.BOTH,       SubjectCategory.ELECTIVE,   "Junior Secondary"),
            ("PTS",   "Pre-Technical Studies",    SubjectType.BOTH,       SubjectCategory.COMPULSORY, "Junior Secondary"),
            ("BST",   "Business Studies",         SubjectType.THEORY,     SubjectCategory.ELECTIVE,   "Senior Secondary"),
            ("CS",    "Computer Science",         SubjectType.BOTH,       SubjectCategory.ELECTIVE,   "Senior Secondary"),
            ("LSK",   "Life Skills",              SubjectType.THEORY,     SubjectCategory.COMPULSORY, "Junior Secondary"),
            ("MUS",   "Music",                    SubjectType.PRACTICAL,  SubjectCategory.ELECTIVE,   "Upper Primary"),
            ("VA",    "Visual Arts",              SubjectType.PRACTICAL,  SubjectCategory.ELECTIVE,   "Upper Primary"),
            ("PA",    "Performing Arts",          SubjectType.PRACTICAL,  SubjectCategory.ELECTIVE,   "Junior Secondary"),
            ("ENV",   "Environmental Activities", SubjectType.BOTH,       SubjectCategory.COMPULSORY, "Pre-Primary"),
            ("HYG",   "Hygiene & Nutrition",      SubjectType.THEORY,     SubjectCategory.COMPULSORY, "Pre-Primary"),
        ]
        subjects = {}
        for code, name, stype, scat, dept_key in subject_defs:
            s = Subject(
                code=code, name=name,
                type=stype, subject_type=scat,
                department_id=depts[dept_key].id,
                credits=3,
            )
            db.add(s)
            subjects[code] = s
        db.flush()
        print("✓ Created subjects")

        # ── 9. Batches ────────────────────────────────────────────────────────
        batches = {}
        for cname, course in courses.items():
            b = Batch(
                name=f"{cname} - 2024",
                code=f"B-{course.code}-2024",
                course_id=course.id,
                start_date=date(2024, 1, 8),
                end_date=date(2024, 11, 29),
            )
            db.add(b)
            batches[cname] = b
        db.flush()
        print("✓ Created batches")

        # ── 10. Classrooms ────────────────────────────────────────────────────
        classrooms = {}
        for i, cname in enumerate(courses.keys(), start=1):
            room = Classroom(
                name=f"Room {cname}",
                code=f"RM-{courses[cname].code}",
                capacity=40,
                location=f"Block {chr(64 + ((i - 1) // 5 + 1))}, Room {i}",
            )
            db.add(room)
            classrooms[cname] = room
        db.flush()
        print("✓ Created classrooms")

        # ── 11. Timings ───────────────────────────────────────────────────────
        timing_defs = [
            ("Period 1", time(7, 30), time(8, 30)),
            ("Period 2", time(8, 30), time(9, 30)),
            ("Period 3", time(9, 30), time(10, 30)),
            ("Period 4", time(10, 30), time(11, 30)),
            ("Period 5", time(11, 30), time(12, 30)),
            ("Period 6", time(13, 0),  time(14, 0)),
            ("Period 7", time(14, 0),  time(15, 0)),
            ("Period 8", time(15, 0),  time(16, 0)),
        ]
        timings = []
        for name, st, et in timing_defs:
            t = Timing(name=name, start_time=st, end_time=et)
            db.add(t)
            timings.append(t)
        db.flush()
        print("✓ Created timings")

        # ── 12. FeesTerm ──────────────────────────────────────────────────────
        fees_term = FeesTerm(name="Standard Term Fees", code="STF-2024")
        db.add(fees_term)
        db.flush()

        term_line_defs = [
            ("Term 1 Fees", date(2024, 1, 31), [("Tuition Fee", 12000), ("Activity Fee", 1500), ("Lunch Fee", 3000)]),
            ("Term 2 Fees", date(2024, 5, 15), [("Tuition Fee", 12000), ("Activity Fee", 1500), ("Lunch Fee", 3000)]),
            ("Term 3 Fees", date(2024, 9, 15), [("Tuition Fee", 12000), ("Activity Fee", 1500), ("Lunch Fee", 3000)]),
        ]
        fees_term_lines = []
        for line_name, due_dt, elements in term_line_defs:
            tl = FeesTermLine(
                term_id=fees_term.id,
                name=line_name,
                due_date=due_dt,
                amount=sum(e[1] for e in elements),
            )
            db.add(tl)
            db.flush()
            for ename, eamt in elements:
                db.add(FeesElement(term_line_id=tl.id, name=ename, amount=eamt))
            fees_term_lines.append(tl)
        db.flush()
        print("✓ Created fees term with lines and elements")

        # ── 13. HostelBlock ───────────────────────────────────────────────────
        boys_block = HostelBlock(name="Boys Block", capacity=100)
        girls_block = HostelBlock(name="Girls Block", capacity=100)
        db.add_all([boys_block, girls_block])
        db.flush()

        # ── 14. HostelRoomType ────────────────────────────────────────────────
        rt_single = HostelRoomType(name="Single", monthly_fee=8000, capacity=1)
        rt_double = HostelRoomType(name="Double", monthly_fee=5000, capacity=2)
        rt_dorm   = HostelRoomType(name="Dormitory", monthly_fee=3000, capacity=8)
        db.add_all([rt_single, rt_double, rt_dorm])
        db.flush()
        print("✓ Created hostel blocks and room types")

        # ── 15. HostelRooms ───────────────────────────────────────────────────
        hostel_rooms = []
        room_types_cycle = [rt_single, rt_double, rt_dorm]
        for i in range(1, 21):
            block = boys_block if i <= 10 else girls_block
            rtype = room_types_cycle[(i - 1) % 3]
            room = HostelRoom(
                name=f"Room {i:03d}",
                block_id=block.id,
                room_type_id=rtype.id,
                capacity=rtype.capacity,
                state="available",
            )
            db.add(room)
            hostel_rooms.append(room)
        db.flush()
        print("✓ Created 20 hostel rooms")

        # ── 16. Vehicles ──────────────────────────────────────────────────────
        vehicle_data = [
            ("School Bus 1", "KCA 123A", "Kamau Njoroge", "0712345678"),
            ("School Bus 2", "KBZ 456B", "Otieno Omondi", "0723456789"),
            ("School Bus 3", "KDA 789C", "Wekesa Simiyu", "0734567890"),
            ("School Bus 4", "KDB 321D", "Mutua Musyoka", "0745678901"),
            ("School Bus 5", "KDC 654E", "Korir Kipchoge", "0756789012"),
        ]
        vehicles = []
        for name, reg, driver, phone in vehicle_data:
            v = Vehicle(name=name, registration_number=reg, capacity=50,
                        driver_name=driver, driver_phone=phone)
            db.add(v)
            vehicles.append(v)
        db.flush()
        print("✓ Created 5 vehicles")

        # ── 17. TransportRoutes ───────────────────────────────────────────────
        route_defs = [
            ("Nairobi CBD Route",  "Nairobi CBD",  "School", [("Nairobi CBD", "06:30"), ("University Way", "06:45"), ("School Gate", "07:15")]),
            ("Westlands Route",    "Westlands",    "School", [("Westlands Roundabout", "06:35"), ("Parklands", "06:50"), ("School Gate", "07:15")]),
            ("Eastleigh Route",    "Eastleigh",    "School", [("Eastleigh 1st Ave", "06:30"), ("Pangani", "06:50"), ("School Gate", "07:20")]),
            ("Karen Route",        "Karen",        "School", [("Karen Shopping Centre", "06:20"), ("Langata Road", "06:45"), ("School Gate", "07:15")]),
            ("Kibera Route",       "Kibera",       "School", [("Kibera Drive", "06:25"), ("Olympic Estate", "06:45"), ("School Gate", "07:15")]),
        ]
        transport_routes = []
        route_stops_map = {}
        for idx, (rname, start, end, stops) in enumerate(route_defs):
            route = TransportRoute(
                name=rname, vehicle_id=vehicles[idx].id,
                start_point=start, end_point=end,
            )
            db.add(route)
            db.flush()
            stop_objs = []
            for seq, (sname, ptime) in enumerate(stops, start=1):
                stop = TransportRouteStop(
                    route_id=route.id, name=sname,
                    sequence=seq, pickup_time=ptime,
                )
                db.add(stop)
                stop_objs.append(stop)
            db.flush()
            transport_routes.append(route)
            route_stops_map[route.id] = stop_objs
        print("✓ Created 5 transport routes with stops")

        # ── 18. MediaType ─────────────────────────────────────────────────────
        media_types = {}
        for mt_name in ["Book", "Journal", "Magazine", "DVD"]:
            mt = MediaType(name=mt_name)
            db.add(mt)
            media_types[mt_name] = mt
        db.flush()

        # ── 19. Publishers ────────────────────────────────────────────────────
        publisher_names = [
            "Kenya Literature Bureau",
            "Longhorn Publishers",
            "Oxford University Press Kenya",
            "Jomo Kenyatta Foundation",
            "Storymoja",
        ]
        publishers = []
        for pname in publisher_names:
            p = Publisher(name=pname)
            db.add(p)
            publishers.append(p)
        db.flush()

        # ── 20. Authors ───────────────────────────────────────────────────────
        author_names = [
            "Ngugi wa Thiong'o", "Grace Ogot", "Meja Mwangi", "Marjorie Oludhe Macgoye",
            "Wahome Mutahi", "Micere Githae Mugo", "John Ruganda", "Rebeka Njau",
            "Francis Imbuga", "David Maillu",
        ]
        authors = []
        for aname in author_names:
            a = Author(name=aname, bio=f"Kenyan author: {aname}")
            db.add(a)
            authors.append(a)
        db.flush()

        # ── 21. LibraryTags ───────────────────────────────────────────────────
        tag_names = ["Mathematics", "Science", "Literature", "History", "Geography",
                     "Technology", "Arts", "Health", "Agriculture", "Languages"]
        lib_tags = []
        for tname in tag_names:
            t = LibraryTag(name=tname)
            db.add(t)
            lib_tags.append(t)
        db.flush()
        print("✓ Created media types, publishers, authors, library tags")

        # ── 22. Media (50 books) ──────────────────────────────────────────────
        book_titles = [
            ("CBC Mathematics Grade 1", "GR1", "Mathematics"),
            ("CBC Mathematics Grade 2", "GR2", "Mathematics"),
            ("CBC Mathematics Grade 3", "GR3", "Mathematics"),
            ("CBC Mathematics Grade 4", "GR4", "Mathematics"),
            ("CBC Mathematics Grade 5", "GR5", "Mathematics"),
            ("CBC Mathematics Grade 6", "GR6", "Mathematics"),
            ("CBC Mathematics Grade 7", "GR7", "Mathematics"),
            ("CBC English Grade 1", "GR1", "English"),
            ("CBC English Grade 2", "GR2", "English"),
            ("CBC English Grade 3", "GR3", "English"),
            ("CBC English Grade 4", "GR4", "English"),
            ("CBC English Grade 5", "GR5", "English"),
            ("CBC Kiswahili Grade 1", "GR1", "Kiswahili"),
            ("CBC Kiswahili Grade 2", "GR2", "Kiswahili"),
            ("CBC Kiswahili Grade 3", "GR3", "Kiswahili"),
            ("CBC Kiswahili Grade 4", "GR4", "Kiswahili"),
            ("CBC Science & Technology Grade 4", "GR4", "Science"),
            ("CBC Science & Technology Grade 5", "GR5", "Science"),
            ("CBC Science & Technology Grade 6", "GR6", "Science"),
            ("CBC Social Studies Grade 4", "GR4", "Social Studies"),
            ("CBC Social Studies Grade 5", "GR5", "Social Studies"),
            ("CBC Social Studies Grade 6", "GR6", "Social Studies"),
            ("CBC Agriculture Grade 7", "GR7", "Agriculture"),
            ("CBC Agriculture Grade 8", "GR8", "Agriculture"),
            ("CBC Agriculture Grade 9", "GR9", "Agriculture"),
            ("CBC Pre-Technical Studies Grade 7", "GR7", "Technology"),
            ("CBC Pre-Technical Studies Grade 8", "GR8", "Technology"),
            ("CBC Business Studies Grade 10", "GR10", "Business"),
            ("CBC Business Studies Grade 11", "GR11", "Business"),
            ("CBC Computer Science Grade 10", "GR10", "Technology"),
            ("CBC Computer Science Grade 11", "GR11", "Technology"),
            ("CBC Computer Science Grade 12", "GR12", "Technology"),
            ("Weep Not Child - Ngugi wa Thiong'o", "GR10", "Literature"),
            ("The River Between - Ngugi wa Thiong'o", "GR11", "Literature"),
            ("A Grain of Wheat - Ngugi wa Thiong'o", "GR12", "Literature"),
            ("The Promised Land - Grace Ogot", "GR10", "Literature"),
            ("Going Down River Road - Meja Mwangi", "GR11", "Literature"),
            ("Coming to Birth - Marjorie Oludhe Macgoye", "GR12", "Literature"),
            ("Whispers - Wahome Mutahi", "GR9", "Literature"),
            ("The Trial of Dedan Kimathi - Ngugi & Micere", "GR12", "Literature"),
            ("Betrayal in the City - Francis Imbuga", "GR11", "Literature"),
            ("Kenya Geography Handbook", "GR8", "Geography"),
            ("East African History", "GR7", "History"),
            ("Kenya History & Government Grade 10", "GR10", "History"),
            ("Kenya History & Government Grade 11", "GR11", "History"),
            ("Kenya History & Government Grade 12", "GR12", "History"),
            ("CBC Life Skills Grade 7", "GR7", "Life Skills"),
            ("CBC Life Skills Grade 8", "GR8", "Life Skills"),
            ("CBC Physical Education Grade 4", "GR4", "Health"),
            ("CBC Environmental Activities PP1", "PP1", "Environment"),
        ]
        media_list = []
        for idx, (title, grade, subject_area) in enumerate(book_titles, start=1):
            m = Media(
                name=title,
                isbn=f"978-9966-{idx:04d}-{random.randint(0,9)}",
                internal_code=f"LIB-{idx:04d}",
                edition="1st Edition",
                media_type_id=media_types["Book"].id,
                publisher_id=random.choice(publishers).id,
                grade_level=grade,
                subject_area=subject_area,
                resource_format="book",
                total_copies=random.randint(3, 10),
                available_copies=random.randint(2, 5),
            )
            db.add(m)
            media_list.append(m)
        db.flush()
        # Assign authors and tags to books
        for m in media_list:
            m.authors.append(random.choice(authors))
            m.tags.append(random.choice(lib_tags))
        db.flush()
        print("✓ Created 50 library books")

        # ── 23. AchievementType ───────────────────────────────────────────────
        ach_types = {}
        for aname in ["Academic Excellence", "Sports", "Arts", "Community Service"]:
            at = AchievementType(name=aname)
            db.add(at)
            ach_types[aname] = at
        db.flush()

        # ── 24. ActivityType ──────────────────────────────────────────────────
        act_types = {}
        for aname in ["Sports", "Music", "Drama", "Science Club", "Debate"]:
            at = ActivityType(name=aname)
            db.add(at)
            act_types[aname] = at
        db.flush()

        # ── 25. EventType ─────────────────────────────────────────────────────
        evt_types = {}
        for ename in ["Academic", "Sports", "Cultural", "Community"]:
            et = EventType(name=ename)
            db.add(et)
            evt_types[ename] = et
        db.flush()

        # ── 26. DisciplineAction ──────────────────────────────────────────────
        disc_actions = {}
        for dname in ["Warning", "Suspension", "Counselling", "Parent Meeting"]:
            da = DisciplineAction(name=dname)
            db.add(da)
            disc_actions[dname] = da
        db.flush()

        # ── 27. InventoryCategory ─────────────────────────────────────────────
        inv_cats = {}
        for iname in ["Stationery", "Sports Equipment", "Lab Equipment", "Furniture"]:
            ic = InventoryCategory(name=iname)
            db.add(ic)
            inv_cats[iname] = ic
        db.flush()

        # ── 28. ScholarshipType ───────────────────────────────────────────────
        schol_types = {}
        for sname, amt in [
            ("Government Bursary", 15000),
            ("CDF Bursary", 10000),
            ("School Bursary", 8000),
            ("Needy Fund", 5000),
        ]:
            st = ScholarshipType(name=sname, amount=amt)
            db.add(st)
            schol_types[sname] = st
        db.flush()

        # ── 29. BlogCategory ──────────────────────────────────────────────────
        blog_cats = {}
        for bname in ["Academic", "Sports", "Events", "Announcements"]:
            bc = BlogCategory(name=bname)
            db.add(bc)
            blog_cats[bname] = bc
        db.flush()

        # ── 30. FoodCategory ──────────────────────────────────────────────────
        food_cats = {}
        for fname in ["Breakfast", "Lunch", "Snacks"]:
            fc = FoodCategory(name=fname)
            db.add(fc)
            food_cats[fname] = fc
        db.flush()

        # ── 31. GradingConfig (CBC) ───────────────────────────────────────────
        grading_config = GradingConfig(name="CBC Grading")
        db.add(grading_config)
        db.flush()
        cbc_grades = [
            ("EE", 80, 100, 4.0),
            ("ME", 60, 79,  3.0),
            ("AE", 40, 59,  2.0),
            ("BE", 0,  39,  1.0),
        ]
        for gname, gmin, gmax, gp in cbc_grades:
            db.add(GradingRule(config_id=grading_config.id, name=gname,
                               min_marks=gmin, max_marks=gmax, grade_point=gp))
        db.flush()

        # ── 32. ParentRelationship ────────────────────────────────────────────
        parent_rels = {}
        for rname in ["Mother", "Father", "Guardian"]:
            pr = ParentRelationship(name=rname)
            db.add(pr)
            parent_rels[rname] = pr
        db.flush()
        print("✓ Created lookup data (achievement types, activity types, event types, etc.)")

        # ── 33. Teachers (100) ────────────────────────────────────────────────
        teacher_users = []
        teacher_records = []
        dept_list = list(depts.values())
        for i in range(1, 101):
            first, gender = pick_name(i, FIRST_NAMES_MALE, FIRST_NAMES_FEMALE)
            last = random.choice(LAST_NAMES)
            emp_id = f"TCH{i:03d}"
            email = make_email(first, last, f".t{i}")
            u = User(
                email=email,
                username=f"teacher{i:03d}",
                hashed_password=get_password_hash("Teacher@1234"),
                first_name=first,
                last_name=last,
                role=UserRole.TEACHER,
                is_active=True,
            )
            db.add(u)
            db.flush()
            t = Teacher(
                user_id=u.id,
                employee_id=emp_id,
                first_name=first,
                last_name=last,
                gender=gender,
                date_of_birth=date(random.randint(1970, 1990), random.randint(1, 12), random.randint(1, 28)),
                blood_group=random.choice(BLOOD_GROUPS),
                nationality="Kenyan",
                phone=f"07{random.randint(10000000, 99999999)}",
                mobile=f"07{random.randint(10000000, 99999999)}",
                email=email,
                qualification="Bachelor of Education",
                specialization=random.choice(["Mathematics", "English", "Science", "Kiswahili", "Social Studies"]),
                experience_years=random.randint(1, 20),
                join_date=date(random.randint(2010, 2023), random.randint(1, 12), 1),
                main_department_id=random.choice(dept_list).id,
            )
            db.add(t)
            teacher_users.append(u)
            teacher_records.append(t)
        db.flush()
        print("✓ Created 100 teachers")

        # ── 34. Staff Users (100) ─────────────────────────────────────────────
        for i in range(1, 101):
            first, gender = pick_name(i, FIRST_NAMES_MALE, FIRST_NAMES_FEMALE)
            last = random.choice(LAST_NAMES)
            email = make_email(first, last, f".s{i}")
            u = User(
                email=email,
                username=f"staff{i:03d}",
                hashed_password=get_password_hash("Staff@1234"),
                first_name=first,
                last_name=last,
                role=UserRole.STAFF,
                is_active=True,
            )
            db.add(u)
        db.flush()
        print("✓ Created 100 staff users")

        # ── 35. Students (100) ────────────────────────────────────────────────
        student_users = []
        student_records = []
        cat_list = list(categories.values())
        kenyan_cities = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
                         "Thika", "Machakos", "Nyeri", "Meru", "Kakamega"]
        for i in range(1, 101):
            first, gender = pick_name(i, FIRST_NAMES_MALE, FIRST_NAMES_FEMALE)
            last = random.choice(LAST_NAMES)
            adm_no = f"KEN2024/{i:03d}"
            gr_no = f"GR{i:04d}"
            email = make_email(first, last, f".st{i}")
            u = User(
                email=email,
                username=f"student{i:03d}",
                hashed_password=get_password_hash("Student@1234"),
                first_name=first,
                last_name=last,
                role=UserRole.STUDENT,
                is_active=True,
            )
            db.add(u)
            db.flush()
            s = Student(
                user_id=u.id,
                admission_number=adm_no,
                gr_no=gr_no,
                first_name=first,
                last_name=last,
                gender=gender,
                date_of_birth=date(random.randint(2008, 2018), random.randint(1, 12), random.randint(1, 28)),
                blood_group=random.choice(BLOOD_GROUPS),
                nationality="Kenyan",
                mobile=f"07{random.randint(10000000, 99999999)}",
                email=email,
                city=random.choice(kenyan_cities),
                country="Kenya",
                category_id=random.choice(cat_list).id,
                admission_date=date(2024, 1, 8),
                emergency_contact_name=f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}",
                emergency_contact_phone=f"07{random.randint(10000000, 99999999)}",
                emergency_contact_relation="Parent",
            )
            db.add(s)
            student_users.append(u)
            student_records.append(s)
        db.flush()
        print("✓ Created 100 students")

        # ── 36. Parents (20) ──────────────────────────────────────────────────
        parent_records = []
        rel_list = list(parent_rels.values())
        for i in range(1, 21):
            first, gender = pick_name(i, FIRST_NAMES_MALE, FIRST_NAMES_FEMALE)
            last = random.choice(LAST_NAMES)
            email = make_email(first, last, f".p{i}")
            u = User(
                email=email,
                username=f"parent{i:03d}",
                hashed_password=get_password_hash("Parent@1234"),
                first_name=first,
                last_name=last,
                role=UserRole.PARENT,
                is_active=True,
            )
            db.add(u)
            db.flush()
            p = Parent(
                user_id=u.id,
                first_name=first,
                last_name=last,
                email=email,
                mobile=f"07{random.randint(10000000, 99999999)}",
                relationship_id=random.choice(rel_list).id,
            )
            db.add(p)
            db.flush()
            # Link each parent to ~5 students
            start_idx = (i - 1) * 5
            for s in student_records[start_idx:start_idx + 5]:
                p.students.append(s)
            parent_records.append(p)
        db.flush()
        print("✓ Created 20 parents linked to students")

        # ── 37. Enroll students into courses ──────────────────────────────────
        # Distribute ~7-8 students per grade level (14 grades, 100 students)
        course_list = list(courses.values())
        enrollments = []
        for idx, student in enumerate(student_records):
            course = course_list[idx % len(course_list)]
            batch = batches[course.name]
            sc = StudentCourse(
                student_id=student.id,
                course_id=course.id,
                batch_id=batch.id,
                roll_number=f"ROLL-{course.code}-{idx + 1:03d}",
                academic_year_id=ay2024.id,
                academic_term_id=terms["T1-2024"].id,
                state="running",
                fees_start_date=date(2024, 1, 8),
            )
            db.add(sc)
            enrollments.append((student, course, batch, sc))
        db.flush()
        print("✓ Enrolled 100 students into courses")

        # ── 38. Assign subjects to courses ────────────────────────────────────
        # Map grade levels to relevant subjects
        pp_subjects = [subjects["ENV"], subjects["HYG"], subjects["CAC"], subjects["PHE"], subjects["ENG"], subjects["KIS"]]
        lp_subjects = [subjects["MATH"], subjects["ENG"], subjects["KIS"], subjects["CAC"], subjects["PHE"], subjects["ENV"]]
        up_subjects = [subjects["MATH"], subjects["ENG"], subjects["KIS"], subjects["SCI"], subjects["SST"], subjects["CRE"], subjects["PHE"], subjects["MUS"]]
        js_subjects = [subjects["MATH"], subjects["ENG"], subjects["KIS"], subjects["SCI"], subjects["SST"], subjects["AGR"], subjects["PTS"], subjects["LSK"], subjects["PA"]]
        ss_subjects = [subjects["MATH"], subjects["ENG"], subjects["KIS"], subjects["SCI"], subjects["SST"], subjects["BST"], subjects["CS"], subjects["AGR"]]

        grade_subject_map = {
            "PP1": pp_subjects, "PP2": pp_subjects,
            "Grade 1": lp_subjects, "Grade 2": lp_subjects, "Grade 3": lp_subjects,
            "Grade 4": up_subjects, "Grade 5": up_subjects, "Grade 6": up_subjects,
            "Grade 7": js_subjects, "Grade 8": js_subjects, "Grade 9": js_subjects,
            "Grade 10": ss_subjects, "Grade 11": ss_subjects, "Grade 12": ss_subjects,
        }
        for cname, course in courses.items():
            subj_list = grade_subject_map.get(cname, lp_subjects)
            for subj in subj_list:
                if subj not in course.subjects:
                    course.subjects.append(subj)
        db.flush()
        print("✓ Assigned subjects to courses")

        # ── 39. Assign subjects to teachers ───────────────────────────────────
        subj_list_all = list(subjects.values())
        for i, teacher in enumerate(teacher_records):
            # Each teacher gets 2-3 subjects
            assigned = random.sample(subj_list_all, min(2, len(subj_list_all)))
            for subj in assigned:
                if subj not in teacher.subjects:
                    teacher.subjects.append(subj)
        db.flush()
        print("✓ Assigned subjects to teachers")

        # ── 40. AttendanceRegisters ───────────────────────────────────────────
        att_registers = {}
        for cname, course in courses.items():
            batch = batches[cname]
            reg = AttendanceRegister(
                name=f"Attendance Register - {cname} 2024",
                course_id=course.id,
                batch_id=batch.id,
                academic_year_id=ay2024.id,
                academic_term_id=terms["T1-2024"].id,
            )
            db.add(reg)
            att_registers[cname] = reg
        db.flush()
        print("✓ Created 14 attendance registers")

        # ── 41. AttendanceSheets + Lines ──────────────────────────────────────
        # Build course -> students map
        course_students_map = {}
        for student, course, batch, sc in enrollments:
            cname = course.name
            if cname not in course_students_map:
                course_students_map[cname] = []
            course_students_map[cname].append(student)

        base_date = date(2024, 1, 15)
        att_statuses = [AttendanceStatus.PRESENT, AttendanceStatus.PRESENT,
                        AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.LATE]
        for cname, reg in att_registers.items():
            teacher = random.choice(teacher_records)
            students_in_course = course_students_map.get(cname, [])
            for day_offset in range(5):
                sheet_date = base_date + timedelta(days=day_offset)
                sheet = AttendanceSheet(
                    name=f"{cname} - {sheet_date}",
                    register_id=reg.id,
                    attendance_date=sheet_date,
                    faculty_id=teacher.id,
                    state=AttendanceSheetState.DONE,
                )
                db.add(sheet)
                db.flush()
                for student in students_in_course:
                    line = AttendanceLine(
                        sheet_id=sheet.id,
                        student_id=student.id,
                        status=random.choice(att_statuses),
                    )
                    db.add(line)
        db.flush()
        print("✓ Created attendance sheets and lines")

        # ── 42. ExamSessions ──────────────────────────────────────────────────
        exam_sessions = {}
        for cname, course in courses.items():
            batch = batches[cname]
            es = ExamSession(
                name=f"Term 1 2024 Exams - {cname}",
                course_id=course.id,
                batch_id=batch.id,
                academic_year_id=ay2024.id,
                academic_term_id=terms["T1-2024"].id,
                start_date=datetime(2024, 3, 18, 8, 0),
                end_date=datetime(2024, 3, 22, 17, 0),
                state="scheduled",
            )
            db.add(es)
            exam_sessions[cname] = es
        db.flush()
        print("✓ Created exam sessions")

        # ── 43. Exams (3 per session) ─────────────────────────────────────────
        exam_subject_map = {
            "PP1": [subjects["ENV"], subjects["ENG"], subjects["CAC"]],
            "PP2": [subjects["ENV"], subjects["ENG"], subjects["CAC"]],
            "Grade 1": [subjects["MATH"], subjects["ENG"], subjects["KIS"]],
            "Grade 2": [subjects["MATH"], subjects["ENG"], subjects["KIS"]],
            "Grade 3": [subjects["MATH"], subjects["ENG"], subjects["KIS"]],
            "Grade 4": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 5": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 6": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 7": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 8": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 9": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 10": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 11": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
            "Grade 12": [subjects["MATH"], subjects["ENG"], subjects["SCI"]],
        }
        all_exams = {}  # cname -> list of Exam
        exam_counter = 1
        for cname, session in exam_sessions.items():
            course = courses[cname]
            batch = batches[cname]
            exam_subjs = exam_subject_map.get(cname, [subjects["MATH"], subjects["ENG"], subjects["SCI"]])
            exams_for_course = []
            for day_off, subj in enumerate(exam_subjs):
                exam_dt = datetime(2024, 3, 18 + day_off, 8, 0)
                exam = Exam(
                    name=f"{subj.name} Exam - {cname} T1 2024",
                    exam_code=f"EX-{course.code}-{subj.code}-{exam_counter:04d}",
                    session_id=session.id,
                    course_id=course.id,
                    batch_id=batch.id,
                    subject_id=subj.id,
                    start_time=exam_dt,
                    end_time=exam_dt + timedelta(hours=2),
                    total_marks=100,
                    min_marks=40,
                    state=ExamState.RESULT_UPDATED,
                )
                db.add(exam)
                exams_for_course.append(exam)
                exam_counter += 1
            all_exams[cname] = exams_for_course
        db.flush()
        print("✓ Created exams (3 per course)")

        # ── 44. ExamAttendees ─────────────────────────────────────────────────
        for cname, exams_list in all_exams.items():
            students_in_course = course_students_map.get(cname, [])
            for exam in exams_list:
                for student in students_in_course:
                    marks = round(random.uniform(40, 100), 1)
                    state = "pass" if marks >= 40 else "fail"
                    db.add(ExamAttendees(
                        exam_id=exam.id,
                        student_id=student.id,
                        marks=marks,
                        state=state,
                    ))
        db.flush()
        print("✓ Created exam attendees with marks")

        # ── 45. Assignments (3 per course) ────────────────────────────────────
        assignment_counter = 1
        all_assignments = {}  # cname -> list of Assignment
        for cname, course in courses.items():
            batch = batches[cname]
            teacher = random.choice(teacher_records)
            subj_pool = grade_subject_map.get(cname, lp_subjects)
            chosen_subjs = random.sample(subj_pool, min(3, len(subj_pool)))
            assignments_for_course = []
            for k, subj in enumerate(chosen_subjs):
                issued = date(2024, 1, 15) + timedelta(days=k * 7)
                due = issued + timedelta(days=7)
                asgn = Assignment(
                    name=f"{subj.name} Assignment {k + 1} - {cname}",
                    course_id=course.id,
                    batch_id=batch.id,
                    subject_id=subj.id,
                    faculty_id=teacher.id,
                    issued_date=issued,
                    submission_date=due,
                    total_marks=30,
                    description=f"Complete the {subj.name} assignment for {cname}.",
                    state=AssignmentState.PUBLISHED,
                )
                db.add(asgn)
                assignments_for_course.append(asgn)
                assignment_counter += 1
            all_assignments[cname] = assignments_for_course
        db.flush()

        # ── 46. AssignmentSubmissions ─────────────────────────────────────────
        for cname, asgn_list in all_assignments.items():
            students_in_course = course_students_map.get(cname, [])
            for asgn in asgn_list:
                for student in students_in_course:
                    sub = AssignmentSubmission(
                        assignment_id=asgn.id,
                        student_id=student.id,
                        submission_date=asgn.submission_date,
                        marks=round(random.uniform(15, 30), 1),
                        state="graded",
                    )
                    db.add(sub)
        db.flush()
        print("✓ Created assignments and submissions")

        # ── 47. StudentFeeInvoices (3 per student = 300 total) ────────────────
        term_codes = ["T1-2024", "T2-2024", "T3-2024"]
        all_invoices = []
        for student, course, batch, sc in enrollments:
            for tcode in term_codes:
                term_obj = terms[tcode]
                invoice = StudentFeeInvoice(
                    student_id=student.id,
                    course_id=course.id,
                    academic_year_id=ay2024.id,
                    academic_term_id=term_obj.id,
                    fees_term_id=fees_term.id,
                    total_amount=16500.0,
                    paid_amount=0.0,
                    due_date=term_obj.start_date + timedelta(days=30),
                    state=PaymentState.PENDING,
                )
                db.add(invoice)
                all_invoices.append(invoice)
        db.flush()
        print("✓ Created 300 fee invoices")

        # ── 48. FeePayments (70% of invoices) ─────────────────────────────────
        payment_methods = ["mpesa", "cash", "bank", "mpesa", "mpesa"]  # weighted toward mpesa
        paid_count = 0
        for invoice in all_invoices:
            if random.random() < 0.70:
                method = random.choice(payment_methods)
                ref = f"REF{random.randint(100000, 999999)}"
                payment = FeePayment(
                    invoice_id=invoice.id,
                    amount=invoice.total_amount,
                    payment_date=invoice.due_date - timedelta(days=random.randint(0, 10)),
                    payment_method=method,
                    reference=ref,
                    note=f"Payment via {method.upper()}",
                )
                db.add(payment)
                invoice.paid_amount = invoice.total_amount
                invoice.state = PaymentState.PAID
                paid_count += 1
        db.flush()
        print(f"✓ Created {paid_count} fee payments (70% of invoices)")

        # ── 49. HostelAllocations (30 students) ───────────────────────────────
        hostel_students = random.sample(student_records, 30)
        for idx, student in enumerate(hostel_students):
            room = hostel_rooms[idx % len(hostel_rooms)]
            alloc = HostelAllocation(
                student_id=student.id,
                room_id=room.id,
                academic_year_id=ay2024.id,
                check_in_date=date(2024, 1, 8),
                check_out_date=date(2024, 11, 29),
                monthly_fee=room.room_type.monthly_fee,
                state=HostelAllocationState.CONFIRMED,
            )
            db.add(alloc)
        db.flush()
        print("✓ Created 30 hostel allocations")

        # ── 50. StudentTransport (40 students) ────────────────────────────────
        transport_students = random.sample(student_records, 40)
        for idx, student in enumerate(transport_students):
            route = transport_routes[idx % len(transport_routes)]
            stops = route_stops_map[route.id]
            stop = random.choice(stops)
            db.add(StudentTransport(
                student_id=student.id,
                route_id=route.id,
                stop_id=stop.id,
                transport_type="both",
                academic_year_id=ay2024.id,
            ))
        db.flush()
        print("✓ Created 40 student transport assignments")

        # ── 51. MediaMovements (20 book issues) ───────────────────────────────
        lib_students = random.sample(student_records, 20)
        for idx, student in enumerate(lib_students):
            book = media_list[idx % len(media_list)]
            issue_dt = date(2024, 1, 20) + timedelta(days=idx)
            due_dt = issue_dt + timedelta(days=14)
            returned = idx % 3 != 0  # ~2/3 returned
            mm = MediaMovement(
                media_id=book.id,
                student_id=student.id,
                issue_date=issue_dt,
                due_date=due_dt,
                return_date=due_dt - timedelta(days=2) if returned else None,
                state=MediaMovementState.RETURNED if returned else MediaMovementState.ISSUED,
            )
            db.add(mm)
        db.flush()
        print("✓ Created 20 library media movements")

        db.commit()
        print("\n✅ Kenya CBC seed data committed successfully!")
        print("   Admin login: admin@kenyacbc.ac.ke / Admin@1234")
        print("   Teachers:    teacher001..teacher100 / Teacher@1234")
        print("   Students:    student001..student100 / Student@1234")
        print("   Parents:     parent001..parent020   / Parent@1234")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seed failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
