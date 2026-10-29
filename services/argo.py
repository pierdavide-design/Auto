import re
import httpx
from datetime import datetime
from config import Config
from models import ElementoRegistro

class ArgoService:
    def __init__(self):
        # Manteniamo la sessione HTTP e i cookie per l'intero ciclo di vita
        self.client = httpx.Client(timeout=15.0, follow_redirects=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        self.logged_in = False

    def _login(self) -> bool:
        """Gestisce in automatico il flusso SSO completo di Argo."""
        try:
            # 1. Richiesta iniziale per ottenere la pagina di login SSO con il login_challenge
            start_url = "https://www.portaleargo.it/argoweb/famiglia/api/rest/v2/login"
            res_init = self.client.get(start_url, headers=self.headers)
            
            login_url = str(res_init.url)
            html = res_init.text

            # 2. Estrazione automatica dei campi dal form di login
            payload = {
                "cod_scuola": Config.ARGO_CODICE_SCUOLA,
                "username": Config.ARGO_USERNAME,
                "password": Config.ARGO_PASSWORD,
                "des_user": Config.ARGO_USERNAME,
                "des_pwd": Config.ARGO_PASSWORD,
            }

            # Cerca eventuali token/campi nascosti generati dal server SSO
            for match in re.finditer(r'<input[^>]+name=["\']([^"\']+)["\'][^>]+value=["\']([^"\']*)["\']', html):
                name, val = match.group(1), match.group(2)
                if name not in payload:
                    payload[name] = val

            # 3. Invio delle credenziali al form SSO
            res_post = self.client.post(login_url, data=payload, headers=self.headers)
            
            # Verifica che il login sia andato a buon fine
            if res_post.status_code == 200:
                self.logged_in = True
                print("[ARGO] Autenticazione SSO completata con successo!")
                return True
            else:
                print(f"[ERRORE ARGO LOGIN] Status: {res_post.status_code}")
                return False

        except Exception as e:
            print(f"[ERRORE ARGO] Login SSO fallito: {e}")
            return False

    def get_compiti(self) -> list[ElementoRegistro]:
        """Recupera i compiti utilizzando la sessione autenticata."""
        if not self.logged_in and not self._login():
            return []

        elementi = []
        oggi = datetime.now().strftime("%Y-%m-%d")
        url_compiti = "https://www.portaleargo.it/argoweb/famiglia/api/rest/v2/compiti"
        
        try:
            res = self.client.get(url_compiti, headers={"Accept": "application/json"})
            if res.status_code == 200 and "json" in res.headers.get("content-type", ""):
                dati = res.json().get("dati", [])
                for item in dati:
                    elementi.append(
                        ElementoRegistro(
                            tipo="COMPITO",
                            materia=item.get("desMateria", "Generale"),
                            descrizione=item.get("desCompito", ""),
                            data_evento=item.get("datCompiti", oggi)
                        )
                    )
            elif res.status_code == 401:
                self.logged_in = False
        except Exception as e:
            print(f"[ERRORE ARGO] Lettura compiti fallita: {e}")

        return elementi