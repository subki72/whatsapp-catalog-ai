# Code Readability Audit

Stack terdeteksi: Python 3.10 (FastAPI, SQLAlchemy, Pydantic v2, LangChain-Groq) + Vanilla JS/HTML/CSS
Style convention detected:
- Naming: Python `snake_case` / `PascalCase` class / `UPPER_SNAKE_CASE` konstanta; JS `camelCase`
- Indentation: 4 spasi (Python, JS, HTML, CSS), tanpa tab
- Line length: tidak dikonfigurasi; praktik dominan ≤ 100 karakter (12 baris > 120)

## Ringkasan
Total issue: **29** (Critical: 0, High: 3, Medium: 15, Low: 11)

Tidak ada temuan Critical: tidak ada variabel satu huruf di logika kompleks, nesting maksimum 4 level, function terpanjang ~80 baris.

## Issue

### [HIGH] R-01 — Naming (`product_name` sebenarnya menyimpan nama usaha)
**File:** `app/models/schema.py`, `app/models/pydantic_schemas.py`, `app/api/webhook.py`, `wa-catalog-frontend/app.js`
**Lokasi:** `schema.py` L10; `pydantic_schemas.py` L9; `webhook.py` L172-176, L215; `app.js` L159

**Masalah:**
Field bernama `product_name`, tetapi isinya nama **usaha** ("Nasi Goreng Gila Gondrong", "Kopi Senja Bahagia"). Label UI/WA menyebutnya "Nama Usaha", dan deskripsi field ragu-ragu "product or business". Daftar produk justru ada di `menus`.

**Contoh kode (sebelum):**
```python
product_name: str = Field(description="Name of the product or business")
...
clean_name = extracted_data["product_name"].strip()
...
f"🛍 Nama Usaha: {catalog.product_name}\n"
```

**Alasan kenapa ini readability issue:**
Pembaca baru akan mengira `product_name` = nama satu produk, lalu bingung kenapa logika upsert (webhook L174-177) mencocokkan katalog berdasarkan "nama produk".

**Rekomendasi:**
Tanpa migrasi DB (feasible): perjelas deskripsi + docstring kelas, dan pakai nama variabel lokal yang jujur. Rename kolom penuh bisa dijadwalkan terpisah.

**Contoh kode (sesudah):**
```python
class CatalogItem(BaseModel):
    """Structured catalog data extracted by the LLM.

    Note: `product_name` holds the *business* name (e.g. "Kopi Senja");
    individual products are listed in `menus`.
    """
    product_name: str = Field(description="Business / shop name")
...
business_name = extracted_data["product_name"].strip()
```

---

### [HIGH] R-02 — Structure (`background_process_wa_message` terlalu banyak tanggung jawab)
**File:** `app/api/webhook.py`
**Lokasi:** baris 151-230, function `background_process_wa_message`

**Masalah:**
Satu function ±80 baris dengan nesting 4 level (`try` → `try` → `if` → assignment) menangani: panggilan AI, klasifikasi error, pemilihan pesan maaf, query upsert, logging, penyusunan balasan, rollback, dan fallback error.

**Contoh kode (sebelum):**
```python
async def background_process_wa_message(sender: str, message: str):
    try:
        ...
        if extracted_data.get("product_name") == "Error":
            ...
            if "system" in usp.lower() or "limit" in usp.lower() or "fail" in usp.lower():
                user_msg = "..."
            else:
                user_msg = "..."
            ...
        db = SessionLocal()
        try:
            clean_name = ...
            existing_catalog = db.query(CatalogDB).filter(...).first()
            if not existing_catalog and clean_name.lower() in {...}:
                ...
            if existing_catalog:
                ... # 7 baris update
            else:
                ... # 10 baris insert
            db.commit()
            ...
            reply_text = (...)
```

**Alasan kenapa ini readability issue:**
Alur utama ("ekstrak → simpan → balas") tenggelam di detail; pembaca harus menelusuri seluruh function untuk tahu kapan balasan dikirim.

**Rekomendasi:**
Ekstrak 3 helper kecil tanpa mengubah perilaku.

**Contoh kode (sesudah):**
```python
async def background_process_wa_message(sender: str, message: str) -> None:
    try:
        extracted_data = await extractor.extract_catalog_data(message)
        if is_extraction_error(extracted_data):
            await send_whatsapp_reply(sender, build_extraction_error_reply(extracted_data))
            return

        with SessionLocal() as db:
            catalog, is_update = upsert_catalog(db, sender, extracted_data)
        logger.info("%s catalog ID %s", "Updated" if is_update else "Created", catalog.id)
        await send_whatsapp_reply(sender, build_success_reply(catalog, sender))
    except Exception as exc:
        logger.error("Webhook background error: %s", exc, exc_info=True)
        await send_whatsapp_reply(sender, INTERNAL_ERROR_REPLY)
```

