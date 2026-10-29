from dataclasses import dataclass
import hashlib

@dataclass
class ElementoRegistro:
    tipo: str          # "COMPITO" o "AVVISO"
    materia: str
    descrizione: str
    data_evento: str   # Data di consegna o di pubblicazione

    @property
    def id_univoco(self) -> str:
        """Genera un hash univoco per evitare messaggi duplicati."""
        raw_str = f"{self.tipo}:{self.materia.strip().lower()}:{self.data_evento}:{self.descrizione.strip().lower()}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()