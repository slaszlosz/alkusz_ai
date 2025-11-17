# AlkuszAI - Vállalati Tudásbázis Chatbot

Egy modern, RAG (Retrieval Augmented Generation) alapú chatbot alkalmazás, amely vállalati dokumentumokból nyert tudást használ fel válaszadásra. Kifejezetten biztosítási alkusz cégek számára lett tervezve, de bármilyen dokumentum-alapú tudásbázis kezelésére alkalmas.

## Funkciók

- **Chat interfész**: AI asszisztens streaming válaszokkal, amely a feltöltött dokumentumok alapján válaszol
- **Dokumentum feltöltés**: PDF, DOCX, TXT fájlok feltöltése és automatikus feldolgozása
- **Vektor keresés**: Szemantikus keresés a dokumentumokban OpenAI embeddings használatával
- **Forrás hivatkozások**: Minden válaszhoz pontos forrás megjelölés (fájlnév + oldalszám + relevancia score)
- **Kategorizálás**: Dokumentumok csoportosítása (pl. biztosító neve szerint)
- **Dokumentum kezelés**: Feltöltött dokumentumok listázása, letöltése, törlése
- **Streaming válaszok**: Valós idejű szövegfolyam, mint a ChatGPT
- **Session kezelés**: Beszélgetések mentése és folytatása
- **Monitoring Dashboard**: Token használat, költségek, latencia metrikák követése
- **Evaluation Framework**: Háromszintű kiértékelési rendszer (RAG, Prompt, Application)

## Technológiai Stack

### Backend
- **FastAPI** - Modern, gyors Python web framework
- **OpenAI API** - GPT-4o-mini és text-embedding-3-large
- **ChromaDB** - Vektor adatbázis cosine similarity-vel
- **SQLite** - Metadata és session tárolás (async SQLAlchemy)
- **LangChain** - RAG pipeline orchestration
- **PyPDF & python-docx** - Dokumentum feldolgozás
- **Tiktoken** - Token counting
- **Server-Sent Events** - Streaming támogatás

### Frontend
- **React 18** + **TypeScript**
- **Vite** - Gyors fejlesztői környezet
- **Lucide React** - Ikonok
- **React Markdown** - Formázott válaszok
- **Axios** - API kommunikáció

## Telepítés és Futtatás

### Előfeltételek

