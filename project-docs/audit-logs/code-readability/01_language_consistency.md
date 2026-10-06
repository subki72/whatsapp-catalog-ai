# Language Consistency Audit

Bahasa baku project: **dual-language berdasarkan audiens** — end-user (UI web + balasan WhatsApp) = **ID**; developer/operator (identifier, comment, docstring, log, API JSON, error CLI, README) = **EN**. Tidak ada i18n.
Istilah exception (boleh tetap asli): `WhatsApp`, `WA`, `API`, `webhook`, `link`, `server`, `AI`, `katalog`, `menu`, `etalase`. `database`/`backend`/`Docker` hanya boleh di teks developer.

## Ringkasan
Total temuan: **8** (Critical: 1, High: 2, Medium: 3, Low: 2)

Identifier (variable/function/class) **100% EN dan konsisten** — tidak ada temuan naming dari aspek bahasa (aspek kejelasan naming dibahas di `02_readability.md`).

## Temuan

### [CRITICAL] L-01 — UI String (nilai sentinel LLM berbahasa EN tampil di UI ID)
**File:** `app/services/ai_extractor.py`, `app/models/pydantic_schemas.py`, `app/api/webhook.py`, `wa-catalog-frontend/app.js`
**Lokasi:** `ai_extractor.py` baris 15-21 (`AIExtractor.__init__`, prompt); `pydantic_schemas.py` baris 10 (`CatalogItem.location`); `webhook.py` baris 180 & 213-219 (`background_process_wa_message`); `app.js` baris 171 (`renderCatalogs`)

**Masalah:**
Prompt LLM menginstruksikan nilai default **`'Not provided'`** (EN). Nilai ini disimpan ke DB lalu ditampilkan apa adanya di kartu UI ("Lokasi: Not provided") dan di balasan WhatsApp ("📍 Lokasi: Not provided"). Prompt juga tidak menginstruksikan bahasa output, sehingga `unique_selling_point` bisa dihasilkan dalam EN padahal label sekitarnya ID ("Keunggulan:").

**Contoh kode:**
```python
# ai_extractor.py L20-21
"Extract the product name, location, menu list, and unique selling points.\n"
"If any information is missing, use 'Not provided' for strings and an empty array [] for lists.\n\n"

# webhook.py L216
f"📍 Lokasi: {catalog.location}\n"
```
```js
// app.js L171
<p class="card-location">Lokasi: ${safeLocation}</p>
```

**Konteks:**
Seluruh layar dan pesan WhatsApp berbahasa ID, tetapi data yang mengisi label berasal dari prompt EN → user melihat "Lokasi: Not provided" di satu kalimat.

**Rekomendasi:**
- Ubah instruksi prompt (L20-21) agar: (a) nilai kosong memakai `'Tidak disebutkan'`, dan (b) "Jawab dalam bahasa yang sama dengan pesan user (umumnya Bahasa Indonesia)".
- Samakan daftar sentinel di `webhook.py` L180 (`{"not provided", "none", ""}`) → tambahkan `"tidak disebutkan"` dan jadikan satu konstanta bersama (lihat R-17 di `02_readability.md`).
- Perbarui `Field(description=...)` di `pydantic_schemas.py` L10 sesuai sentinel baru.
- Total ±4 baris.

---

### [HIGH] L-02 — UI String (judul tab EN di halaman ID)
**File:** `wa-catalog-frontend/index.html`
**Lokasi:** baris 7, `<title>`

**Masalah:**
Judul tab browser "My Cloud Catalog" berbahasa EN dan berbeda nama brand dengan header halaman "KatalogKu".

**Contoh kode:**
```html
<html lang="id">
...
<title>My Cloud Catalog</title>
...
<h1 class="logo-title"><span class="logo-icon"></span> KatalogKu</h1>
<p class="subtitle">Etalase Digital Otomatis Anda</p>
```

**Konteks:**
Atribut `lang="id"` dan seluruh teks halaman ID; hanya `<title>` EN dengan brand berbeda — user melihat dua nama produk di satu layar.