---

### [HIGH] R-03 — Structure (kontrak error berbasis string sentinel tersembunyi antar modul)
**File:** `app/services/ai_extractor.py`, `app/api/webhook.py`
**Lokasi:** `ai_extractor.py` L21, L87-92, L121-126; `webhook.py` L160-166, L180

**Masalah:**
Extractor menandai gagal dengan `product_name == "Error"` dan teks bebas di `unique_selling_point`. Webhook menebak jenis error dengan substring `"system"`, `"limit"`, `"fail"`. Karena teks default extractor adalah `"Failed to extract data"` (mengandung "fail"), cabang `else` hampir tak pernah tercapai — maksud kode tidak terbaca. Daftar `{"not provided", "none", ""}` di webhook juga bergantung diam-diam pada teks prompt di extractor.

**Contoh kode (sebelum):**
```python
# ai_extractor.py
return {"product_name": "Error", ..., "unique_selling_point": "Failed to extract data"}

# webhook.py
if extracted_data.get("product_name") == "Error":
    usp = extracted_data.get("unique_selling_point", "")
    if "system" in usp.lower() or "limit" in usp.lower() or "fail" in usp.lower():
        ...
if not existing_catalog and clean_name.lower() in {"not provided", "none", ""}:
```

**Alasan kenapa ini readability issue:**
Kopling implisit: mengubah satu kata di extractor mengubah perilaku webhook tanpa ada referensi yang bisa ditelusuri (find-usages tidak menemukannya).

**Rekomendasi:**
Definisikan konstanta bersama di `ai_extractor.py` dan field eksplisit `error_type`.

**Contoh kode (sesudah):**
```python
# ai_extractor.py
EXTRACTION_ERROR = "Error"
MISSING_VALUE = "Not provided"          # or "Tidak disebutkan", see L-01
EMPTY_NAME_VALUES = {MISSING_VALUE.lower(), "none", ""}

def _error_result(error_type: str) -> dict:
    return {"product_name": EXTRACTION_ERROR, "location": EXTRACTION_ERROR,
            "menus": [], "unique_selling_point": "", "error_type": error_type}

# webhook.py
if extracted_data.get("error_type") == "service_unavailable":
    ...
```

---

### [MEDIUM] R-04 — Naming (satu konsep "nomor telepon" punya 6 nama)
**File:** lintas file
**Lokasi:** `schema.py` L9 `user_id`; `webhook.py` `sender` / `target_number`; `catalog.py` `user_id` / `clean_user_id`; `app.js` `userId` / `phone` / `initialUserId`

**Masalah:**
Kolom `user_id` berisi nomor WhatsApp, bukan ID user. Di modul lain disebut `sender`, `target_number`, `phone`.

**Contoh kode (sebelum):**
```python
user_id = Column(String, index=True)
async def send_whatsapp_reply(target_number: str, text: str):
```

**Alasan kenapa ini readability issue:**
`user_id` menyiratkan ID internal; pembaca perlu membuka validator `WebhookPayload` untuk tahu itu nomor telepon.

**Rekomendasi:**
Tanpa rename kolom: tambahkan comment di model dan seragamkan nama parameter baru ke `phone_number`.

**Contoh kode (sesudah):**
```python
# WhatsApp phone number in international format without "+" (e.g. "6281234567890")
user_id = Column(String, index=True)
```

---

### [MEDIUM] R-05 — Naming (alias global hanya demi kompatibilitas test)
**File:** `app/api/webhook.py`, `tests/test_api.py`
**Lokasi:** `webhook.py` L23-24; `test_api.py` L4, L17

**Masalah:**
`rate_limit_cache` adalah alias dari `sender_rate_limit_cache`. Kode produksi menyimpan nama kedua hanya untuk test lama.

**Contoh kode (sebelum):**
```python
# Keep rate_limit_cache reference for test compatibility
rate_limit_cache = sender_rate_limit_cache
```

**Alasan kenapa ini readability issue:**
Dua nama untuk satu objek; pembaca mengira ada cache ketiga.

**Rekomendasi:**
Hapus alias, ganti import di `test_api.py` ke `sender_rate_limit_cache` (atau pakai fixture reset bersama di `conftest.py`, lihat R-18).

