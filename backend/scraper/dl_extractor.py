"""
Driving Licence Data Extractor
Strategy: Download PDFs from official sources + manual curation
Note: dmt.gov.lk is domain-hijacked — use eservices.motortraffic.gov.lk
      and gov.lk for official info.

LEARNING NOTE:
- PDFs are NOT all the same — some have real text, some are scanned images
- pdfplumber works on text-based PDFs (most official government forms)
- Scanned PDFs need OCR (Tesseract) — we'll skip that for now
"""

import json
import requests
import pdfplumber
from io import BytesIO
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "GovFlowAI/1.0 Research Bot",
}


def try_extract_pdf(url: str) -> str:
    """
    Download a PDF and extract its text.
    Returns extracted text or empty string if it fails.
    
    LEARNING: We use BytesIO to keep the PDF in memory (no need to save to disk).
    pdfplumber opens it and extracts text page by page.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        
        pdf_bytes = BytesIO(response.content)
        text_parts = []
        
        with pdfplumber.open(pdf_bytes) as pdf:
            print(f"  → PDF has {len(pdf.pages)} pages")
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"[Page {i+1}]\n{page_text}")
        
        full_text = "\n\n".join(text_parts)
        print(f"  → Extracted {len(full_text)} chars of text")
        return full_text
        
    except Exception as e:
        print(f"  ✗ PDF extraction failed: {e}")
        return ""


def build_dl_manual_data() -> dict:
    """
    Manually curated Driving Licence workflow data.
    
    LEARNING: This is intentional manual curation because:
    1. The real DMT site requires login
    2. Government procedures require human verification for accuracy
    3. This is the "admin review" step made explicit — YOU are the admin right now
    
    Sources used to build this:
    - eservices.motortraffic.gov.lk (appointment portal structure)
    - gov.lk service listings
    - Yamu.lk verified guide (cross-referenced with official)
    - DMT WhatsApp: 071-4033300
    """
    return {
        "service_type": "driving_licence",
        "department": "Department of Motor Traffic",
        "official_appointment_url": "https://eservices.motortraffic.gov.lk",
        "official_contact_whatsapp": "071-4033300",
        "review_status": "manually_curated",
        "note": "Cross-referenced from eservices.motortraffic.gov.lk and gov.lk. Verify before publishing.",
        
        "sub_services": {
            "dl_new": {
                "name": "New Driving Licence (First Time)",
                "eligibility": {
                    "minimum_age": 18,
                    "requires_learner_permit": True,
                    "learner_permit_holding_period_days": 90
                },
                "required_documents": [
                    {
                        "key": "nic_original",
                        "name": "Original National Identity Card (NIC)",
                        "requirement_type": "required",
                        "notes": "Must be the smart card (12-digit NIC number)"
                    },
                    {
                        "key": "nic_copy",
                        "name": "Photocopy of NIC",
                        "requirement_type": "required",
                        "notes": "Both front and back"
                    },
                    {
                        "key": "birth_certificate",
                        "name": "Birth Certificate",
                        "requirement_type": "required",
                        "notes": "Original or certified copy"
                    },
                    {
                        "key": "medical_certificate",
                        "name": "Medical Certificate from National Transport Medical Institution",
                        "requirement_type": "required",
                        "notes": "Must be from NTMI — not any private hospital"
                    },
                    {
                        "key": "learner_permit",
                        "name": "Current Learner Permit",
                        "requirement_type": "required",
                        "notes": "Must be held for at least 3 months"
                    },
                    {
                        "key": "passport_photo",
                        "name": "Recent Passport-Sized Photographs",
                        "requirement_type": "required",
                        "notes": "Check current DMT specification for count"
                    },
                    {
                        "key": "driving_school_certificate",
                        "name": "Certificate from Registered Driving School",
                        "requirement_type": "conditional",
                        "condition": "If attended a driving school",
                        "notes": "Optional but recommended"
                    }
                ],
                "workflow_steps": [
                    {
                        "step_key": "get_learner_permit",
                        "title": "Obtain a Learner Permit first",
                        "description": "You must hold a learner permit for at least 3 months before applying for the full licence. Visit your nearest DMT district office.",
                        "order": 1,
                        "estimated_time": "1 day to obtain"
                    },
                    {
                        "step_key": "get_medical_certificate",
                        "title": "Get Medical Certificate from NTMI",
                        "description": "Visit the National Transport Medical Institution (NTMI) for a medical fitness examination. This is ONLY accepted from NTMI — not any private hospital.",
                        "order": 2,
                        "estimated_time": "1 day"
                    },
                    {
                        "step_key": "book_appointment",
                        "title": "Book appointment on DMT e-Services portal",
                        "description": "Visit https://eservices.motortraffic.gov.lk to book your appointment at your nearest DMT district office.",
                        "order": 3,
                        "estimated_time": "15 minutes online"
                    },
                    {
                        "step_key": "prepare_documents",
                        "title": "Prepare all required documents",
                        "description": "Gather all documents listed in the checklist. Double-check each item before your appointment.",
                        "order": 4,
                        "estimated_time": "1–2 days"
                    },
                    {
                        "step_key": "attend_dmt_office",
                        "title": "Attend DMT district office on appointment date",
                        "description": "Bring all original documents and photocopies. Submit your application and pay the applicable fee at the cashier.",
                        "order": 5,
                        "estimated_time": "Half day"
                    },
                    {
                        "step_key": "written_test",
                        "title": "Pass the written knowledge test",
                        "description": "A computer-based test on traffic rules and road signs will be conducted at the DMT office.",
                        "order": 6,
                        "estimated_time": "30–60 minutes"
                    },
                    {
                        "step_key": "practical_test",
                        "title": "Pass the practical driving test",
                        "description": "A DMT examiner will conduct the practical driving test at the DMT office grounds.",
                        "order": 7,
                        "estimated_time": "30–60 minutes"
                    },
                    {
                        "step_key": "collect_licence",
                        "title": "Collect your driving licence",
                        "description": "Upon passing, your licence will be issued. Verify the processing time at your DMT office.",
                        "order": 8,
                        "estimated_time": "Same day or few days"
                    }
                ]
            },
            "dl_renewal": {
                "name": "Driving Licence Renewal",
                "renewal_window": "Can be renewed 3 months before expiry or up to 1 year after expiry",
                "required_documents": [
                    {
                        "key": "current_licence",
                        "name": "Current/Expired Driving Licence",
                        "requirement_type": "required"
                    },
                    {
                        "key": "nic_original",
                        "name": "Original NIC",
                        "requirement_type": "required"
                    },
                    {
                        "key": "nic_copy",
                        "name": "Photocopy of NIC",
                        "requirement_type": "required"
                    },
                    {
                        "key": "medical_certificate",
                        "name": "Medical Certificate from NTMI",
                        "requirement_type": "conditional",
                        "condition": "Required if renewing after expiry or for certain age groups. Check with DMT."
                    }
                ],
                "workflow_steps": [
                    {
                        "step_key": "book_appointment",
                        "title": "Book renewal appointment online",
                        "description": "Visit https://eservices.motortraffic.gov.lk and book a renewal appointment.",
                        "order": 1
                    },
                    {
                        "step_key": "prepare_documents",
                        "title": "Prepare renewal documents",
                        "description": "Gather current licence + NIC. Check if a medical certificate is needed for your case.",
                        "order": 2
                    },
                    {
                        "step_key": "attend_dmt_office",
                        "title": "Visit DMT office on your appointment date",
                        "description": "Submit documents and pay the renewal fee.",
                        "order": 3
                    },
                    {
                        "step_key": "collect_renewed_licence",
                        "title": "Collect renewed licence",
                        "description": "Renewed licence is typically issued on the same day.",
                        "order": 4
                    }
                ]
            }
        }
    }


def run():
    print("[DL] Building Driving Licence data...")
    
    # Build manual data
    dl_data = {
        "scraped_at": "2026-08-03T00:00:00Z",
        "source_note": "Manually curated from eservices.motortraffic.gov.lk and gov.lk. Requires admin review before publishing.",
        "data": build_dl_manual_data()
    }
    
    # Save
    output_path = OUTPUT_DIR / "dl_manual.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dl_data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Saved DL data to: {output_path}")
    print(f"   Sub-services: {list(dl_data['data']['sub_services'].keys())}")


if __name__ == "__main__":
    run()
