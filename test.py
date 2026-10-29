import httpx
from models import ElementoRegistro
from services.gemini import GeminiService

gemini = GeminiService()
URL_NODE = "http://localhost:3000/send"

print("🧪 Avvio test di invio messaggi...\n")

# Test 1: Compito
compito = ElementoRegistro(
    tipo="COMPITO",
    materia="Matematica",
    descrizione="Esercizi pag. 104 n. 12, 15 e 18 su equazioni di secondo grado.",
    data_evento="2026-10-30"
)

print("1. Formattazione e invio COMPITO nel canale 'Compiti'...")
testo_compito = gemini.formatta_elemento(compito)
print(f"--- Testo generato da Gemini ---\n{testo_compito}\n-------------------------------")

payload_compito = {
    "group_name": "Compiti",
    "message": testo_compito
}

try:
    res = httpx.post(URL_NODE, json=payload_compito, timeout=10.0)
    print(f"Risposta Node: Status {res.status_code} - {res.text}\n")
except Exception as e:
    print(f"[ERRORE CONNESSIONE NODE]: {e}\n")


# Test 2: Avviso
avviso = ElementoRegistro(
    tipo="AVVISO",
    materia="Generale",
    descrizione="Si comunica che domani la classe uscirà alle ore 12:00 per assemblea d'istituto.",
    data_evento="2026-10-30"
)

print("2. Formattazione e invio AVVISO nel canale 'Comunicazioni'...")
testo_avviso = gemini.formatta_elemento(avviso)
print(f"--- Testo generato da Gemini ---\n{testo_avviso}\n-------------------------------")

payload_avviso = {
    "group_name": "Comunicazioni",
    "message": testo_avviso
}

try:
    res = httpx.post(URL_NODE, json=payload_avviso, timeout=10.0)
    print(f"Risposta Node: Status {res.status_code} - {res.text}\n")
except Exception as e:
    print(f"[ERRORE CONNESSIONE NODE]: {e}\n")