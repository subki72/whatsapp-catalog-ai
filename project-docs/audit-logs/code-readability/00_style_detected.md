# Style Convention & Bahasa Baku — Hasil Deteksi

## 1. Bahasa Baku Project: **dual-language (berdasarkan audiens)**

| Lapisan | Bahasa dominan | Bukti |
|---|---|---|
| Identifier (variable/function/class) | **EN** (100%) | `extract_catalog_data`, `fetchCatalogsByUser`, `CatalogDB`, `is_rate_limited` — tidak ada identifier berbahasa ID |
| Comment & docstring | **EN** (~95%) | Semua docstring Python EN; pengecualian: `styles.css` L296, L349 |
| Log & API response (developer-facing) | **EN** | `logger.*`, `HTTPException(detail=...)`, response JSON webhook |
| String UI frontend (end-user) | **ID** | `index.html` `lang="id"`, tombol "Cari Katalog", "Tampilkan Semua" |
| Balasan WhatsApp (end-user) | **ID** | "Katalog Berhasil Disimpan!", "Maaf, sistem AI kami..." |
| Pesan error CLI operator (`seed.py`) | **Campur** | ID di L17-19 & L153-154, EN di L34 & L146-148 |
| README | **EN** | Seluruh heading & isi |

**Aturan baku yang dipakai untuk audit:**
- Semua teks yang dilihat **end-user** (UI web + balasan WhatsApp) → **Bahasa Indonesia**.
- Semua yang dilihat **developer/operator** (identifier, comment, docstring, log, API JSON, error CLI, README) → **English**.

## 2. Style Convention

### Python (backend, tests, scripts)
| Aspek | Konvensi terdeteksi |
|---|---|
| Naming | `snake_case` (variable/function/module), `PascalCase` (class), `UPPER_SNAKE_CASE` (konstanta modul & field `Settings`) |
| Indentation | 4 spasi, tanpa tab |
| Line length | Tidak dikonfigurasi. Mayoritas baris ≤ 100 karakter; 12 baris > 120 |
| Quotes | Double quote dominan; single quote dipakai di target `mocker.patch('...')` di tests |
| Docstring | Triple double-quote, satu paragraf deskriptif, tanpa section Args/Returns |
| Type hints | Parsial; dua gaya bercampur (`str \| None` vs `typing.Optional/List`) |
| Import order | Tidak konsisten; tidak ada isort/ruff config |
| Blank line antar top-level def | Campur 1 dan 2 baris (PEP 8 = 2) |
| Linter/formatter config | **Tidak ada** (`.flake8`, `pyproject.toml`, `.editorconfig` absen) |

### JavaScript (frontend)
| Aspek | Konvensi terdeteksi |
|---|---|
| Naming | `camelCase` (variable/function), `UPPER_SNAKE_CASE` (`API_BASE_URL`) |
| Indentation | 4 spasi |
| Quotes | Double quote; template literal untuk interpolasi; single quote hanya saat string berisi `"` |
| Semicolon | Selalu dipakai |
| Comment | `//` satu baris di atas function; tanpa JSDoc |
| Struktur | Semua kode di dalam satu callback `DOMContentLoaded` |

### HTML/CSS
- 4 spasi, class `kebab-case`, id `camelCase` (`phoneInput`, `catalogGrid`).
- Comment CSS `/* Section */` sebagai pemisah section.

### Line ending
- Index git: **LF** semua. Working copy Windows: campuran CRLF/LF (efek `core.autocrlf=true`, file baru ditulis LF). Tidak ada `.gitattributes` aturan `eol`.

## 3. Istilah Teknis yang Boleh Tetap Bahasa Asli (di teks ID)
`WhatsApp`, `WA`, `API`, `webhook`, `link`, `server`, `database`*, `backend`*, `AI`, `katalog`, `menu`, `etalase`.

\* Boleh di teks developer; **dihindari** di teks end-user awam (lihat temuan L-05).
