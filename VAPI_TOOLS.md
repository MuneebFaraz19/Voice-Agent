# Vapi Tool Definitions
# In Vapi Dashboard → Assistant → Tools → Add Tool (Custom Function)
# Add BOTH tools below.

# ─────────────────────────────────────────────────────────────────
# TOOL 1: check_existing_patient
# ─────────────────────────────────────────────────────────────────
Name:        check_existing_patient
Description: Check if a patient already exists in the database by phone number.
             Call this at the start of every registration flow.
Server URL:  https://YOUR-RAILWAY-URL.railway.app/vapi/webhook

Parameters (JSON Schema):
{
  "type": "object",
  "properties": {
    "phone_number": {
      "type": "string",
      "description": "The caller's 10-digit U.S. phone number, digits only."
    }
  },
  "required": ["phone_number"]
}


# ─────────────────────────────────────────────────────────────────
# TOOL 2: save_patient
# ─────────────────────────────────────────────────────────────────
Name:        save_patient
Description: Save or update a patient record after the caller has confirmed all information.
             Only call this AFTER reading back all fields and receiving explicit confirmation.
             Include patient_id only when updating an existing record.
Server URL:  https://YOUR-RAILWAY-URL.railway.app/vapi/webhook

Parameters (JSON Schema):
{
  "type": "object",
  "properties": {
    "patient_id": {
      "type": "string",
      "description": "Existing patient UUID — only include when updating, omit for new patients."
    },
    "first_name": {
      "type": "string",
      "description": "Patient first name (alphabetic, hyphens/apostrophes allowed, max 50 chars)"
    },
    "last_name": {
      "type": "string",
      "description": "Patient last name (alphabetic, hyphens/apostrophes allowed, max 50 chars)"
    },
    "date_of_birth": {
      "type": "string",
      "description": "Date of birth in MM/DD/YYYY format. Must be a past date."
    },
    "sex": {
      "type": "string",
      "enum": ["Male", "Female", "Other", "Decline to Answer"],
      "description": "Biological sex as recorded for medical purposes."
    },
    "phone_number": {
      "type": "string",
      "description": "10-digit U.S. phone number, digits only."
    },
    "email": {
      "type": "string",
      "description": "Optional. Patient email address."
    },
    "address_line_1": {
      "type": "string",
      "description": "Street address line 1."
    },
    "address_line_2": {
      "type": "string",
      "description": "Optional. Apartment, suite, or unit number."
    },
    "city": {
      "type": "string",
      "description": "City name."
    },
    "state": {
      "type": "string",
      "description": "2-letter U.S. state abbreviation (e.g. NY, CA, TX)."
    },
    "zip_code": {
      "type": "string",
      "description": "5-digit or ZIP+4 format (e.g. 10001 or 10001-1234)."
    },
    "insurance_provider": {
      "type": "string",
      "description": "Optional. Name of insurance company."
    },
    "insurance_member_id": {
      "type": "string",
      "description": "Optional. Insurance member or subscriber ID."
    },
    "preferred_language": {
      "type": "string",
      "description": "Optional. Defaults to English."
    },
    "emergency_contact_name": {
      "type": "string",
      "description": "Optional. Full name of emergency contact."
    },
    "emergency_contact_phone": {
      "type": "string",
      "description": "Optional. 10-digit U.S. phone number for emergency contact."
    }
  },
  "required": [
    "first_name",
    "last_name",
    "date_of_birth",
    "sex",
    "phone_number",
    "address_line_1",
    "city",
    "state",
    "zip_code"
  ]
}
