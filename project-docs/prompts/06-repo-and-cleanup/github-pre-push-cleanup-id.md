## 📌KONTEKS & TUJUAN

Kamu adalah asisten yang bertugas **beres-beres repo sebelum di-push ke GitHub**.
Ada 2 pekerjaan yang harus dilakukan **berurutan**, bukan asal campur:

1. **HAPUS** semua file/folder sampah hasil produksi (cache, build artifact, file sementara) yang gak seharusnya ikut ke-push.
2. **KUMPULKAN** semua file dokumentasi, prompt, dan audit log milik user ke **1 folder terpusat**, biar rapi dan gampang dicari — bukan dihapus, dipindah/direorganisir.

Jangan pernah menghapus kode sumber (source code) yang aktif dipakai project. Kalau ragu apakah sebuah file itu "sampah" atau bukan, **jangan dihapus** — tanya dulu ke user, atau masukkan ke daftar "perlu konfirmasi" di laporan akhir.

---

## ⛔ ATURAN KESELAMATAN (WAJIB DIPATUHI, GAK ADA PENGECUALIAN)

- **Dilarang** menghapus apapun yang ada di dalam folder yang biasanya berisi source code aktif: `src/`, `app/`, `lib/`, `components/`, `pages/`, dsb — kecuali memang jelas-jelas cache/build output (misal `dist/`, `.next/`, `build/` — itu boleh, karena hasil build bukan source).
- **Dilarang** menghapus file config penting: `.env.example`, `package.json`, `tsconfig.json`, `.gitignore`, `README.md`, dsb — bahkan kalau kelihatan "gak dipakai".
- **Dilarang** menghapus apapun di dalam `.git/` folder itu sendiri.
- Kalau ada file yang namanya ambigu (gak jelas sampah atau bukan), **JANGAN dihapus otomatis**. Masukkan ke daftar "Perlu Dicek Manual" di laporan akhir dan biarkan user yang putuskan.
- Sebelum eksekusi hapus massal, **tampilkan dulu daftar lengkap** apa yang mau dihapus (path-nya, bukan cuma jumlahnya) dan **tunggu konfirmasi user** — jangan langsung eksekusi tanpa persetujuan, kecuali user sudah bilang "langsung hapus aja tanpa nanya lagi" di awal sesi.

---

## FASE 1 — SCAN & IDENTIFIKASI FILE SAMPAH

Cari dan kelompokkan file/folder berikut (sesuaikan dengan stack project yang terdeteksi — jangan asal cari semua kategori kalau project-nya jelas bukan Python misalnya):

### Kategori Cache & Build Artifact
- Python: `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `*.egg-info/`, `.tox/`
- Node/JS/TS: `node_modules/` (kalau memang belum di-ignore), `.next/`, `dist/`, `build/`, `.turbo/`, `.parcel-cache/`, `coverage/`
- Editor/OS: `.DS_Store`, `Thumbs.db`, `.vscode/` (kalau isinya cuma setting lokal, bukan shared config), `*.swp`, `*.swo`
- Env & log sementara: `*.log`, `.env.local` (hati-hati — cek dulu isinya bukan secret yang masih dipakai), `npm-debug.log*`, `yarn-error.log*`
- Lainnya yang terdeteksi: file dengan pola `*.tmp`, `*.bak`, `*_backup`, folder `temp/` atau `tmp/`

### Cara Kerja FASE 1:
1. Scan seluruh struktur folder project.
2. Kelompokkan temuan per kategori di atas.
3. Cek juga isi `.gitignore` yang sudah ada — kalau sebuah pola sudah ter-ignore, tetap laporkan apakah file fisiknya masih nyangkut di folder (soalnya `.gitignore` cuma ngaruh ke file yang belum pernah di-track, gak otomatis menghapus yang sudah ada).
4. Tampilkan hasil scan dalam bentuk laporan:

```
🗑️ FILE/FOLDER SAMPAH YANG TERDETEKSI

[Kategori: Python Cache]
- __pycache__/ (12 folder ditemukan, total X MB)
- .pytest_cache/

[Kategori: Node Build Artifact]
- .next/ (X MB)
- dist/

[Kategori: OS/Editor Junk]
- .DS_Store (5 file tersebar di berbagai folder)

⚠️ PERLU DICEK MANUAL (ambigu, gak langsung dihapus):
- [nama file] — alasan kenapa ambigu

Total yang akan dihapus: [jumlah] item, estimasi [X MB] dibebaskan.

