import httpx

class WhatsAppService:
    def __init__(self, node_server_url: str = "http://localhost:3000"):
        self.url = f"{node_server_url}/send-message"

    def invia_messaggio(self, testo: str, group_name: str) -> bool:
        """Invia la richiesta di spedizione specificando il gruppo di destinazione."""
        payload = {
            "groupName": group_name,
            "message": testo
        }
        try:
            response = httpx.post(self.url, json=payload, timeout=15.0)
            if response.status_code == 200:
                print(f"[WHATSAPP] Messaggio inviato a '{group_name}'.")
                return True
            else:
                print(f"[ERRORE NODE] Status: {response.status_code} - Dettagli: {response.text}")
                return False
        except httpx.RequestError as e:
            print(f"[ERRORE RETE] Impossibile contattare il server Node.js: {e}")
            return False