**Rekomendasi:**
Ganti baris 7 menjadi `<title>KatalogKu — Etalase Digital Otomatis</title>`. 1 baris.

---

### [HIGH] L-03 — UI String / Comment (pesan error operator campur ID & EN dalam satu file)
**File:** `seed.py`
**Lokasi:** baris 16-20, 33-35, 146-149, 152-155, `seed_food_beverage_catalogs`

**Masalah:**
Dalam satu function, dua `RuntimeError` berbahasa ID, satu `RuntimeError` + `print` berbahasa EN, dan comment EN.

**Contoh kode:**
```python
raise RuntimeError(
    "DATABASE_URL masih mengarah ke path Docker. "
    "Untuk menjalankan seed secara lokal di Windows, gunakan "
    ...
)
# Ensure tables and missing columns exist
...
raise RuntimeError(
    "DANGER: FORCE_RESEED is blocked in production or non-SQLite environment unless ..."
)
...
print(f"Seed completed for database {database_url}. ...")
...
raise RuntimeError(
    f"Gagal membuka database di '{database_url}'. "
    "Cek apakah path SQLite valid untuk environment yang sedang dipakai."
)
```

**Konteks:**
Mayoritas file (comment, print, 1 dari 3 error) EN — sesuai baku developer-facing. Dua pesan error ID menyimpang.

**Rekomendasi:**
Terjemahkan baris 17-19 dan 153-154 ke EN, mis.:
`"DATABASE_URL still points to the Docker path. To run the seed locally on Windows, set 'sqlite:///./catalog_db.sqlite' in .env."` dan
`f"Failed to open database at '{database_url}'. Check that the SQLite path is valid for the current environment."`. 5 baris.

---

### [MEDIUM] L-04 — UI String (istilah "Nomor WA" vs "nomor WhatsApp" tidak seragam)
**File:** `wa-catalog-frontend/index.html`, `wa-catalog-frontend/app.js`
**Lokasi:** `index.html` baris 26, 30; `app.js` baris 93, 108, 115, 129, 172

**Masalah:**
Konsep yang sama ditulis tiga cara: "Nomor WA", "nomor WhatsApp", dan "nomor" saja.

**Contoh kode:**
```html
<input ... placeholder="Masukkan Nomor WA (Misal: 62812...)">
<p id="statusMessage" ...>... Masukkan nomor WhatsApp hanya jika ingin memfilter ...</p>
```
```js
`Menampilkan ${catalogs.length} katalog dari database. Masukkan nomor WhatsApp untuk memfilter ...`
`Mencari katalog untuk nomor ${userId}...`
<p class="card-location">Nomor WA: ${safeUserId}</p>
```

**Konteks:**
Semua ID, namun istilah dan kapitalisasi ("Nomor WA" vs "nomor WhatsApp") berganti-ganti di layar yang sama.

**Rekomendasi:**
Pilih satu istilah, mis. **"nomor WhatsApp"** di kalimat dan **"Nomor WhatsApp"** di label. Ubah placeholder (index.html L26) dan label kartu (app.js L172). 2 baris.

---

### [MEDIUM] L-05 — UI String (jargon teknis di pesan end-user & pesan gagal tidak seragam)
**File:** `wa-catalog-frontend/app.js`
**Lokasi:** baris 78, 93, 101, 136, 146 (`fetchAllCatalogs`, `fetchCatalogsByUser`, `renderCatalogs`)

**Masalah:**
Pesan untuk pengunjung umum memakai istilah developer ("dari database", "backend Docker"). Kegagalan koneksi yang sama punya dua teks berbeda.

**Contoh kode:**
```js
statusMessage.textContent = "Memuat semua katalog dari database...";                       // L78
statusMessage.textContent = "Gagal terhubung ke server. Pastikan backend Docker sedang berjalan."; // L101
statusMessage.textContent = "Gagal terhubung ke server.";                                   // L136
statusMessage.textContent = "Belum ada katalog di database.";                               // L146
```

