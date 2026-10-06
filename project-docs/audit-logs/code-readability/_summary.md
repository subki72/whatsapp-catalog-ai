# Code Readability & Language Consistency — Summary 2026-10-06

Stack: Python 3.10 (FastAPI, SQLAlchemy, LangChain-Groq, Pydantic v2) + Vanilla JS/HTML/CSS  
Total findings: **37** (Language Consistency: 8, Readability: 29)

| Kategori | Critical | High | Medium | Low | Total |
|---|:---:|:---:|:---:|:---:|:---:|
| **Language Consistency** | 1 | 2 | 3 | 2 | **8** |
| **Readability** | 0 | 3 | 15 | 11 | **29** |
| **Total** | **1** | **5** | **18** | **13** | **37** |

---

## Top Issues (Urut Severity)

1. **[Critical] [Language] `app/services/ai_extractor.py`, `app/models/pydantic_schemas.py`, `app/api/webhook.py`, `wa-catalog-frontend/app.js`** — Sentinel LLM `'Not provided'` (EN) muncul di antarmuka & balasan WhatsApp bahasa Indonesia (L-01).
2. **[High] [Language] `wa-catalog-frontend/index.html`** — Judul tab browser "My Cloud Catalog" (EN) bertentangan dengan nama brand & bahasa header "KatalogKu" (ID) (L-02).
3. **[High] [Language] `seed.py`** — Pesan error operator bercampur antara bahasa Indonesia dan English dalam satu fungsi yang sama (L-03).
4. **[High] [Readability] `app/models/schema.py`, `pydantic_schemas.py`, `webhook.py`** — Kolom/properti `product_name` sebenarnya menyimpan nama usaha/bisnis, bukan nama produk tunggal (R-01).
5. **[High] [Readability] `app/api/webhook.py`** — Fungsi `background_process_wa_message` memuat terlalu banyak tanggung jawab (80 baris, 4 level nesting) tanpa sub-fungsi (R-02).
6. **[High] [Readability] `app/services/ai_extractor.py`, `app/api/webhook.py`** — Kontrak deteksi kegagalan ekstraksi mengandalkan string sentinel bebas `"Error"` dan substring matching rapuh (R-03).
7. **[Medium] [Language] `wa-catalog-frontend/index.html`, `app.js`** — Penulisan konsep nomor WhatsApp tidak seragam ("Nomor WA", "nomor WhatsApp", "nomor") (L-04).
8. **[Medium] [Language] `wa-catalog-frontend/app.js`** — Jargon teknis developer ("dari database", "backend Docker") terpapar pada pesan status end-user (L-05).
9. **[Medium] [Language] `wa-catalog-frontend/styles.css`** — Dua komentar media query berbahasa Indonesia di dalam file stylesheet yang 90% berbahasa Inggris (L-06).
10. **[Medium] [Readability] Lintas File** — Satu konsep nomor WhatsApp memiliki 6 variasi nama identifier (`user_id`, `sender`, `target_number`, `phone`, `userId`, `initialUserId`) (R-04).
11. **[Medium] [Readability] `app/api/webhook.py`, `tests/test_api.py`** — Variabel global alias `rate_limit_cache` dipertahankan di kode produksi hanya demi kompatibilitas pengujian lama (R-05).
12. **[Medium] [Readability] `app/services/ai_extractor.py`** — Atribut legacy tak terpakai (`self.llm`, `self.chain`) dan deklarasi atribut di luar method `__init__` (R-06).
13. **[Medium] [Readability] `app/models/schema.py`, `pydantic_schemas.py`** — Ambiguitas pemisahan nama modul `schema.py` (SQLAlchemy ORM) vs `pydantic_schemas.py` tanpa docstring penjelas (R-07).
14. **[Medium] [Readability] Seluruh File Python** — Tidak ada konfigurasi tool linter/formatter (`pyproject.toml`/`.flake8`), 44 titik pelanggaran spasi kosong antar definisi (R-08).
15. **[Medium] [Readability] `.gitattributes`, `docker-entrypoint.sh`** — Konfigurasi EOL git tidak terkunci sehingga working copy Windows menghasilkan campuran CRLF dan LF (R-09).
16. **[Medium] [Readability] `app/api/catalog.py`, `README.md`** — Komentar basi ("consumed by mobile application", "automatic seed on container startup") yang tidak lagi sesuai implementasi aktual (R-10).
17. **[Medium] [Readability] `app/api/webhook.py`, `catalog.py`, `seed.py`** — Magic numbers (5000, 1000, timeout, retry delay) dan teks duplikasi konstanta rate limit (R-11).
18. **[Medium] [Readability] `app/api/catalog.py`, `main.py`, `ai_extractor.py`** — Duplikasi logika paginasi, middleware CORS, path static, dan konstruksi dict error (R-12).
19. **[Medium] [Readability] `wa-catalog-frontend/app.js`** — Pengaturan status dan warna hex berulang 8 kali tanpa fungsi helper terpadu (R-13).
20. **[Medium] [Readability] `wa-catalog-frontend/app.js`** — Inisialisasi awal halaman diletakkan di tengah script dan bergantung pada function hoisting (R-14).
21. **[Medium] [Readability] `main.py`** — Side effect eksekusi database `create_all` & migrasi saat import modul dan ketidakkonsistenan fallback 404 (R-15).
22. **[Medium] [Readability] Lintas File** — Gaya type annotation bercampur (`str | None` vs `typing.List`/`Optional`) dan hilangnya type hint pada fungsi publik (R-16).
23. **[Medium] [Readability] `app/services/ai_extractor.py`, `main.py`, `app.js`** — Helper privat berlogika penting tidak dilengkapi docstring penjelasan (R-17).
24. **[Medium] [Readability] `tests/`** — Duplikasi data mock, fixture reset cache, dan boilerplate inisialisasi `AsyncClient` diulang 15 kali (R-18).

---

## File Laporan Lengkap
- Referensi Style Terdeteksi: [`00_style_detected.md`](./00_style_detected.md)
- Detail Inkonsistensi Bahasa: [`01_language_consistency.md`](./01_language_consistency.md)
- Detail Kerapihan Penulisan Kode: [`02_readability.md`](./02_readability.md)
- Log Progres Audit: [`_progress.md`](./_progress.md)
