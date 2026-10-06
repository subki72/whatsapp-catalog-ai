# 📚 AI System Prompts & Engineering Library

Repositori ini berisi kumpulan prompt terstruktur, sistem agen AI, dan materi mentoring teknis untuk seluruh siklus pengembangan software (SDLC) serta pembelajaran pemrograman.

Seluruh prompt telah dirapikan penamaannya menggunakan konvensi *kebab-case* deskriptif dan dikelompokkan ke dalam 7 kategori modular.

---

## 🗂️ Struktur Direktori

```
project-docs/prompts/
├── 01-setup-and-planning/        # Inisiasi, pemilihan arsitektur, & audit awal
├── 02-coding-and-standards/      # Standar penulisan kode & senior craftsmanship
├── 03-code-analysis-and-docs/    # Pemahaman kode, alur data, & dokumentasi
├── 04-qa-audit-and-security/     # QA komprehensif, keamanan, & evaluasi keyakinan
├── 05-bugfixing-and-refinement/  # Remediasi bug adaptif & perbaikan UI/UX
├── 06-repo-and-cleanup/          # Sanitasi repo & konsolidasi file
└── 07-learning-and-mentoring/    # Modul belajar Rust & STEM AI Tutor
```

---

## 📖 Katalog Lengkap Prompt

### 1. `01-setup-and-planning/` — Persiapan & Perencanaan
Fase inisiasi sebelum menulis kode atau saat mengambil alih codebase yang sudah ada.

| File | Deskripsi & Peran |
|:---|:---|
| [`pre-coding-setup-master.md`](./01-setup-and-planning/pre-coding-setup-master.md) | **Master Pre-Coding Setup** (4 Fase, 13 Dokumen): Memetakan aturan, arsitektur, data flow, dan standarisasi sebelum satu baris kode pun dibuat. |
| [`ml-dl-algorithm-selection.md`](./01-setup-and-planning/ml-dl-algorithm-selection.md) | **ML/DL Algorithm Selection & Evaluation**: Membantu memilih algoritma ML/DL terbaik berdasarkan kriteria data, komputasi, dan trade-off. |
| [`project-resume-and-roadmap-audit.md`](./01-setup-and-planning/project-resume-and-roadmap-audit.md) | **Project Resume & Roadmap Audit**: Onboarding mandiri AI ke project yang sempat terbengkalai, memetakan status aktual roadmap vs dokumentasi. |

---

### 2. `02-coding-and-standards/` — Standar Penulisan & Kualitas Kode
Panduan penulisan kode tingkat senior dan penegakan konvensi otomatis.

| File | Deskripsi & Peran |
|:---|:---|
| [`coding-standards-enforcement.md`](./02-coding-and-standards/coding-standards-enforcement.md) | **Senior Code Standards Enforcement**: Penerapan otomatis standar kode senior (DRY, defensive coding, type safety, idiomatis) saat menghasilkan kode. |
| [`senior-code-craftsmanship.md`](./02-coding-and-standards/senior-code-craftsmanship.md) | **Senior Code Craftsmanship (Multi-Language)**: Mengajar cara berpikir arsitek senior dalam memilih pendekatan, alternatif, dan trade-off kode. |

---

### 3. `03-code-analysis-and-docs/` — Analisis Kode & Dokumentasi
Alat bantu membedah kode asing, memahami arsitektur, dan memetakan alur pemanggilan data.

