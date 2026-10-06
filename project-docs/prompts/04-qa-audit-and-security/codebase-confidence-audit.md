## 📌KONTEKS & TUJUAN

Ini **bukan** laporan penutup setelah kamu ngoding. Ini adalah **audit mandiri terhadap codebase yang SUDAH ADA** (baik ditulis oleh kamu sebelumnya, developer lain, atau campuran keduanya) — tugas kamu murni untuk **membaca dan menilai**, lalu kasih tau ke user: **file/bagian mana yang kamu, sebagai AI, kurang yakin kebenarannya dan perlu dicek manual oleh manusia.**

Anggap posisi kamu seperti **auditor eksternal yang baru masuk**, bukan penulis kode aslinya. Tugasmu bukan memperbaiki apapun (kecuali diminta), murni **menilai tingkat kepercayaan** tiap area kode dan kasih peta prioritas review manual ke user — supaya waktu review manusia yang terbatas gak dihabiskan buat baca semua file secara rata, tapi fokus ke tempat yang beneran berisiko.

---

## ⛔ ATURAN KEJUJURAN (PALING PENTING, BACA DULU)

- **Dilarang keras** bilang "kode ini sudah benar semua" kalau kamu sebenarnya cuma baca sekilas tanpa run test, tanpa akses environment, atau tanpa cara lain buat beneran memverifikasi.
- **Dilarang** kasih daftar "perlu dicek" yang generik/menyeluruh tanpa alasan (misal "cek semua folder API" tanpa spesifik file/fungsi mana dan kenapa) — itu bukan sinyal berguna, itu cuma lempar balik pekerjaan ke user.
- Kalau suatu bagian **memang straightforward dan gampang divalidasi dari baca kode statis** (logikanya deterministic, gak ada asumsi bisnis tersembunyi, scope-nya kecil), **bilang itu juga dengan percaya diri** — jangan taruh semua hal ke kategori "ragu" cuma biar kelihatan hati-hati.
- Setiap area yang kamu tandai "kurang yakin" **wajib** disertai: file spesifik, fungsi/baris spesifik, **alasan konkret kenapa ragu**, dan **apa yang harus dicek manusia** — bukan cuma "cek logikanya".
- Ingat: kamu **membaca kode, bukan menjalankannya** (kecuali kamu punya akses run test/build — kalau punya, manfaatkan, dan sebut di laporan bahwa itu udah divalidasi lewat run, bukan cuma baca). Jujur soal keterbatasan ini di laporan akhir.

---

## PRINSIP KERJA HEMAT CONTEXT (WAJIB UNTUK PROJECT BESAR)

Sama seperti audit QA — codebase existing kemungkinan besar berisi ratusan file. Jangan baca semua isi file dari awal.

- **Cari dulu pola-pola berisiko pakai grep**, baru baca isi file yang ketauan relevan.
- **Prioritaskan folder/area yang secara alami paling berisiko** duluan (lihat daftar "AREA YANG WAJIB DICURIGAI" di bawah), baru ke area yang lebih aman kalau masih ada waktu/context.
- **Kerja per-batch** (per folder/modul), simpan progress ke `qa-report/_confidence_progress.md` biar kalau context habis, sesi berikutnya bisa lanjut tanpa scan ulang dari nol.
- Simpan hasil temuan ke `qa-report/confidence_audit.md`, chat cukup kasih ringkasan + top prioritas.

---

## AREA YANG WAJIB DICURIGAI DULUAN (PRIORITAS SCAN)

AI (termasuk kamu) secara struktural punya blind spot di area-area berikut. **Selalu cek area ini duluan**, apapun jenis project-nya:

1. **Business logic tanpa dokumentasi** — kalkulasi harga/diskon/komisi/skor, aturan approval, state machine bisnis (status order, status pengajuan, dsb) yang cuma bisa ditebak dari nama variabel/komentar.
2. **Routing & middleware API yang bertingkat** — terutama kalau ada banyak layer middleware (auth → rate limit → validation → business logic) yang urutannya penting; gampang salah baca urutan eksekusi atau ada middleware yang keskip di route tertentu.
3. **Concurrency & race condition** — apapun yang melibatkan async operations yang saling bergantung, shared state, queue/worker, atau operasi yang bisa dipanggil bersamaan (contoh: dua request update saldo di waktu bersamaan).
4. **Auth & permission logic** — terutama authorization (bukan cuma authentication): siapa boleh akses apa, role-based access, multi-tenant data isolation.
5. **Integrasi third-party** (payment gateway, notification service, external API) — behavior aslinya cuma bisa dikonfirmasi lewat test di sandbox mereka, bukan cuma baca kode pemanggilnya.
6. **Query database yang kompleks** — terutama yang perlu dioptimasi berdasarkan actual data volume/distribution, atau join bertingkat yang benar secara sintaks tapi belum tentu benar secara performa/hasil di skala production.
7. **Kode di framework/library versi terbaru atau jarang ditemui** — behavior spesifiknya mungkin sudah berubah dari pengetahuan kamu, atau kamu memang jarang terpapar pattern itu.
8. **File konfigurasi environment & secret management** — sering ada asumsi implisit soal environment production vs development yang gak keliatan cuma dari baca file config.
9. **Test yang keliatan lengkap tapi sebenarnya gak nge-cover skenario penting** — cek bukan cuma "ada test atau nggak", tapi apakah test-nya beneran menguji edge case atau cuma happy path.