**Contoh kode (sesudah):**
```python
# tests/test_api.py
from app.api.webhook import sender_rate_limit_cache
```

---

### [MEDIUM] R-06 — Naming / Structure (atribut legacy & atribut di luar `__init__`)
**File:** `app/services/ai_extractor.py`
**Lokasi:** baris 28-31, 37, 43, 51 (`AIExtractor`)

**Masalah:**
`self.llm` dan `self.chain` hanya alias (`self.chain = self.primary_chain`) dan tidak dipakai di mana pun. `self.fallback_llm` dibuat di `_init_llms` tanpa dideklarasikan di `__init__`, padahal pasangannya (`self.llm`) dideklarasikan.

**Contoh kode (sebelum):**
```python
self.primary_chain = None
self.fallback_chain = None
self.llm = None
self.chain = None
...
self.fallback_llm = ChatGroq(...)
self.chain = self.primary_chain
```

**Alasan kenapa ini readability issue:**
Pembaca harus mengecek apakah `chain` vs `primary_chain` berbeda; atribut yang tidak terlihat di `__init__` menyulitkan memahami state objek.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
self.primary_llm = None
self.fallback_llm = None
self.primary_chain = None
self.fallback_chain = None
```

---

### [MEDIUM] R-07 — Naming (modul `schema.py` vs `pydantic_schemas.py`)
**File:** `app/models/schema.py`, `app/models/pydantic_schemas.py`
**Lokasi:** nama file; class `CatalogDB`, `CatalogItem`

**Masalah:**
Dua file "schema" berisi hal berbeda (ORM SQLAlchemy vs model Pydantic); `schema.py` tidak punya docstring modul/kelas.

**Contoh kode (sebelum):**
```python
from app.models import schema          # main.py
from app.models.schema import CatalogDB
```

**Alasan kenapa ini readability issue:**
`schema` ambigu; pembaca harus membuka file untuk tahu itu tabel DB.

**Rekomendasi:**
Minimal tambahkan docstring modul. Opsional rename `schema.py` → `orm_models.py` (3 import).

**Contoh kode (sesudah):**
```python
"""SQLAlchemy ORM models (database tables)."""
class CatalogDB(Base):
    """A merchant catalog row in the `catalogs` table."""