| File | Deskripsi & Peran |
|:---|:---|
| [`comprehensive-project-documentation.md`](./03-code-analysis-and-docs/comprehensive-project-documentation.md) | **Comprehensive Documentation & Walkthrough**: Membangun dokumentasi proyek lengkap dari overview, arsitektur, alur eksekusi hingga panduan test. |
| [`file-deep-dive-analysis.md`](./03-code-analysis-and-docs/file-deep-dive-analysis.md) | **Analisa Deep Dive Per-File**: Membedah satu file kode secara mendalam (Tujuan, Logika, Dependency, Aliran Data, Breakage Risk, Mental Model). |
| [`code-analysis-senior-mentor-id.md`](./03-code-analysis-and-docs/code-analysis-senior-mentor-id.md) | **Analis Kode Gaya Mentor (Bahasa Indonesia)**: Penjelasan kode santai dan intuitif dari sudut pandang mentor senior ke junior. |
| [`per-file-dataflow-generic.md`](./03-code-analysis-and-docs/per-file-dataflow-generic.md) | **Per-File Data Flow Documentation (Generic)**: Membangun dokumentasi peta alur data per-file setingkat function-call dari nol. |
| [`per-file-dataflow-enrichment.md`](./03-code-analysis-and-docs/per-file-dataflow-enrichment.md) | **Per-File Data Flow Enrichment**: Memperkaya file `workflow_lengkap.md` dengan section detail aliran fungsi per file. |
| [`understand-me-project-pack.md`](./03-code-analysis-and-docs/understand-me-project-pack.md) | **UNDERSTAND_ME Prompt Pack**: Template panduan komprehensif bagi developer untuk memahami project buatan AI agent (Big picture, Tech stack, DevOps). |

---

### 4. `04-qa-audit-and-security/` — QA, Audit Keamanan & Evaluasi Keyakinan
Pemeriksaan sistematis terhadap bug logika, celah keamanan, kesiapan production, dan transparansi AI.

| File | Deskripsi & Peran |
|:---|:---|
| [`qa-security-comprehensive-audit.md`](./04-qa-audit-and-security/qa-security-comprehensive-audit.md) | **Comprehensive QA & Security Audit**: Audit terstruktur untuk mencari bug sintaks, logika, celah keamanan API, dan integritas data. |
| [`qa-end-to-end-audit.md`](./04-qa-audit-and-security/qa-end-to-end-audit.md) | **QA End-to-End Audit**: Audit menyeluruh skala besar mencakup logika kode, bisnis, UI, UX, Database, API, dan security dengan strategi hemat context. |
| [`qa-code-quality-audit.md`](./04-qa-audit-and-security/qa-code-quality-audit.md) | **Code Quality Reviewer**: Audit cara penulisan kode di level teknis (performa, memori, tipe data, risiko bug) dengan output modular ke file markdown. |
| [`production-readiness-audit.md`](./04-qa-audit-and-security/production-readiness-audit.md) | **Production-Readiness Audit**: Evaluasi checklist kesiapan peluncuran sistem ke lingkungan production (skalabilitas, monitoring, failover). |
| [`prompt_qa_readability_consistency.md`](./04-qa-audit-and-security/prompt_qa_readability_consistency.md) | **QA Readability & Consistency Audit**: Audit konsistensi bahasa (EN/ID) dan kerapihan penulisan kode tanpa side-effect modifikasi. |
| [`codebase-confidence-audit.md`](./04-qa-audit-and-security/codebase-confidence-audit.md) | **Codebase Confidence Audit**: AI memetakan bagian codebase yang tingkat keyakinannya rendah dan membutuhkan verifikasi mata manusia. |
| [`post-task-confidence-report.md`](./04-qa-audit-and-security/post-task-confidence-report.md) | **Honest Confidence Report**: Laporan penutup wajib pasca-task tentang bagian mana yang teruji pasti vs bagian yang masih ada keraguan teknis. |

---

### 5. `05-bugfixing-and-refinement/` — Perbaikan Bug & UI Refinement
Eksekusi perbaikan bug terstruktur dan peningkatan estetika desain.

| File | Deskripsi & Peran |
|:---|:---|
| [`adaptive-bug-remediation.md`](./05-bugfixing-and-refinement/adaptive-bug-remediation.md) | **Bug Remediation Agent (Adaptive Batching)**: Eksekusi perbaikan bug secara bertahap dan aman berdasarkan daftar audit report tanpa merusak kode existing. |
| [`ui-ux-degenericize-design.md`](./05-bugfixing-and-refinement/ui-ux-degenericize-design.md) | **De-Genericize UI/UX Agent**: Transformasi antarmuka agar terbebas dari kesan generic/template AI dan memiliki identitas visual produk yang unik. |

