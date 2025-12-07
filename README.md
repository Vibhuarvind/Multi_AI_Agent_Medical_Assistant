# Multi-Agent Medical Assistant (POC)

A modular multi-agent system validating the "AI Medical Assistant" architecture for healthcare triage and fulfillment.

## Architecture

- **Ingestion Agent**: Validates files, extracts PDF text (mock OCR), masks PII (name/phone).
- **Imaging Agent**: Analyzes chest X-rays using filename-based logic for demo predictability.
- **Therapy Agent**: Maps conditions → OTC medicines, checks age/allergy constraints, screens drug interactions.
- **Pharmacy Match Agent**: Finds nearest pharmacy with stock using geo-matching + inventory lookup.
- **Coordinator (Orchestrator)**: Central hub that routes tasks, handles fallbacks, triggers doctor escalation.

**Data**: Local CSV/JSON mock database (`Data/` folder).  
**UI**: Streamlit with mobile-friendly sidebar inputs and customer-friendly outputs.

## Setup

### Prerequisites
- Python 3.10+
- pip or uv package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Multi_AI_Agent_Medical_Assistant

# Install dependencies
pip install -r requirements.txt
# OR if using uv:
uv sync

# Run the application
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### Safety First
- **Red-flags** for high severity cases (e.g., severe pneumonia, SpO2 < 92%)
- **Doctor escalation** with mock tele-consult roster when confidence < threshold
- **Drug interaction warnings** (High and Moderate levels surfaced to users)

### Privacy & Ethics
- **PII masking**: Names and phone numbers are masked in logs and UI
- **Anonymous uploads**: Files saved with patient name + short UUID, no real PHI stored
- **Prominent disclaimer**: "Educational demo, not medical advice" on every page

### Smart Fulfillment
- **Location-based pharmacy matching**: Finds nearest pharmacy with stock
- **ETA & delivery fee calculation**: Based on distance from patient
- **OTC-only recommendations**: No prescription drugs, safe for self-care

### Observability
- **Timeline tracking**: Logs each agent step (ingestion → imaging → therapy → pharmacy)
- **Full coordinator output**: JSON payload available for debugging
- **Terminal logging**: Detailed agent actions logged with timestamps

## Sample Workflow

1. **Patient inputs** name, age, phone, gender, allergies, symptoms
2. **Upload** chest X-ray image (e.g., `pneumonia_severe.jpg`)
3. **System analyzes**:
   - Ingestion: Validates, saves, masks PII
   - Imaging: Detects pneumonia (85% confidence), severity: severe
   - Therapy: Recommends Paracetamol, flags "SpO2 likely < 92%", avoids Ibuprofen (patient allergic)
   - Pharmacy: Matches MedQuick Andheri, ETA 20 min, ₹15 delivery
4. **Escalation triggered**: Shows available doctors (Dr. Asha Mehta, etc.) with appointment slots

## Project Structure

```
Multi_AI_Agent_Medical_Assistant/
├── Agents/              # Core agent implementations
├── Data/                # Mock data (medicines, pharmacies, doctors)
├── tmp/                 # Temporary file storage (images/PDFs)
├── tests/               # Unit & integration tests
├── docs/                # Screenshots, diagrams, presentation
├── app.py               # Streamlit UI
└── README.md            # This file
```

## Data Files

- `medicines.csv`: OTC drug formulary with age restrictions & contraindications
- `interactions.csv`: Drug interaction matrix (High/Moderate/Low)
- `pharmacies.json`: Mock pharmacy locations with services & delivery radius
- `inventory.csv`: Pharmacy stock levels per SKU
- `doctors.csv`: Mock doctor roster with specialties & tele-consult slots

## Known Limitations

- **Not for clinical use**: All logic is deterministic/mocked for demonstration
- **Mock X-ray analysis**: Uses filename keywords (e.g., "pneumonia") for predictable demos
- **No real OCR**: PDF text extraction returns placeholder text
- **No real geolocation**: Uses hardcoded lat/lon for demo
- **No payment integration**: Order placement is simulated

## Testing

Run unit tests for agent handoffs:

```bash
pytest tests/
```

## Deployment

Deployed to Streamlit Community Cloud: https://multi-ai-agent-doctor-by-vidisha.streamlit.app/

1. Push code to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Set main file: `app.py`
4. Deploy!

## Disclaimer

**⚠️ STRICTLY A PROOF OF CONCEPT**

This system is an educational demonstration only. It is **NOT** for clinical use. All diagnosis, treatment suggestions, and pharmacy recommendations are simulated using mock data and rule-based logic. Always consult a qualified healthcare provider for medical advice, diagnosis, or treatment.

## License

Educational project - not for commercial use.

