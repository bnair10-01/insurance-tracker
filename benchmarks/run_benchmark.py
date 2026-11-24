"""Generate labeled synthetic policy PDFs, run them through insurance-tracker's API, score field accuracy."""
import os
OUT = os.environ.get("BENCH_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
os.makedirs(OUT, exist_ok=True)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
import io, json, statistics, time, requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

B = BASE_URL

DOCS = [
 dict(category="auto", provider="Harborline Mutual Insurance", policy="HM-AUTO-482913", start="2026-07-01", end="2027-06-30",
      amount=118.50, freq="monthly", phone="1-800-555-0142", email="claims@harborline.example", name="2021 Honda Civic",
      body=["PERSONAL AUTO POLICY DECLARATIONS", "Insured vehicle: 2021 Honda Civic EX, VIN 2HGFC2F69MH512345", "Liability: $100,000 per person / $300,000 per accident", "Collision and comprehensive: $500 deductible", "Uninsured motorist coverage included."]),
 dict(category="home", provider="Cedar Ridge Property & Casualty", policy="CR-HO3-77120045", start="2026-01-15", end="2027-01-15",
      amount=1860.00, freq="annual", phone="1-888-555-0177", email="service@cedarridge.example", name="Home - 214 Maple Ave",
      body=["HOMEOWNERS POLICY (HO-3)", "Insured location: 214 Maple Avenue, Springfield", "Dwelling coverage: $425,000", "Personal property: $212,500", "Water backup endorsement included."]),
 dict(category="health", provider="Northstar Health Plans", policy="NH-PPO-9034418", start="2026-01-01", end="2026-12-10",
      amount=412.00, freq="monthly", phone="1-855-555-0120", email="members@northstarhealth.example", name="Northstar PPO Gold",
      body=["PPO MEDICAL PLAN CERTIFICATE", "Plan: Gold PPO 1500", "Annual deductible: $1,500 individual", "Out-of-pocket maximum: $6,000", "Prescription coverage tiers 1-4."]),
 dict(category="life", provider="Evergreen Life Assurance", policy="EL-T20-5521907", start="2022-03-01", end="2042-03-01",
      amount=64.25, freq="monthly", phone="1-877-555-0166", email="policy@evergreenlife.example", name="20-Year Term Life",
      body=["TERM LIFE INSURANCE POLICY", "Death benefit: $500,000", "Term: 20 years", "Beneficiary designation on file."]),
 dict(category="gadget", provider="DeviceGuard Protection", policy="DG-PH-30019284", start="2026-02-01", end="2026-08-01",
      amount=14.99, freq="monthly", phone="1-866-555-0133", email="support@deviceguard.example", name="iPhone 15 Pro",
      body=["DEVICE PROTECTION PLAN", "Covered device: iPhone 15 Pro 256GB", "Accidental damage and theft coverage", "Service fee per claim: $99."]),
 dict(category="travel", provider="Wayfarer Travel Cover", policy="WT-TRP-6610842", start="2026-12-20", end="2027-01-05",
      amount=189.00, freq="one-time", phone="1-844-555-0109", email="help@wayfarercover.example", name="Trip to Lisbon",
      body=["TRAVEL INSURANCE CERTIFICATE", "Trip: Boston to Lisbon, round trip", "Trip cancellation: up to $5,000", "Emergency medical: up to $100,000."]),
]

def make_pdf(d):
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=letter); y = 740
    c.setFont("Helvetica-Bold", 15); c.drawString(60, y, d["provider"]); y -= 28
    c.setFont("Helvetica", 11)
    lines = d["body"] + ["", f"Policy Number: {d['policy']}", f"Coverage Period: {d['start']} to {d['end']}",
             f"Premium: ${d['amount']:.2f} ({d['freq']})", f"Customer service: {d['phone']}  |  {d['email']}",
             "", "This document is a synthetic specimen created for software testing."]
    for ln in lines:
        c.drawString(60, y, ln); y -= 18
    c.save(); return buf.getvalue()

def req(method, path, **kw):
    r = requests.request(method, B + path, timeout=300, **kw); r.raise_for_status(); return r.json()

email = f"bench{int(time.time())}@example.com"
tok = req("POST", "/api/auth/signup", json={"email": email, "password": "benchmark-pass-1"})["access_token"]
H = {"Authorization": f"Bearer {tok}"}

results = []
for d in DOCS:
    pdf = make_pdf(d)
    t = time.time()
    draft = req("POST", "/api/documents/extract", headers=H, files={"file": (f"{d['policy']}.pdf", pdf, "application/pdf")})
    ms = (time.time() - t) * 1000
    checks = {
        "category": draft["category"] == d["category"],
        "provider_name": (draft["provider_name"] or "").lower() == d["provider"].lower(),
        "policy_number": draft["policy_number"] == d["policy"],
        "coverage_start": draft["coverage_start"] == d["start"],
        "coverage_end": draft["coverage_end"] == d["end"],
        "premium_amount": draft["premium"].get("amount") == d["amount"],
        "premium_frequency": draft["premium"].get("frequency") == d["freq"],
        "phone": draft["provider_contact"].get("phone") == d["phone"],
        "email": draft["provider_contact"].get("email") == d["email"],
    }
    results.append({"doc": d["policy"], "ms": ms, "confidence": draft["extraction_confidence"], "checks": checks, "draft": draft})
    print(f"{d['policy']:<16} {ms:6.0f}ms conf={draft['extraction_confidence']} {sum(checks.values())}/{len(checks)}", {k: v for k, v in checks.items() if not v}, flush=True)
    item = {k: draft[k] for k in ("item_name", "category", "provider_name", "provider_contact", "policy_number", "coverage_start", "coverage_end", "premium", "coverage_summary", "extraction_confidence", "source_document_ref", "raw_extracted_text")}
    req("POST", "/api/items", headers=H, json=item)

items = req("GET", "/api/items", headers=H)
n_checks = sum(len(r["checks"]) for r in results); n_ok = sum(sum(r["checks"].values()) for r in results)
per_field = {k: sum(r["checks"][k] for r in results) / len(results) for k in results[0]["checks"]}
summary = {"email": email, "docs": len(results), "fields_correct": n_ok, "fields_total": n_checks, "field_accuracy": n_ok / n_checks,
           "docs_fully_correct": sum(all(r["checks"].values()) for r in results),
           "per_field": per_field, "latency_ms_p50": statistics.median(r["ms"] for r in results), "latency_ms_max": max(r["ms"] for r in results),
           "statuses": {i["item_name"]: i["status"] for i in items}, "items_saved": len(items)}
json.dump({"summary": summary, "results": results}, open(f"{OUT}/ins_results.json", "w"), indent=1, default=str)
print(json.dumps(summary, indent=1))
