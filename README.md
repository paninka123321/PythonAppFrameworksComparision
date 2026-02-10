# Instrukcja Uruchamiania Aplikacji — Porównanie Framework'ów Django, Flask, FastAPI

## 📋 Konfiguracja Portów

Aby uniknąć konfliktów, aplikacje uruchamiają się na następujących portach:

| Framework | Backend | Frontend (React) | HTML Panel |
|-----------|---------|------------------|-----------|
| **Django** | 8002 | 5174 | http://127.0.0.1:8002/staff/tasks/ |
| **Flask** | 8003 | 5175 | (brak) |
| **FastAPI** | 8001 | 5173 | http://127.0.0.1:8001/staff/tasks/ |

## 🚀 Uruchomienie Aplikacji

### 1. FastAPI (Port 8001)

**Backend:**
```bash
cd FastAPI
python3 main.py
```
Serwer dostępny: `http://127.0.0.1:8001`

**Frontend (React):**
```bash
cd FastAPI/frontend
npm install  # (tylko za pierwszym razem)
npm run dev
```
Aplikacja dostępna: `http://localhost:5173`

**HTML Panel (bez React):**
```
http://127.0.0.1:8001/staff/tasks/
```

---

### 2. Django (Port 8002)

**Backend:**
```bash
cd Django/projekt_firmowy
python3 manage.py runserver 8002
```
Serwer dostępny: `http://127.0.0.1:8002`

**Frontend (React):**
```bash
cd Django/projekt_firmowy/frontend
npm install  # (tylko za pierwszym razem)
npm run dev -- --port 5174
```
Aplikacja dostępna: `http://localhost:5174`

**HTML Panel (bez React):**
```
http://127.0.0.1:8002/staff/tasks/
```

---

### 3. Flask (Port 8003)

**Backend:**
```bash
cd Flask
python3 app.py
```
Serwer dostępny: `http://127.0.0.1:8003`

**Frontend (React):**
```bash
cd Flask/frontend
npm install  # (tylko za pierwszym razem)
npm run dev -- --port 5175
```
Aplikacja dostępna: `http://localhost:5175`

---

## 🔐 Domyślne Dane Logowania

### FastAPI & Django & Flask
- **Login:** `admin` | **Hasło:** `adminpassword`
- **Login:** `adam` | **Hasło:** `password`

### Flask
(Zobacz `Flask/app.py` — sekcja `@app.before_request` dla użytkowników)

---

## 🎨 Motyw Wspólny

Wszystkie aplikacje używają tego samego motywu CSS (zmienne kolorów, czcionki, stylizacja):
- Kolor tła: `#0f1724`
- Akcent: `#4f8cff`
- Tekst: `#e6eef8`

Pliki CSS:
- Django/FastAPI frontendy: `src/theme.css`
- Django/FastAPI szablony HTML: `static/theme.css`

---

## 📱 Responsywność

Wszystkie aplikacje są responsywne — testuj na różnych szerokościach okna (mobile, tablet, desktop).

---

## ✅ Sprawdzenie Wizualne

1. Otwórz każdą aplikację w przeglądarce:
   - FastAPI React: `http://localhost:5173`
   - Django React: `http://localhost:5174`
   - Flask React: `http://localhost:5175`
   - FastAPI HTML: `http://127.0.0.1:8001/staff/tasks/`
   - Django HTML: `http://127.0.0.1:8002/staff/tasks/`

2. Sprawdź:
   - ✅ Spójność kolorów między aplikacjami
   - ✅ Działanie logowania (użyj danych wyżej)
   - ✅ Wyświetlanie danych z API
   - ✅ Responsywność (zmień rozmiar okna)
   - ✅ Ładowanie motywu CSS

---

## 🐛 Rozwiązywanie Problemów

### Port już w użyciu
```bash
# Znajdź proces na porcie (macOS/Linux)
lsof -i :port

# Zabij proces (zamień PID na znaleziony)
kill -9 <PID>
```

### `npm install` nie działa
```bash
# Upewnij się, że Node.js jest zainstalowany
node --version
npm --version

# Jeśli nie, zainstaluj z https://nodejs.org/
```

### CORS błędy w konsoli przeglądarki
- Upewnij się, że backendy mają CORS włączony (są)
- Sprawdź, czy port frontendu jest w `CORS_ALLOWED_ORIGINS` (settings.py) — dla Django

### Aplikacja się nie ładuje
- Sprawdź konsolę przeglądarki (F12 → Console) czy są błędy
- Sprawdź terminal backendu czy są błędy

