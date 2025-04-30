from enum import Enum
import os

class ServiceType(str, Enum):
    TITANIC = "titanic"
    CRIME = "crime"
    MATZIP = "matzip"

def format_url(url: str) -> str:
    if url and not url.startswith("http"):
        return f"http://{url}"
    return url

TITANIC_SERVICE_URL = format_url(os.getenv("TITANIC_SERVICE_URL"))
CRIME_SERVICE_URL = format_url(os.getenv("CRIME_SERVICE_URL"))
MATZIP_SERVICE_URL = format_url(os.getenv("MATZIP_SERVICE_URL"))

SERVICE_URLS = {
    ServiceType.TITANIC: TITANIC_SERVICE_URL,
    ServiceType.CRIME: CRIME_SERVICE_URL,
    ServiceType.MATZIP: MATZIP_SERVICE_URL,
}
