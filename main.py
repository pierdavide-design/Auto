import time
import random
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from config import Config
from services.argo import ArgoService
from services.gemini import GeminiService
from services.whatsapp import WhatsAppService
from storage import StorageService

argo = ArgoService()
gemini = GeminiService()
whatsapp = WhatsAppService(node_server_url="http://localhost:3000")
db = StorageService()

def ciclo_controllo():
    ora_attuale = datetime.now().hour
    if ora_attuale >= 22 or ora_attuale < 6:
        print("[SCHEDULER] Pausa notturna attiva.")
        return

    time.sleep(random.randint(0, 120))
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Avvio controllo registro...")
    
    try:
        elementi = argo.get_compiti()
        for item in elementi:
            if not db.gia_inviato(item.id_univoco):
                # Smistamento: "Compiti" per i compiti, "Comunicazioni" per gli avvisi
                gruppo_destinazione = "Compiti" if item.tipo == "COMPITO" else "Comunicazioni"
                
                # Formattazione e invio
                testo_formattato = gemini.formatta_elemento(item)
                esito = whatsapp.invia_messaggio(testo_formattato, group_name=gruppo_destinazione)
                
                if esito:
                    db.salva_inviato(item.id_univoco, item.tipo, item.materia)
                    print(f"[OK] Inviato a {gruppo_destinazione}: {item.materia}")
                
                time.sleep(3)
    except Exception as e:
        print(f"[ERRORE GENERALE] {e}")

if __name__ == "__main__":
    print("🤖 Bot Argo-WhatsApp avviato con successo!")
    ciclo_controllo()
    
    scheduler = BlockingScheduler()
    scheduler.add_job(ciclo_controllo, 'interval', minutes=15)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[BOT] Arresto eseguito.")