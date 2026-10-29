import httpx
from config import Config

print("🔍 ANALISI REINDIRIZZAMENTI 302 E RISPOSTA FINALE ARGO\n" + "="*50)

endpoints = [
    "https://www.portaleargo.it/argoweb/famiglia/api/rest/v2/login",
    "https://www.portaleargo.it/argoweb/famiglia/api/rest/login"
]

headers = {
    "x-cod-scuola": Config.ARGO_CODICE_SCUOLA,
    "x-key-app": "argo_app_famiglia",
    "x-version-app": "2.1.0",
    "x-produttore-app": "Argo Software s.r.l.",
    "User-Agent": "okhttp/3.12.1",
    "Accept": "application/json, text/plain, */*"
}

params = {
    "cod_scuola": Config.ARGO_CODICE_SCUOLA,
    "des_user": Config.ARGO_USERNAME,
    "des_pwd": Config.ARGO_PASSWORD
}

with httpx.Client(timeout=10.0, follow_redirects=True) as client:
    for url in endpoints:
        print(f"\n🌐 Endpoint di partenza: {url}")
        
        # Test GET con reindirizzamento
        print("\n--- TEST GET ---")
        try:
            res_get = client.get(url, params=params, headers=headers)
            for h in res_get.history:
                print(f"   [Redirect {h.status_code}] -> {h.headers.get('location')}")
            print(f"   Status Finale: {res_get.status_code}")
            print(f"   URL Finale:    {res_get.url}")
            print(f"   Content-Type:  {res_get.headers.get('content-type')}")
            print(f"   Body:          {res_get.text[:300]}")
        except Exception as e:
            print(f"   Errore GET: {e}")

        # Test POST con reindirizzamento
        print("\n--- TEST POST ---")
        try:
            res_post = client.post(url, json=params, headers=headers)
            for h in res_post.history:
                print(f"   [Redirect {h.status_code}] -> {h.headers.get('location')}")
            print(f"   Status Finale: {res_post.status_code}")
            print(f"   URL Finale:    {res_post.url}")
            print(f"   Content-Type:  {res_post.headers.get('content-type')}")
            print(f"   Body:          {res_post.text[:300]}")
        except Exception as e:
            print(f"   Errore POST: {e}")

print("\n" + "="*50)