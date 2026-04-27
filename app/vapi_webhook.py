import logging
import re
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Patient
from app.schemas import PatientCreate
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter()


def normalize_phone(raw: str) -> str:
    """Strip non-digits, return 10-digit string."""
    return re.sub(r"\D", "", raw or "")


@router.post("/vapi/webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Vapi calls this endpoint when the agent invokes a tool (function call).
    We handle two tools:
      - check_existing_patient  → look up by phone number
      - save_patient            → persist the collected record
    """
    body = await request.json()
    logger.info("Vapi webhook payload: %s", body)

    message = body.get("message", {})
    msg_type = message.get("type")

    # ── tool / function call ────────────────────────────────────────────────
    if msg_type == "tool-calls":
        tool_calls = message.get("toolCalls", [])
        results = []

        for tc in tool_calls:
            tool_name = tc.get("function", {}).get("name")
            args      = tc.get("function", {}).get("arguments", {})
            tool_id   = tc.get("id")

            if tool_name == "check_existing_patient":
                result = handle_check_patient(args, db)
            elif tool_name == "save_patient":
                result = handle_save_patient(args, db)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            results.append({
                "toolCallId": tool_id,
                "result": result
            })

        return JSONResponse({"results": results})

    # ── end-of-call summary (log only) ─────────────────────────────────────
    if msg_type == "end-of-call-report":
        logger.info("Call ended. Summary: %s", message.get("summary"))
        return JSONResponse({"received": True})

    return JSONResponse({"received": True})


# ── Tool handlers ────────────────────────────────────────────────────────────

def handle_check_patient(args: dict, db: Session) -> dict:
    phone = normalize_phone(args.get("phone_number", ""))
    if not phone:
        return {"found": False}

    patient = (
        db.query(Patient)
        .filter(Patient.phone_number == phone, Patient.deleted_at == None)
        .first()
    )

    if patient:
        logger.info("Returning caller found: %s %s", patient.first_name, patient.last_name)
        return {
            "found": True,
            "patient_id":  patient.patient_id,
            "first_name":  patient.first_name,
            "last_name":   patient.last_name,
        }
    return {"found": False}


def handle_save_patient(args: dict, db: Session) -> dict:
    """
    Validate and persist a new patient, or update if patient_id provided.
    Logs the full payload to stdout for observability.
    """
    logger.info("Saving patient payload: %s", args)

    # Normalize phone fields
    for field in ("phone_number", "emergency_contact_phone"):
        if args.get(field):
            args[field] = normalize_phone(args[field])

    patient_id = args.pop("patient_id", None)

    try:
        if patient_id:
            # ── UPDATE existing patient ─────────────────────────────────
            patient = db.query(Patient).filter(
                Patient.patient_id == patient_id,
                Patient.deleted_at == None
            ).first()

            if not patient:
                return {"success": False, "error": "Patient not found for update."}

            for key, value in args.items():
                if hasattr(patient, key) and value is not None:
                    setattr(patient, key, value)

            patient.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(patient)
            logger.info("Updated patient %s", patient.patient_id)
            return {
                "success":    True,
                "action":     "updated",
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
            }
        else:
            # ── CREATE new patient ──────────────────────────────────────
            validated = PatientCreate(**args)
            new_patient = Patient(
                patient_id=str(uuid.uuid4()),
                **validated.model_dump()
            )
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            logger.info("Created patient %s", new_patient.patient_id)
            return {
                "success":    True,
                "action":     "created",
                "patient_id": new_patient.patient_id,
                "first_name": new_patient.first_name,
            }

    except Exception as e:
        db.rollback()
        logger.error("Failed to save patient: %s", str(e))
        return {"success": False, "error": str(e)}