**Konteks:**
UI ditujukan ke pembeli/penjual awam; instruksi "Pastikan backend Docker sedang berjalan" hanya bermakna bagi developer lokal.

**Rekomendasi:**
- L101 & L136 → satu teks: `"Gagal terhubung ke server. Silakan coba beberapa saat lagi."`
- L78 → `"Memuat semua katalog..."`; L93 → `"Menampilkan ${n} katalog."`; L146 → `"Belum ada katalog yang tersedia."`
- 5 baris.

---

### [MEDIUM] L-06 — Comment (comment CSS campur EN/ID dalam satu file)
**File:** `wa-catalog-frontend/styles.css`
**Lokasi:** baris 296, 349 (blok media query)

**Masalah:**
9 dari 11 comment section berbahasa EN; dua comment berbahasa ID.

**Contoh kode:**
```css
/* Responsive Catalog Grid */
...
/* Desktop kecil / tablet landscape */
@media screen and (max-width: 1180px) {
/* Tablet */
/* Mobile */
/* HP kecil */
@media screen and (max-width: 420px) {
```

**Konteks:**
Comment developer-facing → baku EN.

**Rekomendasi:**
L296 → `/* Small desktop / landscape tablet */`; L349 → `/* Small phones */`. 2 baris.

---

### [LOW] L-07 — UI String (format balasan WhatsApp tidak seragam)
**File:** `app/api/webhook.py`
**Lokasi:** baris 164, 166, 214, 230, 256 (`background_process_wa_message`, `process_whatsapp_message`)

**Masalah:**
Balasan sukses memakai emoji + judul tebal WhatsApp (`✅ *...*`), peringatan rate limit memakai `⚠️`, sedangkan tiga pesan error polos tanpa emoji/judul. Sapaan juga berganti ("Maaf, ..." vs "Terjadi kesalahan internal pada sistem saat memproses katalog AI Anda." — frasa "katalog AI Anda" janggal karena katalognya milik user, bukan milik AI).

**Contoh kode:**
```python
user_msg = "Maaf, sistem AI kami sedang sibuk ..."
f"✅ *Katalog Berhasil Disimpan!*\n\n"
await send_whatsapp_reply(sender, "Terjadi kesalahan internal pada sistem saat memproses katalog AI Anda.")
"⚠️ Anda mengirim permintaan terlalu cepat. Mohon tunggu 1 menit sebelum mencoba lagi."
```

**Konteks:**
Semua ID (benar), tetapi gaya/format tidak seragam antar pesan dari bot yang sama.

**Rekomendasi:**
Pakai pola tetap: `<emoji> *Judul*` + kalimat diawali "Maaf, ..." untuk semua error, mis. `"❌ *Gagal Memproses Katalog*\nMaaf, terjadi kendala pada sistem saat memproses katalog Anda. Silakan coba lagi."`. 4 baris.

---

### [LOW] L-08 — UI String (pesan API EN yang ambigu)
**File:** `app/api/webhook.py`
**Lokasi:** baris 267, `process_whatsapp_message`

**Masalah:**
Pesan response `"Webhook received, data processing heavily in background."` — kata "heavily" tidak bermakna dan menyesatkan.

**Contoh kode:**
```python
return {
    "status": "success",
    "message": "Webhook received, data processing heavily in background."
}
```

**Konteks:**
Developer-facing, EN sudah benar; masalahnya pilihan kata.

**Rekomendasi:**
Ganti ke `"Webhook received; processing in background."` dan sesuaikan assertion di `tests/test_api.py` L42. 2 baris.

---

## Dikecualikan dari temuan (disengaja)
- Data dummy di `seed.py` dan data uji di `tests/`/`scripts/` memakai bahasa gaul ID ("gue", "nampol", "*custom*") — ini data realistis, bukan teks antarmuka.
- Log dan `HTTPException.detail` berbahasa EN — sesuai baku developer-facing.