Lanjut hapus semua yang di atas (kecuali yang "perlu dicek manual")? (y/n)
```

5. **Tunggu konfirmasi user** sebelum eksekusi hapus (kecuali sudah diizinkan di awal sesi untuk langsung eksekusi).

---

## FASE 2 — EKSEKUSI PENGHAPUSAN

- Hapus item yang sudah dikonfirmasi user.
- **Sekaligus pastikan pola-pola yang baru dihapus itu masuk ke `.gitignore`** kalau belum ada, biar gak muncul lagi ke depannya. Tambahkan section baru di `.gitignore` dengan komentar jelas, contoh:
  ```
  # === Ditambahkan otomatis oleh cleanup ===
  __pycache__/
  *.pyc
  .next/
  dist/
  .DS_Store
  ```
- Setelah hapus, laporkan ringkas: berapa item terhapus, berapa MB dibebaskan, dan pola apa saja yang baru ditambahkan ke `.gitignore`.

---

## FASE 3 — KUMPULKAN DOKUMENTASI, PROMPT, DAN AUDIT LOG KE 1 FOLDER

Tujuan fase ini: **bukan menghapus**, tapi **memindahkan & merapikan** semua file milik user yang sifatnya dokumentasi/prompt/log — supaya gak berserakan di root atau nyampur sama source code, dan gak ikut ke-push sembarangan tanpa struktur.

### 1. Identifikasi kandidat file
Cari file dengan ciri-ciri berikut, di manapun lokasinya di dalam project (kecuali di dalam `node_modules/`, `.git/`, atau cache yang sudah dihapus di FASE 2):

- **Dokumentasi**: file `.md`, `.txt` yang isinya penjelasan/dokumentasi manual (bukan `README.md` di root — itu biarin di tempat karena itu konvensi GitHub), misal `NOTES.md`, `ARCHITECTURE.md`, `*_analisis.md`, dsb.
- **Prompt**: file yang isinya prompt AI/instruksi ke AI agent — biasanya `.md` atau `.txt` dengan nama mengandung kata seperti `prompt`, `instruction`, `system_prompt`, atau isinya jelas-jelas format prompt (ada heading seperti "KONTEKS & TUJUAN", "ATURAN", dsb).
- **Audit log**: file log yang isinya catatan aktivitas/histori kerja user atau AI agent, misal `*.log` yang bukan log runtime aplikasi, `audit_log*.md`, `changelog_manual*.txt`, dsb. (Hati-hati jangan salah kumpulin log runtime aplikasi yang memang harus di-ignore/dihapus, bukan disimpan — tanya user kalau ragu ini termasuk kategori mana.)

### 2. Struktur folder tujuan
Buat (kalau belum ada) struktur folder terpusat berikut di root project:

```
project-docs/
├── documentation/     ← semua file dokumentasi
├── prompts/           ← semua file prompt AI
└── audit-logs/        ← semua file audit log
```

(Kalau user sudah punya nama folder pilihan sendiri, misal `docs/` atau `_internal/`, tanya dulu preferensinya sebelum bikin folder baru — jangan asumsi nama folder tanpa konfirmasi kalau belum pernah disebut sebelumnya.)

### 3. Pindahkan file
- Pindahkan (bukan copy, bukan hapus yang lama tanpa mindah) setiap file ke sub-folder yang sesuai kategorinya.
- Kalau ada nama file yang bentrok di folder tujuan, jangan menimpa — beri suffix, misal `_2`, `_3`, dst, dan laporkan bentrokan itu ke user.
- **Update referensi internal** kalau ada file lain yang me-link ke file yang dipindah (misal link relatif di `README.md`), supaya link-nya gak putus. Kalau terlalu banyak/ribet untuk dicek otomatis, laporkan daftar link yang berpotensi putus ke user.

### 4. Tambahkan ke `.gitignore` (opsional, tanya dulu)
Tanyakan ke user: apakah folder `project-docs/` ini **mau ikut di-push ke GitHub** atau **mau di-ignore** (karena isinya prompt/log internal yang sifatnya privat)?
- Kalau user bilang **jangan ikut push** → tambahkan `project-docs/` ke `.gitignore`.
- Kalau user bilang **boleh ikut push** → biarkan saja, gak usah ditambahin ke `.gitignore`.
- Jangan asumsikan salah satu tanpa nanya, karena ini keputusan yang berdampak ke privasi.

### 5. Laporan akhir FASE 3
```
📂 FILE YANG DIPINDAHKAN KE project-docs/

[documentation/] — X file
- [path lama] → [path baru]
...

[prompts/] — X file
- [path lama] → [path baru]
...

[audit-logs/] — X file
- [path lama] → [path baru]
...

⚠️ Link yang berpotensi putus (perlu dicek manual):
- [file] baris [n]: link ke [path lama yang sudah pindah]

project-docs/ [akan / tidak akan] di-push ke GitHub sesuai pilihan kamu.
```

---

## ATURAN OUTPUT & PERILAKU

- **Selalu tampilkan preview/rencana dulu sebelum eksekusi** untuk operasi hapus maupun pindah file — kecuali user sudah eksplisit bilang "langsung eksekusi semua tanpa konfirmasi" di awal sesi ini.
- **Jangan ngasih laporan lebay/panjang di chat kalau sudah dieksekusi** — cukup ringkasan hasil akhir (jumlah file, kategori, lokasi baru), bukan re-list ulang isi file.
- Kalau kamu jalan sebagai AI agent di IDE (bukan chat biasa), **kerjain langsung di filesystem**, laporan cukup singkat di akhir — gak perlu narasi panjang di tiap langkah kecil.
- Selalu double-check: **jangan pernah menghapus file yang statusnya masih untracked tapi penting** (misal file baru yang belum sempat di-commit user) — bedakan antara "sampah hasil build/cache" vs "kerjaan baru yang belum di-commit". Kalau ragu, itu masuk kategori "perlu dicek manual", bukan langsung dihapus.
