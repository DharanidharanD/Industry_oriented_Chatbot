from flask import Flask, request, jsonify
import os

app = Flask(__name__)

KB = {
    "HR": {
        "leave": {
            "keywords": ["leave", "vacation", "holiday", "time off", "pto", "sick", "annual", "maternity", "paternity"],
            "title": "Leave Policy",
            "response": "Annual Leave: 18 days/year. Sick Leave: 10 days/year (medical certificate needed for absences over 2 days). Maternity Leave: 26 weeks fully paid. Paternity Leave: 2 weeks fully paid. Apply via HR Portal under Leave Management."
        },
        "salary": {
            "keywords": ["salary", "pay", "payroll", "payslip", "compensation", "wage", "increment", "hike"],
            "title": "Salary & Payroll",
            "response": "Salaries are credited on the last working day of each month. Payslips are available in the HR Portal under My Payslips. Annual increments are processed every April. For discrepancies contact payroll@retailcorp.com."
        },
        "onboarding": {
            "keywords": ["onboarding", "joining", "new employee", "induction", "new hire", "first day"],
            "title": "Onboarding",
            "response": "Complete e-KYC on the HR Portal within 3 days of joining. Attend the 2-day company induction. Collect your ID card from Admin Desk, Floor 1. Complete mandatory compliance training within 7 days."
        },
        "policy": {
            "keywords": ["policy", "policies", "rules", "code of conduct", "dress code", "wfh", "work from home"],
            "title": "HR Policies",
            "response": "Code of Conduct: Zero tolerance for harassment. Dress Code: Business casual Mon-Thu, casual Friday. WFH Policy: Up to 2 days/week with manager approval. Probation Period: 6 months for all new hires."
        },
        "training": {
            "keywords": ["training", "learning", "development", "course", "upskill", "certification"],
            "title": "Training & Development",
            "response": "Access the LMS at learn.retailcorp.com. Mandatory modules: Safety, Data Privacy, Anti-Bribery (annually). External certification requests go through HR Portal. Each employee has an annual L&D budget of Rs.15,000."
        },
    },
    "IT Support": {
        "password": {
            "keywords": ["password", "reset", "forgot", "locked", "login", "credentials"],
            "title": "Password & Account",
            "response": "Self-service reset: go.retailcorp.com/reset (requires mobile OTP). Account locked: Auto-unlocks after 30 minutes or call IT on extension 1234. First-time login: Check your welcome email for temporary credentials."
        },
        "vpn": {
            "keywords": ["vpn", "remote access", "network", "internet", "wifi", "connection"],
            "title": "VPN & Network",
            "response": "Download GlobalProtect VPN from it.retailcorp.com/vpn. Use your corporate email credentials to authenticate. Connect to RetailCorp-Secure when on office Wi-Fi. IT Support hours: Monday to Saturday 8 AM to 9 PM."
        },
        "hardware": {
            "keywords": ["laptop", "hardware", "mouse", "keyboard", "monitor", "printer", "device", "broken", "not working"],
            "title": "Hardware & Equipment",
            "response": "Log a hardware fault via ServiceDesk under Hardware. Replacement SLA: Peripherals within 24 hours, Laptops within 48 hours. Loaner devices available from IT Store on Floor 2."
        },
        "software": {
            "keywords": ["software", "install", "application", "app", "license", "excel", "outlook", "error", "crash"],
            "title": "Software & Applications",
            "response": "Software installs: ServiceDesk under Software Installation Request. Licensed apps like MS Office and Adobe are pre-approved. Other software requires manager and IT Head approval (2-5 business days)."
        },
        "email": {
            "keywords": ["email", "outlook", "mail", "inbox", "spam", "calendar", "teams", "meeting"],
            "title": "Email & Collaboration",
            "response": "Outlook Web access: mail.retailcorp.com. Storage limit: 50 GB. MS Teams: teams.retailcorp.com or desktop app. Email issues: ServiceDesk under Email Access Issue."
        },
    },
    "Finance": {
        "invoice": {
            "keywords": ["invoice", "bill", "billing", "vendor payment", "supplier", "gst", "tax invoice"],
            "title": "Invoice & Billing",
            "response": "Submit invoices to finance@retailcorp.com or the Vendor Portal. Required fields: GST No., PO Number, Bank Details, Date. Processing time: 7-10 working days after approval. Invoices without PO numbers will be returned."
        },
        "expense": {
            "keywords": ["expense", "reimbursement", "claim", "travel", "petty cash", "advance"],
            "title": "Expense & Reimbursement",
            "response": "Submit claims via Finance Portal under Expense Claims within 30 days. Travel advance: Apply 5 days before travel. Petty cash limit: Rs.5,000 per transaction with receipts. Claims without receipts will be rejected."
        },
        "budget": {
            "keywords": ["budget", "forecast", "opex", "capex", "spending", "allocation"],
            "title": "Budget & Forecasting",
            "response": "Annual budgets are finalised in December. Mid-year revisions require CFO approval. Department heads receive monthly Budget vs Actual reports. CAPEX requests go through Finance Portal."
        },
        "audit": {
            "keywords": ["audit", "compliance", "gst filing", "tax", "tds", "return", "regulatory"],
            "title": "Audit & Compliance",
            "response": "GST returns are filed monthly by the 20th. TDS is deducted per the Income Tax Act. Form 16 is issued in June. Internal audits are conducted quarterly. Document requests: compliance@retailcorp.com."
        },
        "payment": {
            "keywords": ["payment", "bank transfer", "neft", "rtgs", "fund transfer", "purchase order"],
            "title": "Payments & Transfers",
            "response": "Vendor payments are processed every Tuesday and Friday. RTGS/NEFT same-day if submitted before 12 PM. Payment status: Finance Portal under Payments. Urgent payments: finance-urgent@retailcorp.com."
        },
    },
}

SUGGESTIONS = {
    "HR":         ["Leave policy", "Salary and payroll", "Onboarding steps", "HR policies", "Training"],
    "IT Support": ["Reset my password", "VPN setup", "Hardware issue", "Software install", "Email issue"],
    "Finance":    ["Submit an invoice", "Expense claim", "Budget query", "Audit compliance", "Vendor payment"],
}


def detect_intent(user_input, dept):
    text = user_input.lower()
    for topic, data in KB[dept].items():
        if any(kw in text for kw in data["keywords"]):
            return {"title": data["title"], "response": data["response"]}
    return None


@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return f.read()


@app.route("/api/departments")
def get_departments():
    return jsonify([
        {"name": k, "suggestions": SUGGESTIONS[k]}
        for k in KB.keys()
    ])


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    dept = data.get("department", "")
    message = data.get("message", "").strip()

    if not dept or dept not in KB:
        return jsonify({"error": "Invalid department"}), 400
    if not message:
        return jsonify({"error": "Empty message"}), 400

    result = detect_intent(message, dept)
    if result:
        return jsonify(result)
    else:
        return jsonify({
            "title": "Not sure about that",
            "response": "I could not find an answer for your query. Please try rephrasing or choose one of the suggested topics.",
            "suggestions": SUGGESTIONS.get(dept, [])
        })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