---

## FORMAT LAPORAN

```
# 🔍 Confidence Audit Report — [tanggal]

## Ringkasan
Total file di-scan: [n]
Area dengan kepercayaan tinggi: [n]
Area dengan kepercayaan sedang: [n]
Area WAJIB dicek manual: [n]

## ✅ Kepercayaan Tinggi (kemungkinan aman, tapi tetap boleh spot-check)
- [Area/file] — [alasan: logika linear, pattern konsisten di seluruh codebase, dsb]
...

## ⚠️ Kepercayaan Sedang
- [Area/file] — [alasan ada sedikit keraguan, tapi gak fatal]
...

## 🚨 WAJIB DICEK MANUAL (urutan prioritas dari paling kritis)

### 1. [Nama area/fitur] — Prioritas: Tinggi
**File yang perlu dicek (urut):**
1. `[path file 1]` — baris/fungsi `[nama]`
2. `[path file 2]` — baris/fungsi `[nama]`
3. `[path file 3]` — baris/fungsi `[nama]`

**Kenapa saya ragu:**
[alasan konkret — kenapa area ini masuk kategori blind spot AI, spesifik ke kode ini, bukan alasan generik]

**Yang spesifik harus divalidasi manusia:**
[bukan "cek logikanya" — tapi spesifik: "cek apakah urutan middleware di sini benar-benar mencegah user role 'staff' akses endpoint admin, karena saya nemuin route ini didaftarkan di 2 tempat berbeda dengan middleware yang beda"]

**Risiko kalau ini salah dan gak ketauan:**
[dampak konkret]

### 2. [Area berikutnya]
(format sama)
...

## 🧪 Keterbatasan Audit Ini
- [Contoh: "Saya gak menjalankan test suite karena [alasan]"]
- [Contoh: "Saya gak sempat scan folder [X] karena [alasan keterbatasan context/waktu] — kalau mau, bisa lanjutkan audit ke folder itu di sesi berikutnya"]
- [Contoh: "Saya asumsikan framework versi [X] berdasarkan `package.json`, tapi behavior detail versi ini mungkin ada yang saya gak update pengetahuannya"]
```

---

## CARA NENTUIN KATEGORI (SEBELUM NULIS LAPORAN)

Tanyakan ke diri sendiri untuk tiap area/file:

1. **Bisakah saya trace seluruh logikanya cuma dari baca kode, tanpa asumsi eksternal?** Kalau ya → kandidat kepercayaan tinggi. Kalau harus nebak konteks bisnis/requirement → kurang yakin.
2. **Apakah area ini masuk salah satu dari 9 "AREA YANG WAJIB DICURIGAI" di atas?** Kalau ya → otomatis minimal kepercayaan sedang, kemungkinan besar wajib dicek manual.
3. **Apakah saya (AI) secara umum punya rekam jejak sering salah di jenis kode kayak gini?** (misal: kode yang butuh pemahaman performa di skala production, atau nuansa hukum/kebijakan spesifik yang bukan aturan universal) — kalau ya, jujur akui itu di laporan.
4. **Apakah ada test yang membuktikan ini benar, dan saya bisa jalankan?** Kalau ya dan hasilnya pass → boleh naikkan ke kepercayaan tinggi meski areanya sensitif.

---

## ATURAN OUTPUT & PERILAKU

- Ini adalah task **audit/baca saja**, bukan task ngoding — jangan ubah kode apapun kecuali user eksplisit minta setelah lihat laporan ini.
- Chat balasan **ringkas**: ringkasan angka + top 3-5 prioritas paling kritis + lokasi file laporan lengkap (`qa-report/confidence_audit.md`). Jangan re-paste seluruh isi laporan di chat.
- **Urutkan daftar "WAJIB DICEK MANUAL" dari yang paling kritis**, bukan urutan folder A-Z — user harus bisa langsung tau "kalau saya cuma sempat cek 3 hal hari ini, yang mana yang paling penting duluan".
- Kalau project terlalu besar buat di-audit sekaligus dalam 1 sesi, **bilang terus terang** di awal ("saya akan audit per-batch, mulai dari area paling berisiko dulu") daripada maksa nyelesein semua dan hasilnya jadi dangkal.
- Jangan pernah menyembunyikan keraguan demi laporan kelihatan "bersih". Laporan dengan banyak poin "wajib dicek manual" itu **hasil yang baik**, bukan tanda kamu gagal audit — itu justru nilai dari audit ini.
