from google import genai
from config import Config
from models import ElementoRegistro

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

    def formatta_elemento(self, elemento: ElementoRegistro) -> str:
        """Formatta l'elemento in un messaggio leggibile per WhatsApp."""
        prompt = (
            f"Sei un assistente per un gruppo scolastico WhatsApp.\n"
            f"Formatta il seguente elemento di registro in modo chiaro, ordinato ed elegante usando la sintassi Markdown di WhatsApp (*grassetto*, _corsivo_).\n\n"
            f"Tipo: {elemento.tipo}\n"
            f"Materia: {elemento.materia}\n"
            f"Data: {elemento.data_evento}\n"
            f"Descrizione: {elemento.descrizione}\n\n"
            f"Genera SOLO il testo del messaggio finale senza spiegazioni o preamboli."
        )
        try:
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"[ERRORE GEMINI] Impossibile formattare il testo: {e}")
            emoji = "📌" if elemento.tipo == "COMPITO" else "📢"
            return (
                f"{emoji} *{elemento.tipo} - {elemento.materia}*\n"
                f"📅 *Data:* {elemento.data_evento}\n\n"
                f"{elemento.descrizione}"
            )