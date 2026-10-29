import sqlite3
import os

class StorageService:
    def __init__(self, db_path: str = "data/registro.db"):
        self.db_path = db_path
        # Assicura che la cartella data esista
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Crea la tabella se non esiste già."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS elementi_inviati (
                    id_hash TEXT PRIMARY KEY,
                    tipo TEXT,
                    materia TEXT,
                    data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def gia_inviato(self, id_hash: str) -> bool:
        """Verifica se un elemento è già stato elaborato e inviato."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM elementi_inviati WHERE id_hash = ?", (id_hash,))
            return cursor.fetchone() is not None

    def salva_inviato(self, id_hash: str, tipo: str, materia: str):
        """Registra un nuovo elemento come inviato."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO elementi_inviati (id_hash, tipo, materia) VALUES (?, ?, ?)",
                (id_hash, tipo, materia)
            )
            conn.commit()