```

---

### [MEDIUM] R-08 — Formatting (tidak ada konfigurasi linter/formatter; blank line tidak konsisten)
**File:** root project; `catalog.py`, `config.py`, `logger.py`, `migrations.py`, `pydantic_schemas.py`, `schema.py`, `ai_extractor.py`, `main.py`, `seed.py`, semua `tests/*.py`
**Lokasi:** contoh `catalog.py` L11 & L43; `main.py` L27, 44, 73, 83, 94

**Masalah:**
Tidak ada `.flake8`/`pyproject.toml`/`.editorconfig`. `webhook.py` memakai 2 blank line antar top-level def, file lain 1 blank line (44 lokasi E302/E305).

**Contoh kode (sebelum):**
```python
router = APIRouter()

@router.get("/")
def get_all_catalogs(
...
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}/catalogs")
```

**Alasan kenapa ini readability issue:**
Batas visual antar function berbeda-beda antar file; tanpa tool, inkonsistensi akan terus bertambah.

**Rekomendasi:**
Tambah `pyproject.toml` dengan ruff (lint + format, `line-length = 100`) dan langkah `ruff check` di `.github/workflows/ci.yml`.

**Contoh kode (sesudah):**
```toml
[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "W", "F", "I"]
```

---

### [MEDIUM] R-09 — Formatting (line ending tidak dikunci; risiko CRLF pada shell script)
**File:** `.gitattributes`, `docker-entrypoint.sh`
**Lokasi:** `.gitattributes` L1 (hanya aturan LFS)

**Masalah:**
Index git sudah LF, tetapi dengan `core.autocrlf=true` working copy Windows menjadi campuran CRLF (18 file) dan LF (15 file baru). `docker-entrypoint.sh` di working copy ber-CRLF; build Docker lokal dari Windows akan menyalin `\r` ke image.

**Contoh kode (sebelum):**
```
*.png filter=lfs diff=lfs merge=lfs -text
```

**Alasan kenapa ini readability issue:**
Diff penuh noise "whole file changed" saat editor berbeda menyimpan EOL berbeda; shell script CRLF bisa gagal (`set: Illegal option -`).

**Rekomendasi:**
**Contoh kode (sesudah):**
```
* text=auto eol=lf
*.sh text eol=lf
*.png filter=lfs diff=lfs merge=lfs -text
```

---

### [MEDIUM] R-10 — Comment (comment/dokumentasi basi)
**File:** `app/api/catalog.py`, `README.md`, `app/api/webhook.py`
**Lokasi:** `catalog.py` L52; `README.md` L44; `webhook.py` L23

**Masalah:**
- `catalog.py`: "consumed by the mobile/frontend application" — tidak ada aplikasi mobile.
- `README.md`: "automatic database seeding on container startup" — default sekarang `RUN_SEED_ON_STARTUP=false`.
- `webhook.py`: comment menjustifikasi kode produksi demi test (lihat R-05).

**Contoh kode (sebelum):**
```python
"""
Fetch all catalog items belonging to a specific user with pagination.
This endpoint is consumed by the mobile/frontend application.
"""
```

**Alasan kenapa ini readability issue:**
Comment yang salah lebih menyesatkan daripada tanpa comment.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
"""Return a paginated list of catalogs owned by one WhatsApp number (used by the web UI)."""
```
README L44 → `- optional database seeding on startup (RUN_SEED_ON_STARTUP=true)`.

---

### [MEDIUM] R-11 — Structure (magic number & teks yang menduplikasi konstanta)
**File:** `app/api/webhook.py`, `app/api/catalog.py`, `seed.py`
**Lokasi:** `webhook.py` L104-111, L133, L135, L146-148, L256, L260; `catalog.py` L13-14, L46-47; `seed.py` L13, L31

**Masalah:**
- Pruning cache memakai `5000` dan `1000` tanpa nama.
- Jumlah retry Fonnte ditulis di 3 tempat (`range(1, 3)`, `attempt < 2`, `"after 2 attempts"`), timeout `10.0`, jeda `1.0`.
- Teks "Mohon tunggu 1 menit" dan "Max 3 per minute" menduplikasi `RATE_LIMIT_WINDOW_SECONDS` / `RATE_LIMIT_MAX_REQUESTS`.
- Default pagination `20`/`100` diketik dua kali di `catalog.py`.
- Parsing boolean env `{"1", "true", "yes"}` diulang di `seed.py`.

**Contoh kode (sebelum):**
```python
for attempt in range(1, 3):
    ...
    if attempt < 2:
        await asyncio.sleep(1.0)
logger.error(f"Failed to dispatch WhatsApp reply to {target_number} after 2 attempts")
...
"message": "Rate limit exceeded (Max 3 per minute)."
```

**Alasan kenapa ini readability issue:**
Mengubah satu nilai mengharuskan pencarian manual; pembaca tidak tahu arti 5000/1000.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
FONNTE_MAX_ATTEMPTS = 2
FONNTE_TIMEOUT_SECONDS = 10.0
FONNTE_RETRY_DELAY_SECONDS = 1.0
CACHE_PRUNE_THRESHOLD = 5000
CACHE_PRUNE_BATCH = 1000

for attempt in range(1, FONNTE_MAX_ATTEMPTS + 1):
    ...
"message": f"Rate limit exceeded (max {RATE_LIMIT_MAX_REQUESTS} per minute)."
```

---

### [MEDIUM] R-12 — Structure (duplikasi kode)
**File:** `app/api/catalog.py`, `main.py`, `app/services/ai_extractor.py`, `wa-catalog-frontend/index.html`
**Lokasi:** `catalog.py` L23-38 vs L57-77; `main.py` L47-63, L78 vs L89, L34-41 vs `index.html` L6; `ai_extractor.py` L87-92 vs L121-126

**Masalah:**
- Query + response pagination identik di dua endpoint katalog.
- Dua blok `add_middleware(CORSMiddleware, ...)` hanya beda `allow_origins`/`allow_credentials`.
- Path `index.html` dihitung ulang di dua route.
- String CSP disalin di header Python dan meta HTML (rawan drift).
- Dict error extractor ditulis dua kali.

**Contoh kode (sebelum):**
```python
if not origins or origins == ["*"]:
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, ...)
else:
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, ...)
```

**Alasan kenapa ini readability issue:**
Pembaca harus membandingkan blok baris per baris untuk menemukan perbedaannya.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
allow_all = not origins or origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)
INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")
```
Untuk katalog: helper `_paginate(query, limit, offset) -> dict`. Untuk extractor: helper `_error_result()` (lihat R-03).

---

### [MEDIUM] R-13 — Structure (pengaturan status UI diulang 8 kali)
**File:** `wa-catalog-frontend/app.js`
**Lokasi:** baris 77-78, 92-93, 100-101, 107-108, 114-115, 128-129, 135-136, 145-146

**Masalah:**
Pola `statusMessage.style.color = ...; statusMessage.textContent = ...;` berulang dengan warna hex mentah. Warna error tidak konsisten: `"red"` (L100, L135) vs `"#d9534f"` (L114, L145).

**Contoh kode (sebelum):**
```js
statusMessage.style.color = "#d9534f";
statusMessage.textContent = `Tidak ada katalog untuk nomor ${userId}. ...`;
...
statusMessage.style.color = "red";
statusMessage.textContent = "Gagal terhubung ke server.";
```

**Alasan kenapa ini readability issue:**
Makna warna (info/sukses/error) harus ditebak dari kode hex; dua merah berbeda untuk kondisi yang sama.

**Rekomendasi:**
**Contoh kode (sesudah):**
```js
const STATUS_COLORS = { info: "#0056b3", success: "#28a745", error: "#d9534f" };

function setStatus(text, tone = "info") {
    statusMessage.style.color = STATUS_COLORS[tone];
    statusMessage.textContent = text;
}

setStatus("Gagal terhubung ke server.", "error");
```

---

### [MEDIUM] R-14 — Structure (urutan kode di `app.js` mengandalkan hoisting)
**File:** `wa-catalog-frontend/app.js`
**Lokasi:** baris 43-49 (bootstrap) memanggil `fetchCatalogsByUser` (L105) & `fetchAllCatalogs` (L74)

**Masalah:**
Inisialisasi halaman dijalankan di tengah file, sebelum definisi function yang dipanggilnya dan sebelum event listener dipasang.

**Contoh kode (sebelum):**
```js
const initialUserId = getInitialUserId();
if (initialUserId) {
    phoneInput.value = initialUserId;
    fetchCatalogsByUser(initialUserId);   // didefinisikan 60 baris di bawah
} else {
    fetchAllCatalogs();
}
phoneInput.addEventListener(...)
```

**Alasan kenapa ini readability issue:**
Pembaca harus loncat ke bawah lalu kembali ke atas untuk mengikuti alur startup.

**Rekomendasi:**
Urutkan: konstanta → helper (`escapeHtml`, `maskPhoneNumber`, `setStatus`) → fetch → render → event listener → bootstrap di akhir.

**Contoh kode (sesudah):**
```js
// ... all function definitions above ...

// Bootstrap
const initialUserId = getInitialUserId();
initialUserId ? loadUserCatalogs(initialUserId) : fetchAllCatalogs();
```

---

### [MEDIUM] R-15 — Structure (side effect saat import & fallback route tidak konsisten)
**File:** `main.py`
**Lokasi:** baris 17-18; baris 73-81 vs 83-92

**Masalah:**
`create_all` + `run_migrations` dijalankan saat modul di-import (termasuk saat test meng-import `main`). Route `/` mengembalikan 200 + dict bila frontend tidak ada, sedangkan `/users/{id}/catalogs` mengembalikan 404 untuk kondisi yang sama.

**Contoh kode (sebelum):**
```python
schema.Base.metadata.create_all(bind=engine)
run_migrations(engine)

app = FastAPI(...)
```

**Alasan kenapa ini readability issue:**
Efek samping tersembunyi di level modul sulit ditemukan; dua perilaku berbeda untuk "frontend hilang" membingungkan.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    schema.Base.metadata.create_all(bind=engine)
    run_migrations(engine)
    yield

app = FastAPI(..., lifespan=lifespan)
```
Samakan fallback kedua route (keduanya 404 JSON atau keduanya pesan API).

---

### [MEDIUM] R-16 — Type (type hint tidak konsisten & sering absen)
**File:** `app/api/webhook.py`, `app/api/catalog.py`, `app/models/pydantic_schemas.py`, `app/core/migrations.py`, `app/core/logger.py`, `app/core/database.py`, `app/services/ai_extractor.py`, `seed.py`
**Lokasi:** contoh `webhook.py` L116, L151; `migrations.py` L4; `ai_extractor.py` L55; `pydantic_schemas.py` L3, L11; `catalog.py` L12, L44

**Masalah:**
- Dua gaya: `str | None` (webhook) vs `typing.List`/`Optional` (pydantic_schemas).
- Banyak function tanpa return type (`send_whatsapp_reply`, `background_process_wa_message`, `get_db`, `setup_logger`, `run_migrations`, endpoint katalog); parameter `engine` dan `chain` tanpa tipe.
- Endpoint mengembalikan dict tanpa `response_model`, sehingga bentuk response hanya bisa diketahui dengan membaca body.

**Contoh kode (sebelum):**
```python
from typing import List, Optional
menus: List[str] = Field(...)
def run_migrations(engine):
async def _invoke_with_retry(self, chain, user_message: str, max_attempts: int = 2, retry_delay: float = 1.0):
```

**Alasan kenapa ini readability issue:**
Pembaca tidak tahu tipe `engine`/`chain`/hasil fungsi tanpa menelusuri pemanggil.

**Rekomendasi:**
Seragamkan ke gaya built-in Python 3.10 dan lengkapi signature publik.

**Contoh kode (sesudah):**
```python
menus: list[str] = Field(...)
def run_migrations(engine: Engine) -> None:
async def send_whatsapp_reply(target_number: str, text: str) -> None:
async def _invoke_with_retry(self, chain: Runnable, user_message: str, ...) -> CatalogItem:
```

---

### [MEDIUM] R-17 — Comment (helper privat & beberapa kelas tanpa docstring)
**File:** `app/services/ai_extractor.py`, `main.py`, `app/core/config.py`, `app/models/schema.py`, `seed.py`, `wa-catalog-frontend/app.js`
**Lokasi:** `_init_llms` L34, `_invoke_with_retry` L55, `_to_dict` L82; `SecurityHeadersMiddleware` L27; `Settings` L3; `CatalogDB` L4; `seed_food_beverage_catalogs` L11; JS `fetchAllCatalogs`, `fetchCatalogsByUser`, `renderCatalogs`

**Masalah:**
Function publik di webhook/catalog punya docstring, tetapi helper yang logikanya paling tidak jelas (retry backoff hanya untuk rate limit; fallback init dengan `"dummy_key"`) tidak punya. Di JS, 3 dari 7 function punya comment.

**Contoh kode (sebelum):**
```python
async def _invoke_with_retry(self, chain, user_message: str, max_attempts: int = 2, retry_delay: float = 1.0):
    last_error = None
```

**Alasan kenapa ini readability issue:**
Aturan penting ("hanya error rate-limit yang di-retry dengan exponential backoff") tidak terlihat tanpa membaca isi loop.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
async def _invoke_with_retry(...):
    """Invoke `chain`, retrying only on rate-limit errors with exponential backoff.

    Non rate-limit errors are raised immediately after the first failure.
    """
```

---

### [MEDIUM] R-18 — Structure (duplikasi di test suite)
**File:** `tests/test_api.py`, `tests/test_webhook.py`, `tests/test_catalog.py`, `tests/test_health.py`
**Lokasi:** `MOCK_EXTRACTED_DATA` (test_api L7-12, test_webhook L7-12); fixture reset cache (test_api L14-18, test_webhook L14-18); `AsyncClient(transport=ASGITransport(app=app), base_url="http://test")` diulang 14 kali

**Masalah:**
Data mock dan fixture identik disalin antar file; boilerplate client diulang di setiap test.

**Contoh kode (sebelum):**
```python
async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
```

**Alasan kenapa ini readability issue:**
Inti test (request + assertion) tertutup boilerplate; dua salinan data mock bisa berbeda tanpa disadari.

**Rekomendasi:**
Pindahkan ke `tests/conftest.py`.

**Contoh kode (sesudah):**
```python
@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

async def test_webhook_success(client, mock_extractor):
    response = await client.post("/api/v1/whatsapp-catalog", json=payload)
```

---

### [LOW] R-19 — Naming (singkatan & penamaan variabel kecil tidak seragam)
**File:** `app/core/logger.py`, `app/api/webhook.py`, `seed.py`, `app/models/pydantic_schemas.py`
**Lokasi:** `logger.py` L21 `ch`; `webhook.py` L105, L109 `k, v`; `seed.py` L130 `data`; `pydantic_schemas.py` L24 `clean` vs L32 `cleaned`

**Masalah:**
`ch` (console handler), `k, v` di comprehension cache, `data` untuk satu baris dummy. Variabel hasil pembersihan dinamai `clean`, `cleaned`, `clean_name`, `clean_user_id`.

**Contoh kode (sebelum):**
```python
ch = logging.StreamHandler(sys.stdout)
empty_senders = [k for k, v in sender_rate_limit_cache.items() if not v]
for data in dummies:
```

**Alasan kenapa ini readability issue:**
Ringan, tetapi menambah beban tebak-menebak.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
console_handler = logging.StreamHandler(sys.stdout)
empty_senders = [sender for sender, timestamps in sender_rate_limit_cache.items() if not timestamps]
for dummy_catalog in dummy_catalogs:
```

---

### [LOW] R-20 — Naming (fixture berformat PascalCase)
**File:** `tests/conftest.py`
**Lokasi:** baris 26, fixture `TestSessionLocal`

**Masalah:**
Fixture (function) dinamai seperti kelas.

**Contoh kode (sebelum):**
```python
@pytest.fixture(scope="session")
def TestSessionLocal(test_engine):
```

**Alasan kenapa ini readability issue:**
Melanggar konvensi `snake_case` function yang dipakai di seluruh project.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
@pytest.fixture(scope="session")
def test_session_factory(test_engine):
```

---

### [LOW] R-21 — Naming (nama test berisi ID tiket)
**File:** `tests/test_webhook.py`
**Lokasi:** baris 170, `test_multiple_catalogs_per_user_biz_01`

**Masalah:**
Sufiks `_biz_01` merujuk ID temuan audit, bukan perilaku.

**Contoh kode (sebelum):**
```python
async def test_multiple_catalogs_per_user_biz_01(mocker):
```

**Alasan kenapa ini readability issue:**
ID tiket tidak bermakna bagi pembaca di masa depan.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
async def test_same_sender_can_own_multiple_catalogs(mocker):
```

---

### [LOW] R-22 — Formatting (trailing whitespace & blank line berisi spasi)
**File:** `catalog.py` L31, 69, 78; `config.py` L8, 13, 19; `logger.py` L10, 14, 19, 24, 26; `migrations.py` L15, 23, 31; `schema.py` L12, 14, 15; `ai_extractor.py` L12, 27; `webhook.py` L153; `database.py` L7; `tests/test_api.py` L23, 35, 38, 48, 55, 68; `tests/test_seed.py` L10, 25
**Lokasi:** lihat daftar

**Masalah:**
Spasi tak terlihat di akhir baris / pada baris kosong.

**Contoh kode (sebelum):**
```python
        )
········
        return {
```

**Alasan kenapa ini readability issue:**
Menimbulkan noise di diff dan review.

**Rekomendasi:**
Jalankan `ruff format` (R-08) atau aktifkan "trim trailing whitespace" di editor.

**Contoh kode (sesudah):**
```python
        )

        return {
```

---

### [LOW] R-23 — Formatting (file tanpa newline di akhir)
**File:** `app/api/catalog.py`, `app/api/webhook.py`, `app/core/config.py`, `app/core/database.py`, `app/models/schema.py`, `main.py`, `tests/test_webhook.py`
**Lokasi:** baris terakhir masing-masing file

**Masalah:**
7 file tidak diakhiri newline, file lain diakhiri newline.

**Contoh kode (sebelum):**
```
settings = Settings()⏎(tidak ada)
```

**Alasan kenapa ini readability issue:**
Diff menampilkan "\ No newline at end of file" dan mengubah baris terakhir saat ada penambahan.

**Rekomendasi:**
Tambahkan newline akhir (otomatis via formatter).

**Contoh kode (sesudah):**
```
settings = Settings()
⏎
```

---

### [LOW] R-24 — Formatting (blank line ganda di dalam function)
**File:** `app/core/logger.py`
**Lokasi:** baris 10-21, `setup_logger`

**Masalah:**
Setiap langkah dipisahkan dua baris kosong (salah satunya berisi spasi).

**Contoh kode (sebelum):**
```python
    logger = logging.getLogger("wa_catalog_bot")
    

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        

        formatter = logging.Formatter(
```

**Alasan kenapa ini readability issue:**
Function 15 baris terlihat terpecah-pecah seperti beberapa blok tak berhubungan.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
    logger = logging.getLogger("wa_catalog_bot")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger
```

---

### [LOW] R-25 — Formatting (baris > 120 karakter)
**File:** `webhook.py` L164, 166; `migrations.py` L20, 22, 28, 30; `schema.py` L18; `seed.py` L34, 122; `scripts/manual_test_webhook.py` L13; `tests/test_migrations.py` L46; `tests/test_webhook.py` L161
**Lokasi:** lihat daftar (12 baris; terpanjang 255 karakter)

**Masalah:**
Pesan WhatsApp panjang, string SQL, dan definisi kolom dalam satu baris.

**Contoh kode (sebelum):**
```python
updated_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now(), nullable=True)
```

**Alasan kenapa ini readability issue:**
Perlu scroll horizontal; argumen terakhir mudah terlewat.

**Rekomendasi:**
**Contoh kode (sesudah):**
```python
updated_at = Column(
    DateTime(timezone=True),
    default=func.now(),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=True,
)
```

---

### [LOW] R-26 — Import (unused import)
**File:** `app/api/catalog.py` L3; `app/api/webhook.py` L6; `app/models/pydantic_schemas.py` L3; `scripts/manual_test_webhook.py` L5
**Lokasi:** lihat daftar

**Masalah:**
`List`, `Optional` (catalog), `Session` (webhook), `Optional` (pydantic_schemas), `sys` (script) di-import tapi tidak dipakai.

**Contoh kode (sebelum):**
```python
from typing import List, Optional   # catalog.py — keduanya tidak dipakai
from sqlalchemy.orm import Session  # webhook.py — tidak dipakai
```

**Alasan kenapa ini readability issue:**
Pembaca mengira modul memakai tipe/objek tersebut.

**Rekomendasi:**
Hapus 4 baris/bagian import tersebut.

**Contoh kode (sesudah):**
```python
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
```

---

### [LOW] R-27 — Import (urutan/grouping import tidak konsisten)
**File:** `app/services/ai_extractor.py` L1-7; `main.py` L1-8; `app/api/webhook.py` L1-8; `tests/test_webhook.py` L144, 158, 171-173
**Lokasi:** lihat daftar

**Masalah:**
Import lokal dan third-party bercampur (`app.core.config` diapit `asyncio` dan `langchain_groq`); `import os` (stdlib) diletakkan setelah third-party di `main.py`; beberapa test mengimpor di dalam function. Tidak ditemukan circular import (`database → config`, `schema → database`, `webhook → services → models`).

**Contoh kode (sebelum):**
```python
import asyncio
from app.core.config import settings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.models.pydantic_schemas import CatalogItem
```

**Alasan kenapa ini readability issue:**
Sulit melihat sekilas dependensi eksternal vs internal.

**Rekomendasi:**
Grouping stdlib → third-party → local (otomatis dengan ruff rule `I`).

**Contoh kode (sesudah):**
```python
import asyncio

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logger import logger
from app.models.pydantic_schemas import CatalogItem
```

---

### [LOW] R-28 — Comment / Consistency (gaya log & pesan error tidak seragam; `print` vs logger)
**File:** `app/api/webhook.py`, `app/api/catalog.py`, `main.py`, `seed.py`
**Lokasi:** `webhook.py` L52, 123, 157, 247; `catalog.py` L41, 83; `main.py` L107; `seed.py` L146

**Masalah:**
Prefix log berganti gaya: `"CRITICAL: ..."`, `"[Simulated Fonnte API] ..."`, `"Background Task: ..."`, `"SPAM BLOCKED: ..."`, `"Healthcheck DB failure"`, `"Database Fetch Error"`. Detail HTTP 500 berbeda antar endpoint (`"Internal server error"` vs `"Internal server error while fetching catalogs"`). `seed.py` memakai `print` padahal ada `logger`. Semua log memakai f-string, bukan lazy `%s`.

**Contoh kode (sebelum):**
```python
logger.warning(f"SPAM BLOCKED: Rate limit exceeded for {payload.sender} from IP {client_ip}")
logger.error(f"Healthcheck DB failure: {e}", exc_info=True)
print(f"Seed completed for database {database_url}. ...")
```

**Alasan kenapa ini readability issue:**
Sulit mencari/filter log; level sudah ada di formatter sehingga prefix "CRITICAL:" redundan.

**Rekomendasi:**
Satu gaya kalimat biasa tanpa prefix kapital; level ditentukan method logger.

**Contoh kode (sesudah):**
```python
logger.warning("Rate limit exceeded for sender=%s ip=%s", payload.sender, client_ip)
logger.error("Health check database failure: %s", exc, exc_info=True)
logger.info("Seed completed: created=%d updated=%d", created_count, updated_count)
```

---

### [LOW] R-29 — Formatting (atribut tombol HTML tidak seragam)
**File:** `wa-catalog-frontend/index.html`
**Lokasi:** baris 27-28

**Masalah:**
`showAllBtn` punya `type="button"`, `searchBtn` tidak.

**Contoh kode (sebelum):**
```html
<button id="searchBtn" class="primary-btn">Cari Katalog</button>
<button id="showAllBtn" class="primary-btn" type="button">Tampilkan Semua</button>
```

**Alasan kenapa ini readability issue:**
Pembaca bertanya apakah perbedaan itu disengaja (mis. submit form).

**Rekomendasi:**
**Contoh kode (sesudah):**
```html
<button id="searchBtn" class="primary-btn" type="button">Cari Katalog</button>
<button id="showAllBtn" class="primary-btn" type="button">Tampilkan Semua</button>
```
