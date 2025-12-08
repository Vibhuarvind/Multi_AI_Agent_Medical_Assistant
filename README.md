# 🏥 Multi-Agent Healthcare Assistant (POC)

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit)](https://multi-ai-agent-doctor-by-vidisha.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-Passing-success?style=for-the-badge)](tests/)

> **⚠️ EDUCATIONAL DEMONSTRATION ONLY**  
> This is a proof-of-concept system for academic/portfolio purposes. It is **NOT** for clinical use. Always consult qualified healthcare professionals for medical advice.

---

## 📋 Overview

An AI-powered multi-agent system that demonstrates clinical triage, OTC medication recommendations, and e-pharmacy integration for respiratory conditions. Built with modular agents that collaborate to provide safe, intelligent healthcare assistance.

**Key Features:**
- 🔍 Chest X-ray analysis (mock classifier)
- 💊 OTC medicine recommendations with safety checks
- 🏥 Pharmacy matching with delivery ETA
- 👨‍⚕️ Doctor escalation for severe cases
- 🔒 PII/PHI protection (masked data, anonymized files)
- 📊 Full observability (timeline, agent logs, JSON outputs)

---

## 🏗️ System Architecture

![Multi-Agent Healthcare Architecture](Docs/Framework%20Architecture.png)

### Core Agents

| Agent | Responsibility | Key Outputs |
|-------|---------------|-------------|
| **🗂️ Ingestion** | File validation, PII masking, mock OCR | `{patient: {age, allergies}, xray_path, notes, pdf_text}` |
| **🔬 Imaging** | X-ray classification, severity detection | `{condition_probs: {pneumonia, normal, covid}, severity_hint}` |
| **💊 Therapy** | OTC recommendations, interaction screening | `{otc_options: [{sku, dose, freq}], red_flags: [...]}` |
| **🚨 Doctor Escalation** | Triage logic, consultation routing | `{doctor_escalation_needed: bool, escalation_suggestions: [...]}` |
| **🏥 Pharmacy Match** | Stock + geo matching, ETA calculation | `{pharmacy_id, items, eta_min, delivery_fee}` |
| **🎯 Orchestrator** | Flow coordination, timeline tracking | Consolidated results + order preview |

### Data Flow

```
User Input → Ingestion → Imaging → Therapy → Doctor Escalation
                                         ↓
                                   Pharmacy Match → Order Preview
```

Each agent handoff is **validated through integration tests** (see `tests/integration/`).

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **pip** or **uv** package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Multi_AI_Agent_Medical_Assistant

# Install dependencies (includes dev tools for testing)
pip install -e .[dev]

# Run the application
streamlit run app.py
```

The app will launch at `http://localhost:8501` 🎉

### Alternative: Using uv (faster)

```bash
uv pip install -e .[dev]
streamlit run app.py
```

---

## 📁 Project Structure

```
Multi_AI_Agent_Medical_Assistant/
├── Agents/                      # Core agent implementations
│   ├── ingestion.py             # File validation, PII masking
│   ├── imaging.py               # X-ray analysis (mock classifier)
│   ├── therapy.py               # OTC recommendation engine
│   ├── pharmacy_match.py        # Geo + inventory matching
│   ├── doctor_escalation.py     # Triage & consultation routing
│   └── coordinator.py           # Orchestrator (flow control)
├── Data/                        # Mock data sources (CSV/JSON)
│   ├── medicines.csv            # OTC formulary (age limits, contraindications)
│   ├── interactions.csv         # Drug interaction matrix
│   ├── pharmacies.json          # Partner pharmacy locations
│   ├── inventory.csv            # Stock levels per pharmacy
│   ├── doctors.csv              # Mock tele-consult roster
│   └── zipcodes.csv             # Pincode → lat/lon mapping
├── Utils/                       # Helper utilities
│   ├── data_loader.py           # CSV/JSON loaders
│   ├── logger.py                # Structured logging
│   ├── lookups.py               # SKU/pharmacy name mappings
│   └── constants.py             # Global config
├── tests/                       # Unit & integration tests
│   ├── unit/                    # Agent-level tests
│   └── integration/             # Handoff validation tests
├── Docs/                        # Documentation & diagrams
├── Testcases/                   # Sample X-rays, PDFs, screenshots
├── app.py                       # Streamlit UI
├── sample_order.json            # Sample order payload
├── test_sample_order.py         # Order validation script
└── README.md                    # This file
```

---

## 🎯 Sample Workflow

### User Journey

1. **Patient Input**
   - Enter demographics (name, age, phone, allergies, gender)
   - Describe symptoms in free text
   - Upload chest X-ray (PNG/JPG) - optional
   - Upload PDF report - optional
   - Provide pincode for pharmacy matching

2. **System Processing**
   ```
   Ingestion Agent
     ↓ (validates, masks PII, extracts text)
   Imaging Agent
     ↓ (analyzes X-ray → condition probabilities + severity)
   Therapy Agent
     ↓ (matches symptoms → OTC options, checks age/allergy/interactions)
   Doctor Escalation Agent
     ↓ (evaluates red flags → escalate if severe)
   Pharmacy Match Agent
     ↓ (finds nearest stock → calculates ETA & delivery fee)
   ```

3. **Output**
   - **Customer Summary Tab**: Diagnosis, medicines, safety warnings, pharmacy details, doctor suggestions
   - **Observability Tab**: Timeline, agent JSON outputs, order confirmation logs

4. **Order Placement** (Mock)
   - User clicks "Place mock order"
   - System generates `order_id`, `placed_at` timestamp, `total_cost`
   - Confirmation displayed in human-readable format + JSON log

### Example Order

See [`sample_order.json`](sample_order.json) for a complete example. Test it with:

```bash
python test_sample_order.py
```

**Expected output:**
```
📂 Loading sample order from: sample_order.json
🔍 Validating order schema...
✅ Schema validation PASSED

============================================================
           ORDER CONFIRMATION
============================================================

📋 Order ID: ORDER-AB12CD
📅 Placed: December 08, 2025 at 04:30:45 PM
🏥 Pharmacy: ph001
⏱️  Estimated Delivery: 20 minutes

💊 Items Ordered:
------------------------------------------------------------
1. Paracetamol (SKU: SKU001)
   Quantity: 100 | Unit Price: ₹20 | Subtotal: ₹2000
2. Ibuprofen (SKU: SKU002)
   Quantity: 50 | Unit Price: ₹30 | Subtotal: ₹1500

------------------------------------------------------------
Subtotal:        ₹   3500.00
Delivery Fee:    ₹     15.00
==============================================
TOTAL:           ₹   3515.00
============================================================
```

---

## 🧪 Testing

### Run All Tests

```bash
# Full test suite (unit + integration)
pytest

# Only integration tests (agent handoffs)
pytest tests/integration/

# Verbose output
pytest -v
```

### Test Coverage

**Integration Tests (Agent Handoffs):**
- ✅ `test_ingestion_to_imaging` - File persistence & X-ray path handoff
- ✅ `test_imaging_to_therapy` - Condition enrichment (imaging → therapy)
- ✅ `test_therapy_to_pharmacy` - SKU matching (therapy → pharmacy)
- ✅ `test_full_flow` - End-to-end orchestration with order preview

**Unit Tests:**
- Individual agent behavior (age checks, allergy screening, geo matching, etc.)

---

## 🔒 Safety & Privacy

### Safety Mechanisms

| Feature | Implementation |
|---------|---------------|
| **Red-Flag Detection** | "SpO2 < 92%", severe severity → immediate doctor escalation |
| **Age Restrictions** | Automatic rejection of medicines below `age_min` threshold |
| **Allergy Screening** | Checks `contra_allergy_keywords` for patient allergies |
| **Drug Interactions** | High/Moderate interactions flagged from `interactions.csv` |
| **Doctor Escalation** | Triggered when severity=severe, red flags present, or confidence < 50% |
| **OTC Only** | No prescription drugs recommended |

### Privacy Guarantees

- **PII Masking**: Names and phone numbers masked in logs (`P***t`, `########76`)
- **Anonymous Uploads**: Files saved with non-identifying prefixes (e.g., `xray_abc123.jpg`, `pneumonia_def456.jpg`)
- **No PHI Persistence**: All data treated as temporary, anonymous artifacts
- **Prominent Disclaimers**: "Educational demo only, not medical advice" shown throughout UI

---

## ⚠️ Known Limitations

### Technical Limitations

| Area | Current Implementation | Production Requirement |
|------|----------------------|----------------------|
| **X-ray Classifier** | Filename-based heuristics (keywords: `pneumonia`, `covid`, `normal`) | Trained CNN (ResNet-50 on ChestX-ray14 dataset) |
| **OCR** | Mock placeholder text | AWS Textract / pytesseract |
| **Geo Matching** | Dummy Manhattan distance | Google Maps API / Haversine formula |
| **Pharmacy APIs** | Static CSV inventory | Real-time inventory webhooks |
| **Payment** | Mock confirmation only | Stripe / Razorpay integration |
| **Authentication** | None (single-user demo) | OAuth2 + RBAC |
| **Database** | Local CSV/JSON files | PostgreSQL + MongoDB |

### Scope Constraints

- **OTC only**: No prescription drugs or controlled substances
- **Mock data**: All pharmacies, doctors, stock levels are simulated
- **Single condition focus**: Optimized for respiratory conditions (pneumonia, COVID-19, normal)
- **No longitudinal tracking**: Each session is independent (no patient history)
- **English only**: No multi-language support

---

## 📊 Data Sources

### Mock Data Files

All data files are located in `Data/` and are used for demonstration purposes only.

| File | Description | Sample Fields |
|------|-------------|---------------|
| `medicines.csv` | OTC formulary (8 drugs) | `sku`, `drug_name`, `indication`, `age_min`, `contra_allergy_keywords` |
| `interactions.csv` | Drug-drug interaction rules | `drug_a`, `drug_b`, `level` (High/Moderate/Low), `note` |
| `pharmacies.json` | Partner pharmacy locations (3 stores) | `id`, `name`, `lat`, `lon`, `services`, `delivery_km` |
| `inventory.csv` | Stock levels per pharmacy | `pharmacy_id`, `sku`, `drug_name`, `price`, `qty` |
| `doctors.csv` | Tele-consult roster (2 doctors) | `doctor_id`, `name`, `specialty`, `tele_slots` (ISO 8601) |
| `zipcodes.csv` | Pincode → geo mapping | `pincode`, `lat`, `lon` |

### Data Assumptions

- **Inventory**: Static stock levels (no real-time sync)
- **ETA Calculation**: Based on dummy distance (< 0.03 = 20 min, < 0.07 = 40 min, else 60 min)
- **Doctor Availability**: Fixed tele-slots (no booking system)
- **Pricing**: Mock prices in INR (Indian Rupees)

---

## 🛠️ Development

### Adding New Agents

1. Create agent class in `Agents/` (follow existing patterns)
2. Implement main method with clear JSON input/output contract
3. Add structured logging via `get_logger(__name__)`
4. Write unit tests in `tests/unit/`
5. Write integration tests for handoffs in `tests/integration/`
6. Update orchestrator to call new agent in flow

### Adding New Data

1. Place CSV/JSON files in `Data/`
2. Add loader function in `Utils/data_loader.py`
3. Update relevant agent to consume new data
4. Add test fixtures in `tests/`

---

## 📦 Deployment

### Streamlit Community Cloud

This app is deployed at: **https://multi-ai-agent-doctor-by-vidisha.streamlit.app/**

**Deployment steps:**
1. Push code to GitHub
2. Connect repo to Streamlit Community Cloud
3. Set Python version to 3.10+
4. Deploy from `app.py`

### Alternative Platforms

- **Render**: Free tier, connect GitHub repo
- **Heroku**: Use Procfile with `web: streamlit run app.py --server.port=$PORT`
- **AWS EC2**: Docker container with Streamlit

---

## 🎓 Educational Context

This project was built as a **proof-of-concept for a multi-agent healthcare system** to demonstrate:

- Modular agent architecture with clear separation of concerns
- Safe AI triage with human-in-the-loop escalation
- Privacy-first design (PII masking, anonymous uploads)
- Integration testing for agent handoffs
- Observable, debuggable system design (timeline, JSON logs)
- Streamlit UI for rapid prototyping

**Key Learning Outcomes:**
- Multi-agent orchestration patterns
- Healthcare data handling (safety checks, red flags)
- CSV/JSON data modeling
- Python testing (pytest, fixtures, integration tests)
- Streamlit UI development
- Deployment to cloud platforms

---

## 📝 Citation

If you reference this project, please cite:

```
Multi-Agent Healthcare Assistant POC
Author: Vidisha Arvind
Year: 2025
GitHub: https://github.com/Vibhuarvind/Multi_AI_Agent_Medical_Assistant
Demo: https://multi-ai-agent-doctor-by-vidisha.streamlit.app/
```

---

## 📄 License

**Educational project - not for commercial use.**

This is a portfolio/demonstration project. No warranties or guarantees are provided. Use at your own risk.

---

## 🤝 Contributing

This is a demonstration project, but feedback and suggestions are welcome!

---

## 📞 Contact

For questions about this project:

**GitHub Issues**: [Open an issue](https://github.com/your-username/your-repo/issues)


---

## 🙏 Acknowledgments

- Mock data inspired by real OTC formularies and pharmacy networks
- ChestX-ray dataset references for future ML integration
- Streamlit community for rapid prototyping tools

---

**Built with ❤️ for safe, intelligent healthcare automation**
