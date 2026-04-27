# CareCloud Voice AI Agent — Testing Guide

This document contains all test cases for validating the Patient Registration API and Vapi webhook integration.

---

## Table of Contents

1. [Health Check](#1-health-check)
2. [List Patients](#2-list-patients)
3. [Get Single Patient](#3-get-single-patient)
4. [Create Patient](#4-create-patient)
5. [Update Patient](#5-update-patient)
6. [Delete Patient](#6-delete-patient)
7. [Vapi Webhook — Tool Calls](#7-vapi-webhook--tool-calls)
8. [Recommended Test Flow](#recommended-test-flow)

---

## Base URL

```
https://your-app.render.com
```

Access Swagger UI at: `https://your-app.render.com/docs`

---

## 1. Health Check

### `GET /health`

**Request:**
```bash
curl -X GET "https://your-app.render.com/health"
```

**Expected Response (200):**
```json
{
  "status": "ok"
}
```

---

## 2. List Patients

### `GET /patients`

#### 2a. List All Patients (No Filters)

**Request:**
```bash
curl -X GET "https://your-app.render.com/patients"
```

**Expected Response (200):**
```json
{
  "data": [
    {
      "patient_id": "...",
      "first_name": "Jane",
      "last_name": "Doe",
      "date_of_birth": "03/15/1985",
      "sex": "Female",
      "phone_number": "5551234567",
      ...
    }
  ],
  "error": null
}
```

#### 2b. Filter by Last Name

**Request:**
```bash
curl -X GET "https://your-app.render.com/patients?last_name=Doe"
```

**Query Params:**
| Param | Value |
|-------|-------|
| `last_name` | `Doe` |

**Expected Response (200):**
Returns only patients whose last name contains "Doe" (case-insensitive).

#### 2c. Filter by Phone Number

**Request:**
```bash
curl -X GET "https://your-app.render.com/patients?phone_number=5551234567"
```

**Query Params:**
| Param | Value |
|-------|-------|
| `phone_number` | `5551234567` |

#### 2d. Filter by Date of Birth

**Request:**
```bash
curl -X GET "https://your-app.render.com/patients?date_of_birth=03/15/1985"
```

**Query Params:**
| Param | Value |
|-------|-------|
| `date_of_birth` | `03/15/1985` |

#### 2e. Combined Filters

**Request:**
```bash
curl -X GET "https://your-app.render.com/patients?last_name=Doe&phone_number=5551234567"
```

---

## 3. Get Single Patient

### `GET /patients/{patient_id}`

#### 3a. Existing Patient

**Path Param:** `patient_id` = valid UUID from `GET /patients`

**Request:**
```bash
curl -X GET "https://your-app.render.com/patients/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Expected Response (200):**
```json
{
  "data": {
    "patient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "first_name": "Jane",
    "last_name": "Doe",
    ...
  },
  "error": null
}
```

#### 3b. Non-Existent Patient

**Path Param:** `patient_id` = `00000000-0000-0000-0000-000000000000`

**Expected Response (404):**
```json
{
  "data": null,
  "error": "Patient not found."
}
```

#### 3c. Soft-Deleted Patient

After calling `DELETE /patients/{id}`, a `GET` on the same ID should return **404**.

---

## 4. Create Patient

### `POST /patients`

#### 4a. ✅ Valid — Full Patient (All Fields)

**Request Body:**
```json
{
  "first_name": "Alice",
  "last_name": "Johnson",
  "date_of_birth": "05/12/1988",
  "sex": "Female",
  "phone_number": "5558675309",
  "email": "alice.j@example.com",
  "address_line_1": "789 Pine Street",
  "address_line_2": "Apt 4B",
  "city": "Chicago",
  "state": "IL",
  "zip_code": "60614",
  "insurance_provider": "UnitedHealthcare",
  "insurance_member_id": "UH99887766",
  "preferred_language": "English",
  "emergency_contact_name": "Bob Johnson",
  "emergency_contact_phone": "5551239999"
}
```

**Expected Response (201):**
```json
{
  "data": {
    "patient_id": "...",
    "first_name": "Alice",
    "last_name": "Johnson",
    ...
  },
  "error": null
}
```

#### 4b. ✅ Valid — Minimum Required Fields Only

**Request Body:**
```json
{
  "first_name": "Carlos",
  "last_name": "Martinez",
  "date_of_birth": "11/03/1995",
  "sex": "Male",
  "phone_number": "5554443333",
  "address_line_1": "100 Elm Rd",
  "city": "Miami",
  "state": "FL",
  "zip_code": "33101"
}
```

**Expected Response (201):**
Patient created with `email`, `address_line_2`, `insurance_provider`, etc. set to `null`.

#### 4c. ❌ Invalid — Missing Required Fields

**Request Body:**
```json
{
  "first_name": "Test",
  "last_name": "User",
  "date_of_birth": "01/01/1990",
  "sex": "Male",
  "phone_number": "5550001111"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "address_line_1": "Field required",
    "city": "Field required",
    "state": "Field required",
    "zip_code": "Field required"
  }
}
```

#### 4d. ❌ Invalid — Future Date of Birth

**Request Body:**
```json
{
  "first_name": "Future",
  "last_name": "Baby",
  "date_of_birth": "12/31/2030",
  "sex": "Other",
  "phone_number": "5550002222",
  "address_line_1": "123 Nowhere",
  "city": "Springfield",
  "state": "IL",
  "zip_code": "62701"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "date_of_birth": "Date of birth cannot be today or in the future"
  }
}
```

#### 4e. ❌ Invalid — Bad Phone Number

**Request Body:**
```json
{
  "first_name": "Bad",
  "last_name": "Phone",
  "date_of_birth": "01/01/1990",
  "sex": "Male",
  "phone_number": "123",
  "address_line_1": "123 Main",
  "city": "Austin",
  "state": "TX",
  "zip_code": "78701"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "phone_number": "Phone number must be a valid 10-digit U.S. number"
  }
}
```

#### 4f. ❌ Invalid — Bad State (Full Name Instead of Abbreviation)

**Request Body:**
```json
{
  "first_name": "Bad",
  "last_name": "State",
  "date_of_birth": "01/01/1990",
  "sex": "Female",
  "phone_number": "5550003333",
  "address_line_1": "123 Main",
  "city": "Austin",
  "state": "Texas",
  "zip_code": "78701"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "state": "Invalid state"
  }
}
```

#### 4g. ❌ Invalid — Bad ZIP Code

**Request Body:**
```json
{
  "first_name": "Bad",
  "last_name": "Zip",
  "date_of_birth": "01/01/1990",
  "sex": "Male",
  "phone_number": "5550004444",
  "address_line_1": "123 Main",
  "city": "Austin",
  "state": "TX",
  "zip_code": "78"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "zip_code": "Invalid ZIP"
  }
}
```

#### 4h. ❌ Invalid — Name with Numbers

**Request Body:**
```json
{
  "first_name": "John123",
  "last_name": "Doe",
  "date_of_birth": "01/01/1990",
  "sex": "Male",
  "phone_number": "5550005555",
  "address_line_1": "123 Main",
  "city": "Austin",
  "state": "TX",
  "zip_code": "78701"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "first_name": "Name must be 1-50 alphabetic characters (hyphens/apostrophes allowed)"
  }
}
```

#### 4i. ❌ Invalid — Duplicate Phone Number

Create the same patient twice (same `phone_number`).

**Expected Response (409):**
```json
{
  "data": null,
  "error": "A patient with this phone number already exists"
}
```

---

## 5. Update Patient

### `PUT /patients/{patient_id}`

#### 5a. ✅ Partial Update — Email & Insurance

**Path Param:** valid `patient_id`

**Request Body:**
```json
{
  "email": "new.email@updated.com",
  "insurance_provider": "Aetna",
  "insurance_member_id": "AET123456"
}
```

**Expected Response (200):**
Patient record returned with updated fields. `updated_at` timestamp changed.

#### 5b. ✅ Partial Update — Address Only

**Request Body:**
```json
{
  "address_line_1": "500 New Street",
  "address_line_2": "Suite 100",
  "city": "Denver",
  "state": "CO",
  "zip_code": "80202"
}
```

#### 5c. ❌ Invalid — Bad Phone on Update

**Request Body:**
```json
{
  "phone_number": "999"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "phone_number": "Phone number must be a valid 10-digit U.S. number"
  }
}
```

#### 5d. ❌ Invalid — Bad State on Update

**Request Body:**
```json
{
  "state": "California"
}
```

**Expected Response (422):**
```json
{
  "data": null,
  "error": {
    "state": "Invalid state"
  }
}
```

#### 5e. ❌ Patient Not Found

**Path Param:** non-existent UUID

**Expected Response (404):**
```json
{
  "data": null,
  "error": "Patient not found."
}
```

---

## 6. Delete Patient

### `DELETE /patients/{patient_id}`

#### 6a. ✅ Soft Delete Existing Patient

**Path Param:** valid `patient_id`

**Request:**
```bash
curl -X DELETE "https://your-app.render.com/patients/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Expected Response (200):**
```json
{
  "data": {
    "message": "Patient a1b2c3d4-e5f6-7890-abcd-ef1234567890 deleted."
  },
  "error": null
}
```

#### 6b. Verify Soft Delete

Immediately `GET /patients/{patient_id}` with the same ID.

**Expected Response (404):**
```json
{
  "data": null,
  "error": "Patient not found."
}
```

#### 6c. Verify Excluded from List

`GET /patients` — deleted record should **not** appear.

#### 6d. ❌ Delete Non-Existent Patient

**Expected Response (404):**
```json
{
  "data": null,
  "error": "Patient not found."
}
```

---

## 7. Vapi Webhook — Tool Calls

### `POST /vapi/webhook`

#### 7a. ✅ Check Existing Patient — Found

**Request Body:**
```json
{
  "message": {
    "type": "tool-calls",
    "toolCalls": [
      {
        "id": "call_abc123",
        "function": {
          "name": "check_existing_patient",
          "arguments": {
            "phone_number": "5551234567"
          }
        }
      }
    ]
  }
}
```

**Expected Response (200):**
```json
{
  "results": [
    {
      "toolCallId": "call_abc123",
      "result": {
        "found": true,
        "patient_id": "...",
        "first_name": "Jane",
        "last_name": "Doe"
      }
    }
  ]
}
```

#### 7b. ✅ Check Existing Patient — Not Found

**Request Body:**
```json
{
  "message": {
    "type": "tool-calls",
    "toolCalls": [
      {
        "id": "call_def456",
        "function": {
          "name": "check_existing_patient",
          "arguments": {
            "phone_number": "5559998888"
          }
        }
      }
    ]
  }
}
```

**Expected Response (200):**
```json
{
  "results": [
    {
      "toolCallId": "call_def456",
      "result": {
        "found": false
      }
    }
  ]
}
```

#### 7c. ✅ Save Patient — Create New

**Request Body:**
```json
{
  "message": {
    "type": "tool-calls",
    "toolCalls": [
      {
        "id": "call_ghi789",
        "function": {
          "name": "save_patient",
          "arguments": {
            "first_name": "Vapi",
            "last_name": "TestUser",
            "date_of_birth": "06/15/1992",
            "sex": "Female",
            "phone_number": "5557776666",
            "address_line_1": "321 Oak Blvd",
            "city": "Portland",
            "state": "OR",
            "zip_code": "97201"
          }
        }
      }
    ]
  }
}
```

**Expected Response (200):**
```json
{
  "results": [
    {
      "toolCallId": "call_ghi789",
      "result": {
        "success": true,
        "action": "created",
        "patient_id": "...",
        "first_name": "Vapi"
      }
    }
  ]
}
```

#### 7d. ❌ Save Patient — Missing Required Fields

**Request Body:**
```json
{
  "message": {
    "type": "tool-calls",
    "toolCalls": [
      {
        "id": "call_jkl012",
        "function": {
          "name": "save_patient",
          "arguments": {
            "first_name": "Incomplete",
            "last_name": "Data",
            "date_of_birth": "01/01/1990",
            "sex": "Male",
            "phone_number": "5551112222"
          }
        }
      }
    ]
  }
}
```

**Expected Response (200):**
```json
{
  "results": [
    {
      "toolCallId": "call_jkl012",
      "result": {
        "success": false,
        "error": "Missing required fields: address_line_1, city, state, zip_code. Please ask the caller for these before calling save_patient."
      }
    }
  ]
}
```

#### 7e. ✅ End-of-Call Report

**Request Body:**
```json
{
  "message": {
    "type": "end-of-call-report",
    "summary": "Patient registered successfully."
  }
}
```

**Expected Response (200):**
```json
{
  "received": true
}
```

#### 7f. ✅ Unknown Tool Name

**Request Body:**
```json
{
  "message": {
    "type": "tool-calls",
    "toolCalls": [
      {
        "id": "call_xyz999",
        "function": {
          "name": "unknown_tool",
          "arguments": {}
        }
      }
    ]
  }
}
```

**Expected Response (200):**
```json
{
  "results": [
    {
      "toolCallId": "call_xyz999",
      "result": {
        "error": "Unknown tool: unknown_tool"
      }
    }
  ]
}
```

---

## Recommended Test Flow

Run these in order to validate the full system:

| Step | Action | Endpoint | Expected Result |
|------|--------|----------|-----------------|
| 1 | Health check | `GET /health` | `{"status": "ok"}` |
| 2 | List all patients | `GET /patients` | See Jane & John seed data |
| 3 | Create full patient | `POST /patients` | 201, patient returned |
| 4 | Create minimal patient | `POST /patients` | 201, optional fields null |
| 5 | Filter by last name | `GET /patients?last_name=...` | Matching records only |
| 6 | Get single patient | `GET /patients/{id}` | 200, full record |
| 7 | Update patient email | `PUT /patients/{id}` | 200, updated record |
| 8 | Verify update | `GET /patients/{id}` | Updated email present |
| 9 | Soft delete patient | `DELETE /patients/{id}` | 200, success message |
| 10 | Verify deletion | `GET /patients/{id}` | 404, not found |
| 11 | Verify excluded from list | `GET /patients` | Deleted record absent |
| 12 | Test validation — missing fields | `POST /patients` | 422, specific errors |
| 13 | Test validation — future DOB | `POST /patients` | 422, DOB error |
| 14 | Test validation — bad phone | `POST /patients` | 422, phone error |
| 15 | Test validation — bad state | `POST /patients` | 422, state error |
| 16 | Test validation — bad ZIP | `POST /patients` | 422, ZIP error |
| 17 | Test validation — bad name | `POST /patients` | 422, name error |
| 18 | Test duplicate phone | `POST /patients` (x2) | 409 on second call |
| 19 | Vapi check existing — found | `POST /vapi/webhook` | `found: true` |
| 20 | Vapi check existing — not found | `POST /vapi/webhook` | `found: false` |
| 21 | Vapi save patient — valid | `POST /vapi/webhook` | `success: true` |
| 22 | Vapi save patient — missing fields | `POST /vapi/webhook` | `success: false` with missing list |

---

## Notes

- All dates use **MM/DD/YYYY** format.
- Phone numbers are stored as **10 digits only** (non-digits stripped).
- States must be **2-letter U.S. abbreviations** (e.g., `CA`, `NY`, `TX`).
- ZIP codes accept **5-digit** or **ZIP+4** format (e.g., `90210` or `90210-1234`).
- The `deleted_at` field is used for **soft deletes** — records are hidden from queries but remain in the database.
- Vapi webhook responses use the `results` array format expected by the Vapi platform.