---

### 6. `06-repo-and-cleanup/` — Pembersihan & Pengorganisasian Repositori
Menghapus file cache, sampah build, dan menata dokumentasi sebelum commit/push ke Git.

| File | Deskripsi & Peran |
|:---|:---|
| [`project-cleanup-and-organization.md`](./06-repo-and-cleanup/project-cleanup-and-organization.md) | **Project Cleanup & Organization**: Membersihkan build artifact, memvalidasi `.gitignore`, dan merapikan folder project. |
| [`repo-cleanup-and-consolidation.md`](./06-repo-and-cleanup/repo-cleanup-and-consolidation.md) | **Repo Cleanup & Doc Consolidation**: Pembersihan repo dengan aturan ketat Dry-Run (Safety First) dan konsolidasi dokumentasi berserakan. |
| [`github-pre-push-cleanup-id.md`](./06-repo-and-cleanup/github-pre-push-cleanup-id.md) | **Beres-beres Repo Pra-Push (Bahasa Indonesia)**: Panduan langkah demi langkah membersihkan repo sebelum dipublikasikan ke GitHub. |

---

### 7. `07-learning-and-mentoring/` — Pembelajaran & Mentoring Khusus
Materi pembelajaran terstruktur untuk bahasa Rust dan gaya belajar terpersonalisasi.

| File | Deskripsi & Peran |
|:---|:---|
| [`rust-learning-mentor-python-to-rust.md`](./07-learning-and-mentoring/rust-learning-mentor-python-to-rust.md) | **Rust Learning Mentor (Python to Rust)**: Instruktur Rust interaktif dengan tempo bertahap yang disesuaikan untuk developer Python. |
| [`rust-project-analysis-and-learning.md`](./07-learning-and-mentoring/rust-project-analysis-and-learning.md) | **Rust Project Analysis & Learning**: Menguraikan project Rust yang sudah ada menjadi bahan ajar berbasis konsep dan sintaks. |
| [`rust-syntax-logic-deepdive.md`](./07-learning-and-mentoring/rust-syntax-logic-deepdive.md) | **Rust Syntax & Logic Deep-Dive**: Micro-learning fokus mendalam pada metode, operator (`?`), atau konstruksi sintaks spesifik Rust. |
| [`prompt_codebase_deep_dive.md`](./07-learning-and-mentoring/prompt_codebase_deep_dive.md) | **Codebase Deep-Dive Explainer**: Menjelaskan arsitektur codebase dari awal hingga akhir per-sintaks dan per-logika dengan detail tinggi. |
| [`personalized-ai-tutor-stem.docx`](./07-learning-and-mentoring/personalized-ai-tutor-stem.docx) | **Personalized AI Tutor (Top-Down STEM)**: Panduan strategi AI tutor untuk gaya belajar pembaca/penulis berbasis gambaran besar ke detail. |

---

## 💡 Rekomendasi Alur Penggunaan (SDLC Workflow)

1. **Inisiasi Proyek**: Gunakan `01-setup-and-planning/pre-coding-setup-master.md`.
2. **Saat Menulis Kode**: Pasang `02-coding-and-standards/coding-standards-enforcement.md` sebagai instruksi aktif.
3. **Mempelajari/Mendokumentasikan**: Gunakan `03-code-analysis-and-docs/comprehensive-project-documentation.md` atau `understand-me-project-pack.md`.
4. **Sebelum Rilis**: Jalankan `04-qa-audit-and-security/qa-security-comprehensive-audit.md` dilanjutkan `production-readiness-audit.md`.
5. **Perbaikan Temuan**: Terapkan `05-bugfixing-and-refinement/adaptive-bug-remediation.md`.
6. **Sebelum Push ke GitHub**: Bersihkan repo dengan `06-repo-and-cleanup/repo-cleanup-and-consolidation.md`.
