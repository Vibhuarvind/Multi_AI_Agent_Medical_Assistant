"""Application constants and configuration values."""

# File paths
DATA_DIR = "Data"
UPLOADS_DIR = "tmp"
MEDICINES_FILE = f"{DATA_DIR}/medicines.csv"
PHARMACIES_FILE = f"{DATA_DIR}/pharmacies.json"
DOCTORS_FILE = f"{DATA_DIR}/doctors.csv"
INTERACTIONS_FILE = f"{DATA_DIR}/interactions.csv"
INVENTORY_FILE = f"{DATA_DIR}/inventory.csv"
ZIPCODES_FILE = f"{DATA_DIR}/zipcodes.csv"

# Upload directories
IMAGES_DIR = f"{UPLOADS_DIR}/images"
PDFS_DIR = f"{UPLOADS_DIR}/pdfs"

# Patient constraints
MAX_AGE = 120
MIN_AGE = 0
DEFAULT_AGE = 30

# Business rules
PHONE_DIGITS = 10
PHARMACY_MAX_DISTANCE_KM = 50
UUID_SHORT_LENGTH = 6

# Interaction severity levels
INTERACTION_HIGH = "High"
INTERACTION_MODERATE = "Moderate"
INTERACTION_LOW = "Low"

# Severity levels
SEVERITY_SEVERE = "severe"
SEVERITY_MODERATE = "moderate"
SEVERITY_MILD = "mild"

# Condition labels
CONDITION_PNEUMONIA = "pneumonia"
CONDITION_COVID = "covid_suspect"
CONDITION_NORMAL = "normal"