- **Python 3.11+**
- **Node.js 20+**
- **OpenAI API kulcs** ([szerezd be itt](https://platform.openai.com/api-keys))

### 1. Repository klónozása

```bash
git clone <repository-url>
cd alkusz_ai
```

### 2. Környezeti változók beállítása

Hozz létre egy `.env` fájlt a projekt gyökérkönyvtárában:

```bash
cp .env.example .env
```

Szerkeszd a `.env` fájlt és add meg az OpenAI API kulcsodat:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Backend indítása

#### Windows PowerShell / CMD:

```bash
cd backend

# Virtuális környezet létrehozása
python -m venv venv

# Aktiválás (PowerShell)
.\venv\Scripts\Activate.ps1

# Aktiválás (CMD)
venv\Scripts\activate.bat

# Függőségek telepítése
pip install -r requirements.txt

# Szerver indítása
cd ..
python -m uvicorn app.main:app --reload --app-dir backend
```

#### Linux / macOS:

```bash
cd backend

# Virtuális környezet létrehozása
python3 -m venv venv

# Aktiválás
source venv/bin/activate

# Függőségek telepítése
pip install -r requirements.txt

# Szerver indítása
cd ..
uvicorn app.main:app --reload --app-dir backend
```

A backend elérhető lesz a `http://localhost:8000` címen.
API dokumentáció: `http://localhost:8000/docs`

### 4. Frontend indítása

Új terminálban:

```bash
cd frontend

# Függőségek telepítése
npm install

# Development szerver indítása
npm run dev
```

A frontend elérhető lesz a `http://localhost:5173` címen.

### 5. Docker használata (opcionális)

Ha van Docker és Docker Compose a gépeden:

```bash
# Alkalmazás indítása
docker-compose up --build

# Háttérben futtatás
docker-compose up -d

# Leállítás
docker-compose down
```

## Használat

### 1. Dokumentum feltöltése

1. Nyisd meg az alkalmazást: `http://localhost:5173`
2. Kattints a **"Feltöltés"** menüpontra
3. Válassz vagy húzz be egy dokumentumot (PDF, DOCX, TXT)
4. Opcionálisan adj meg kategóriát (pl. "Uniqua", "Generali")
5. Kattints a **"Feltöltés és feldolgozás"** gombra
6. Várj, amíg a feldolgozás befejeződik

### 2. Chatbot használata

1. Menj a **"Chat"** oldalra
2. Írj be egy kérdést, például:
   - "Uniqua basic casco biztosítás mennyit térít jégkárra?"
   - "Milyen kiegészítő csomagok érhetőek el?"
   - "Mi a különbség a basic és premium csomag között?"
3. Az AI válaszol, és megjelöli a forrásokat
4. Kattints a forrásra a dokumentum letöltéséhez

### 3. Dokumentumok kezelése

- **"Dokumentumok"** oldalon láthatod az összes feltöltött fájlt
- Letöltheted vagy törölheted őket
- Lásd a feldolgozási státuszt és statisztikákat

### 4. Metrikák Dashboard

- **"Metrikák"** oldalon valós idejű monitoring
- Token használat és költségek (USD)
- Válaszidő metrikák (total, first token, retrieval)
- Performance breakdown vizualizációk
- Időszűrés (1 óra, 24 óra, összes idő)

## Példa használat - Biztosítási alkusz

**Szcenárió:** Feltöltöttünk 3 biztosító casco katalógusát.

**Kérdés:**
> Uniqua basic casco biztosítás mennyit térít jégkárra?

**AI válasz:**
> A Uniqua Basic Casco biztosítás jégkár esetén a kár 100%-át téríti, maximum 500.000 Ft értékhatárig. A kártérítés önrészmentesen történik, ha az éves díj időarányos része már be lett fizetve.
>
> **Források:**
> - uniqua_basic_casco_katalogus.pdf - 8. oldal (95% relevancia)

**Működés:**
- A felhasználó rákattint a forrásra
- Automatikusan letöltődik a PDF
- Böngészőben megnyílik a 8. oldalon (ha a böngésző támogatja)

## Projekt Struktúra

```
alkusz_ai/
├── backend/
│   ├── app/
│   │   ├── api/                    # API endpointok
│   │   │   ├── chat.py             # Chat API (streaming + non-streaming)
│   │   │   ├── documents.py        # Dokumentum API
│   │   │   ├── evaluation.py       # Evaluation API
│   │   │   └── metrics.py          # Metrics API
│   │   ├── core/                   # Központi logika
│   │   │   ├── config.py           # Konfigurációk
│   │   │   ├── rag.py              # RAG pipeline (streaming support)
│   │   │   └── metrics.py          # Metrics tracking
│   │   ├── db/                     # Adatbázis
│   │   │   ├── database.py         # Async DB kapcsolat
│   │   │   └── models.py           # SQLAlchemy modellek (Conversation, Message)
│   │   ├── evaluation/             # Evaluation Framework
│   │   │   ├── rag_eval.py         # RAG-level (precision, recall, MRR)
│   │   │   ├── prompt_eval.py      # Prompt-level (LLM-as-Judge)
│   │   │   ├── app_eval.py         # Application-level (user journeys)
│   │   │   └── mock_results.py     # Mock eredmények
│   │   ├── services/               # Szolgáltatások
│   │   │   ├── document_processor.py  # Token-based chunking
│   │   │   └── vector_store.py        # ChromaDB integration
│   │   └── main.py                 # FastAPI app
│   ├── evaluation_tests/           # Teszt esetek (70 db)
│   │   ├── rag_test_cases.json
│   │   ├── prompt_test_cases.json
│   │   └── app_test_cases.json
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/           # Chat komponensek (streaming support)
│   │   │   ├── Upload/         # Feltöltés komponensek
│   │   │   ├── Documents/      # Dokumentum lista
│   │   │   └── Metrics/        # Monitoring Dashboard
│   │   ├── lib/
│   │   │   └── api.ts          # API kommunikáció (axios + types)
│   │   ├── App.tsx             # Fő komponens (routing)
│   │   └── index.css           # Stílusok
│   ├── package.json
│   └── Dockerfile
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── GYORS_TELEPITES.md
├── PROJEKTOSSZEFOGLALO.md
└── ZAROFELADAT_DOKUMENTACIO.md
```

## API Endpointok

### Chat API

- `POST /api/chat/` - Üzenet küldése (non-streaming)
- `POST /api/chat/stream` - Üzenet küldése (streaming SSE)
- `GET /api/chat/conversations` - Beszélgetések listája
- `GET /api/chat/conversations/{id}` - Beszélgetés részletei

### Documents API

- `POST /api/documents/upload` - Dokumentum feltöltése
- `GET /api/documents/` - Dokumentumok listázása
- `GET /api/documents/{id}` - Dokumentum részletei
- `GET /api/documents/{id}/download` - Dokumentum letöltése
- `DELETE /api/documents/{id}` - Dokumentum törlése
- `GET /api/documents/stats/overview` - Statisztikák

### Metrics API

- `GET /api/metrics/stats?hours={n}` - Metrikák lekérése
- `GET /api/metrics/health` - Metrika rendszer health check

### Evaluation API

- `POST /api/evaluation/rag` - RAG-level értékelés (precision, recall, MRR)
- `POST /api/evaluation/prompt` - Prompt-level értékelés (LLM-as-Judge)
- `POST /api/evaluation/application` - Application-level értékelés (user journeys)
- `POST /api/evaluation/full` - Teljes 3-szintű kiértékelés
- `GET /api/evaluation/summary` - Evaluation framework összefoglaló

## Konfigurációs Lehetőségek

### Környezeti változók (.env)

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=sqlite+aiosqlite:///./alkusz_ai.db

# Chroma
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### RAG Pipeline beállítások

A `backend/app/core/rag.py` fájlban módosíthatod:
- **Model**: `gpt-4o-mini` (jelenleg - gyors és költséghatékony)
- **Temperature**: 0.3 (precízebb válaszok)
- **Max tokens**: 1000
- **Embedding model**: `text-embedding-3-large` (3072 dimenziós, legjobb minőség)
- **Streaming**: Server-Sent Events (SSE) támogatással

### Chunkolás beállítások

A `backend/app/services/document_processor.py` fájlban:
- **Chunk size**: 1000 token
- **Chunk overlap**: 200 token

## Hibaelhárítás

### Backend nem indul

**Probléma:** `ModuleNotFoundError: No module named 'app'`

**Megoldás:**
```bash
# Ellenőrizd, hogy a backend/app mappában vagy-e a __init__.py fájlok
# Indítsd a szervert a projekt gyökérkönyvtárából:
python -m uvicorn app.main:app --reload --app-dir backend
```

### OpenAI API hiba

**Probléma:** `AuthenticationError: Incorrect API key`

**Megoldás:**
- Ellenőrizd a `.env` fájlban az API kulcsot
- Győződj meg róla, hogy van kreditje az OpenAI fiókodban
- Teszteld a kulcsot: https://platform.openai.com/api-keys

### Frontend nem kapcsolódik a backendhez

**Probléma:** `Network Error` vagy CORS hiba

**Megoldás:**
- Ellenőrizd, hogy a backend fut-e (`http://localhost:8000/health`)
- Nézd meg a `backend/app/core/config.py`-ban a CORS beállításokat
- Győződj meg róla, hogy a frontend a helyes porton fut (5173)

### Dokumentum feltöltés sikertelen

**Probléma:** "Error processing document"

**Megoldás:**
- Ellenőrizd a fájl formátumot (csak PDF, DOCX, TXT támogatott)
- Nézd meg a fájl méretét (max 10MB)
- Ellenőrizd, hogy van-e írási jogosultság az `uploads/` mappában

## Költségbecslés (OpenAI API)

### Embedding költségek
- Model: `text-embedding-3-large`
- Ár: $0.13 / 1M token
- 100 dokumentum (~10,000 oldal): **~$5-10**

### Chat költségek
- Model: `gpt-4o-mini`
- Ár: $0.15 / 1M input token, $0.60 / 1M output token
- 1000 kérdés (átlag 2000 token kontextus): **~$0.30-0.60/hó**
- **98% olcsóbb** mint a GPT-4 Turbo!

### Valós példa
- 70 evaluation teszteset futtatása: ~$0.05
- 100 chat kérdés: ~$0.03-0.06
- Monitoring Dashboard: költségmentes (csak query tracking)

### Optimalizálás
- A GPT-4o-mini már nagyon költséghatékony
- Helyi modellek (Ollama + Llama) 0 költséggel, de gyengébb minőség
- Monitoring Dashboard segít a költségek követésében

## Továbbfejlesztési Lehetőségek

- [x] Streaming válaszok (mint ChatGPT)
- [x] Session kezelés és beszélgetési előzmények
- [x] Monitoring Dashboard (token, költség, latencia)
- [x] Evaluation Framework (3-szintű kiértékelés)
- [ ] Multi-user támogatás és autentikáció
- [ ] Kategória alapú szűrés a chatben
- [ ] Dokumentum összehasonlítás funkció
- [ ] PDF megjelenítő a böngészőben
- [ ] Több LLM provider támogatás (Anthropic, Gemini)
- [ ] Helyi modellek támogatása (Ollama)
- [ ] Beszélgetés export (PDF, Word)
- [ ] Admin dashboard felhasználó kezeléshez
- [ ] A/B testing különböző prompt stratégiákhoz

## Licenc

MIT License - szabadon használható és módosítható.

## Támogatás

Problémák esetén nyiss egy issue-t a GitHub repository-ban.

---

**Készítette:** AlkuszAI - Zárófeladat projekt
**Verzió:** 2.0.0 (Streaming + Monitoring + Evaluation)
**Utolsó frissítés:** 2025 november
