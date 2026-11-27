import os
from dotenv import load_dotenv

load_dotenv()

VWORLD_API_KEY: str = os.getenv("VWORLD_API_KEY", "")
VWORLD_DOMAIN: str = os.getenv("VWORLD_DOMAIN", "localhost")

# Hugging Face Hub repo holding the DeepSolar-3M weights, e.g. "<user>/deepsolar-3m".
DEEPSOLAR_HF_REPO: str = os.getenv("DEEPSOLAR_HF_REPO", "")

# Comma-separated list of browser origins allowed to call the API.
_DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173,http://localhost:5174,http://localhost:3000,"
    "https://solarfit-beta.vercel.app"
)
CORS_ALLOW_ORIGINS: list[str] = [
    o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", _DEFAULT_CORS_ORIGINS).split(",") if o.strip()
]

VWORLD_DATA_URL = "https://api.vworld.kr/req/data"
VWORLD_SEARCH_URL = "https://api.vworld.kr/req/search"
VWORLD_GEOCODER_URL = "https://api.vworld.kr/req/address"

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
OPENTOPODATA_URL = "https://api.opentopodata.org/v1/srtm90m"

HAENAM_CENTER = (34.57, 126.60)
SUBSTATIONS_CSV = "data/substations.csv"
