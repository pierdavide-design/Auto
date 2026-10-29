import os
from sys import exit
from dotenv import load_dotenv

load_dotenv()

class Config:
    ARGO_CODICE_SCUOLA: str = os.getenv("ARGO_CODICE_SCUOLA", "")
    ARGO_USERNAME: str = os.getenv("ARGO_USERNAME", "")
    ARGO_PASSWORD: str = os.getenv("ARGO_PASSWORD", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    @classmethod
    def validate(cls):
        missing = [k for k, v in cls.__dict__.items() if not k.startswith("__") and not v and isinstance(v, str)]
        if missing:
            print(f"[ERRORE] Variabili mancanti nel file .env: {', '.join(missing)}")
            exit(1)

Config.validate()