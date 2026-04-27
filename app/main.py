import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Patient
from app.schemas import PatientCreate, PatientUpdate, PatientResponse
from app.vapi_webhook import router as vapi_router

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── DB init ───────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CareCloud Voice Agent API",
    description="Patient registration system powered by a Voice AI agent.",
    version="1.0.0",
)

app.include_router(vapi_router)


# ── Helpers ───────────────────────────────────────────────────────────────────

def ok(data):
    return {"data": data, "error": None}

def err(msg: str, status: int = 400):
    return JSONResponse(status_code=status, content={"data": None, "error": msg})


# ── Seed data (runs once on startup) ─────────────────────────────────────────

@app.on_event("startup")
def seed_data():
    db = next(get_db())
    if db.query(Patient).count() == 0:
        seeds = [
            Patient(
                patient_id=str(uuid.uuid4()),
                first_name="Jane",
                last_name="Doe",
                date_of_birth="03/15/1985",
                sex="Female",
                phone_number="5551234567",
                email="jane.doe@example.com",
                address_line_1="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001",
                preferred_language="English",
            ),
            Patient(
                patient_id=str(uuid.uuid4()),
                first_name="John",
                last_name="Smith",
                date_of_birth="07/22/1972",
                sex="Male",
                phone_number="5559876543",
                address_line_1="456 Oak Ave",
                city="Los Angeles",
                state="CA",
                zip_code="90001",
                preferred_language="English",
            ),
        ]
        db.add_all(seeds)
        db.commit()
        logger.info("Seeded 2 demo patients.")
    db.close()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/patients")
def list_patients(
    last_name:     Optional[str] = Query(None),
    date_of_birth: Optional[str] = Query(None),
    phone_number:  Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Patient).filter(Patient.deleted_at == None)

    if last_name:
        query = query.filter(Patient.last_name.ilike(f"%{last_name}%"))
    if date_of_birth:
        query = query.filter(Patient.date_of_birth == date_of_birth)
    if phone_number:
        query = query.filter(Patient.phone_number == phone_number)

    patients = query.order_by(Patient.created_at.desc()).all()
    return ok([PatientResponse.model_validate(p).model_dump() for p in patients])


@app.get("/patients/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.deleted_at == None,
    ).first()

    if not patient:
        return err("Patient not found.", 404)

    return ok(PatientResponse.model_validate(patient).model_dump())


@app.post("/patients", status_code=201)
def create_patient(body: PatientCreate, db: Session = Depends(get_db)):
    try:
        patient = Patient(patient_id=str(uuid.uuid4()), **body.model_dump())
        db.add(patient)
        db.commit()
        db.refresh(patient)
        logger.info("Created patient %s %s [%s]", patient.first_name, patient.last_name, patient.patient_id)
        return ok(PatientResponse.model_validate(patient).model_dump())
    except Exception as e:
        db.rollback()
        logger.error("Create failed: %s", e)
        return err(str(e), 422)


@app.put("/patients/{patient_id}")
def update_patient(patient_id: str, body: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.deleted_at == None,
    ).first()

    if not patient:
        return err("Patient not found.", 404)

    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(patient, key, value)

    patient.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(patient)
    logger.info("Updated patient %s", patient_id)
    return ok(PatientResponse.model_validate(patient).model_dump())


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.deleted_at == None,
    ).first()

    if not patient:
        return err("Patient not found.", 404)

    patient.deleted_at = datetime.now(timezone.utc)
    db.commit()
    logger.info("Soft-deleted patient %s", patient_id)
    return ok({"message": f"Patient {patient_id} deleted."})
