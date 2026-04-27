import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, model_validator


US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC"
}

NAME_RE   = re.compile(r"^[A-Za-z\-']{1,50}$")
PHONE_RE  = re.compile(r"^\d{10}$")
ZIP_RE    = re.compile(r"^\d{5}(-\d{4})?$")
DOB_RE    = re.compile(r"^\d{2}/\d{2}/\d{4}$")


# ── Base (shared fields) ────────────────────────────────────────────────────

class PatientBase(BaseModel):
    first_name:     str
    last_name:      str
    date_of_birth:  str
    sex:            str
    phone_number:   str
    email:          Optional[str] = None
    
    # THESE ARE REQUIRED — must match models.py nullable=False
    address_line_1: str
    city:           str
    state:          str
    zip_code:       str

    address_line_2: Optional[str] = None

    insurance_provider:      Optional[str] = None
    insurance_member_id:     Optional[str] = None
    preferred_language:      Optional[str] = "English"

    emergency_contact_name:  Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if not NAME_RE.match(v):
            raise ValueError("Name must be 1-50 alphabetic characters (hyphens/apostrophes allowed)")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v):
        if not DOB_RE.match(v):
            raise ValueError("Date of birth must be MM/DD/YYYY")
        try:
            dob = datetime.strptime(v, "%m/%d/%Y")
        except ValueError:
            raise ValueError("Invalid date of birth")
        if dob.date() >= datetime.utcnow().date():
            raise ValueError("Date of birth cannot be today or in the future")
        return v

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v):
        allowed = {"Male", "Female", "Other", "Decline to Answer"}
        if v not in allowed:
            raise ValueError(f"Sex must be one of: {', '.join(allowed)}")
        return v

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        digits = re.sub(r"\D", "", v)
        if not PHONE_RE.match(digits):
            raise ValueError("Phone number must be a valid 10-digit U.S. number")
        return digits

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        if v is None:
            return v
        if v.upper() not in US_STATES:
            raise ValueError("Invalid state")
        return v.upper()

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v):
        if v is None:
            return v
        if not ZIP_RE.match(v):
            raise ValueError("Invalid ZIP")
        return v

# ── Create (incoming POST body) ─────────────────────────────────────────────

class PatientCreate(PatientBase):
    pass


# ── Update (incoming PUT body — all optional) ───────────────────────────────

class PatientUpdate(BaseModel):
    first_name:     Optional[str] = None
    last_name:      Optional[str] = None
    date_of_birth:  Optional[str] = None
    sex:            Optional[str] = None
    phone_number:   Optional[str] = None
    email:          Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city:           Optional[str] = None
    state:          Optional[str] = None
    zip_code:       Optional[str] = None
    insurance_provider:      Optional[str] = None
    insurance_member_id:     Optional[str] = None
    preferred_language:      Optional[str] = None
    emergency_contact_name:  Optional[str] = None
    emergency_contact_phone: Optional[str] = None


# ── Response (outgoing) ──────────────────────────────────────────────────────

class PatientResponse(PatientBase):
    patient_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── API envelope ─────────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    data:  Optional[object] = None
    error: Optional[str]    = None
