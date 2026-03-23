from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, require_teacher
from app.api.crud import get_one, get_all, create_obj, update_obj, delete_obj
from app.models.attendance import AttendanceRegister, AttendanceSheet, AttendanceLine
from app.schemas.attendance import (
    AttendanceRegisterCreate, AttendanceRegisterUpdate, AttendanceRegisterOut,
    AttendanceSheetCreate, AttendanceSheetUpdate, AttendanceSheetOut,
    AttendanceLineCreate, AttendanceLineOut,
)

router = APIRouter()


# ── Registers ─────────────────────────────────────────────────────────────────
@router.get("/registers/", response_model=List[AttendanceRegisterOut], tags=["Attendance"])
def list_registers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    return get_all(db, AttendanceRegister, skip, limit)

@router.post("/registers/", response_model=AttendanceRegisterOut, status_code=201, tags=["Attendance"])
def create_register(data: AttendanceRegisterCreate, db: Session = Depends(get_db),
                    _=Depends(require_teacher)):
    return create_obj(db, AttendanceRegister, data.model_dump())

@router.get("/registers/{id}", response_model=AttendanceRegisterOut, tags=["Attendance"])
def get_register(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, AttendanceRegister, id)
    if not obj: raise HTTPException(404, "Register not found")
    return obj

@router.put("/registers/{id}", response_model=AttendanceRegisterOut, tags=["Attendance"])
def update_register(id: int, data: AttendanceRegisterUpdate, db: Session = Depends(get_db),
                    _=Depends(require_teacher)):
    obj = get_one(db, AttendanceRegister, id)
    if not obj: raise HTTPException(404, "Register not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.delete("/registers/{id}", status_code=204, tags=["Attendance"])
def delete_register(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, AttendanceRegister, id)
    if not obj: raise HTTPException(404, "Register not found")
    delete_obj(db, obj)


# ── Sheets ────────────────────────────────────────────────────────────────────
@router.get("/sheets/", response_model=List[AttendanceSheetOut], tags=["Attendance"])
def list_sheets(skip: int = 0, limit: int = 100, register_id: int = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(AttendanceSheet)
    if register_id:
        q = q.filter(AttendanceSheet.register_id == register_id)
    return q.offset(skip).limit(limit).all()

@router.post("/sheets/", response_model=AttendanceSheetOut, status_code=201, tags=["Attendance"])
def create_sheet(data: AttendanceSheetCreate, db: Session = Depends(get_db),
                 _=Depends(require_teacher)):
    lines = data.lines or []
    payload = data.model_dump(exclude={"lines"})
    sheet = create_obj(db, AttendanceSheet, payload)
    for line in lines:
        create_obj(db, AttendanceLine, {**line.model_dump(), "sheet_id": sheet.id})
    db.refresh(sheet)
    return sheet

@router.get("/sheets/{id}", response_model=AttendanceSheetOut, tags=["Attendance"])
def get_sheet(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = get_one(db, AttendanceSheet, id)
    if not obj: raise HTTPException(404, "Sheet not found")
    return obj

@router.put("/sheets/{id}", response_model=AttendanceSheetOut, tags=["Attendance"])
def update_sheet(id: int, data: AttendanceSheetUpdate, db: Session = Depends(get_db),
                 _=Depends(require_teacher)):
    obj = get_one(db, AttendanceSheet, id)
    if not obj: raise HTTPException(404, "Sheet not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))

@router.post("/sheets/{id}/submit", response_model=AttendanceSheetOut, tags=["Attendance"])
def submit_sheet(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, AttendanceSheet, id)
    if not obj: raise HTTPException(404, "Sheet not found")
    return update_obj(db, obj, {"state": "done"})

@router.delete("/sheets/{id}", status_code=204, tags=["Attendance"])
def delete_sheet(id: int, db: Session = Depends(get_db), _=Depends(require_teacher)):
    obj = get_one(db, AttendanceSheet, id)
    if not obj: raise HTTPException(404, "Sheet not found")
    delete_obj(db, obj)


# ── Lines (individual student attendance) ─────────────────────────────────────
@router.get("/sheets/{sheet_id}/lines", response_model=List[AttendanceLineOut], tags=["Attendance"])
def list_lines(sheet_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(AttendanceLine).filter(AttendanceLine.sheet_id == sheet_id).all()

@router.put("/lines/{id}", response_model=AttendanceLineOut, tags=["Attendance"])
def update_line(id: int, data: AttendanceLineCreate, db: Session = Depends(get_db),
                _=Depends(require_teacher)):
    obj = db.query(AttendanceLine).filter(AttendanceLine.id == id).first()
    if not obj: raise HTTPException(404, "Line not found")
    return update_obj(db, obj, data.model_dump(exclude_unset=True))
