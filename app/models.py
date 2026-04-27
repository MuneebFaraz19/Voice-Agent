import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, DateTime, Enum, Text
from sqlalchemy.dialects.sqlite import TEXT
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    patient_id     = Column(TEXT, primary_key=True, default=generate_uuid)
    first_name     = Column(String(50), nullable=False)
    last_name      = Column(String(50), nullable=False)
    date_of_birth  = Column(String(10), nullable=False)        # stored as MM/DD/YYYY string
    sex            = Column(String(20), nullable=False)        # Male/Female/Other/Decline to Answer
    phone_number   = Column(String(15), nullable=False)
    email          = Column(String(255), nullable=True)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city           = Column(String(100), nullable=False)
    state          = Column(String(2), nullable=False)
    zip_code       = Column(String(10), nullable=False)

    insurance_provider  = Column(String(255), nullable=True)
    insurance_member_id = Column(String(100), nullable=True)
    preferred_language  = Column(String(100), nullable=True, default="English")

    emergency_contact_name  = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(15), nullable=True)

    created_at  = Column(DateTime(timezone=True), default=utcnow)
    updated_at  = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    deleted_at  = Column(DateTime(timezone=True), nullable=True)   # soft delete
