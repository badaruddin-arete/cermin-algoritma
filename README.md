# Cermin Algoritma: siapa yang terlihat ketika umpan memilih bobotnya

![tests](https://github.com/badaruddin-arete/cermin-algoritma/actions/workflows/tests.yml/badge.svg)

> Status: dalam pengerjaan. Sudah ada generator data, tujuh skema umpan, dan metrik paparan. Grafik perbandingan menyusul.

## Gagasan

Langdon Winner, dalam esai "Do Artifacts Have Politics?" (*Daedalus*, vol. 109, no. 1, 1980), berpendapat bahwa sebuah artefak teknis dapat mengandung pengaturan kuasa: rancangannya sendiri ikut menentukan siapa diuntungkan dan siapa tersingkir, bukan hanya cara orang memakainya.

Proyek ini menguji gagasan itu pada benda yang lebih dekat dengan keseharian: **rumus pengurut umpan**. Pertanyaannya: bila mutu kiriman dibuat setara antarkelompok pembuat, apakah pilihan bobot (waktu tonton, *like*, kebaruan, kesamaan minat) dengan sendirinya menggeser paparan ke kelompok tertentu?

Bentuknya percobaan yang bisa dijalankan ulang, bukan esai: data fiktif dengan *seed* tetap, beberapa skema bobot, lalu paparan tiap kelompok diukur dengan angka yang sama.

## Kasus fiktif: Warung Kabar

| Unsur | Isi |
|---|---|
| Pengguna | 200, masing-masing punya minat pada 6 topik |
| Pembuat | 40, dalam tiga kelompok: besar (5), menengah (15), baru (20) |
| Kiriman | 1.000, dengan topik, umur, durasi, dan mutu laten |
| Relasi ikut | pembuat besar lebih sering diikuti daripada menengah dan baru |

Contoh ringkasan untuk *seed* 2026:

```text
Warung Kabar (fiktif), seed 2026
  pengguna: 200, pembuat: 40, kiriman: 1000
  besar     pembuat  5, kiriman  224, rerata pengikut  79.8
  menengah  pembuat 15, kiriman  515, rerata pengikut  20.8
  baru      pembuat 20, kiriman  261, rerata pengikut   3.7
```

## Skema umpan yang dibandingkan

Untuk tiap pengguna, umpan berisi 20 kiriman teratas menurut skema. Umpan hanya melihat sinyal, tidak pernah melihat mutu laten.

| Skema | Cara menimbang |
|---|---|
| `acak` | Urutan acak. Pembanding: apa yang terjadi bila umpan tidak memihak. |
| `kronologis` | Yang terbaru lebih dulu. |
| `suka` | Jumlah suka mutlak. |
| `suka_rasio` | Suka per penonton awal (dengan penghalus). |
| `waktu_tonton` | Total detik tonton. |
| `kesamaan` | Kecocokan topik dengan minat pengguna saja. |
| `campuran` | 0,4 kesamaan + 0,3 suka (skala log) + 0,3 kebaruan. |

## Hasil percobaan (seed 2026)

Porsi tayangan per kelompok pembuat. Sebagai patokan, porsi kiriman: besar 22,4%, menengah 51,5%, baru 26,1%.

| Skema | Besar | Menengah | Baru | Gini antarpembuat | Pembuat tanpa tayangan (dari 40) |
|---|---:|---:|---:|---:|---:|
| acak | 22,2% | 52,3% | 25,5% | 0,31 | 0 |
| kronologis | 20,0% | 55,0% | 25,0% | 0,72 | 26 |
| suka | 100,0% | 0,0% | 0,0% | 0,92 | 35 |
| suka_rasio | 35,0% | 60,0% | 5,0% | 0,70 | 25 |
| waktu_tonton | 100,0% | 0,0% | 0,0% | 0,91 | 35 |
| kesamaan | 22,2% | 57,4% | 20,4% | 0,45 | 6 |
| campuran | 71,1% | 28,9% | 0,0% | 0,79 | 21 |

Yang dapat dikatakan dari tabel ini, dan yang tidak:

- Mutu kiriman setara di ketiga kelompok, tetapi skema berbasis hitungan mutlak (`suka`, `waktu_tonton`) memberi nyaris seluruh tayangan ke kelompok besar. Pada seed 1, 2, dan 3 pembuat baru tetap mendapat 0% di kedua skema itu (diuji otomatis).
- Mengganti hitungan mutlak menjadi per penonton (`suka_rasio`) menurunkan ketimpangan, tetapi tidak menghapusnya. Pada seed 2026 pembuat baru naik ke 5%, pada seed 2 tetap 0%.
- **Hasil ini sebagian besar tertanam dalam asumsi model**: penonton awal dibuat sebanding dengan jumlah pengikut. Karena itu tabel menunjukkan *bagaimana* sebuah rumus meneruskan keunggulan awal, bukan *seberapa besar* hal itu terjadi di platform nyata.
- Skema yang sama untuk semua pengguna (`kronologis`, `suka`, `waktu_tonton`) menampilkan 20 kiriman yang itu-itu saja. Sebagian ketimpangannya berasal dari pemotongan "20 teratas", bukan hanya dari bobotnya.

## Keputusan desain

| Keputusan | Alasan |
|---|---|
| Mutu laten diambil dari sebaran yang sama, Beta(2, 2), untuk semua kelompok | Bila paparan nanti timpang, sebabnya dapat dilacak ke bobot umpan, bukan ke perbedaan mutu. |
| Mutu laten tidak terlihat oleh umpan | Platform nyata juga hanya melihat sinyal (tonton, *like*), bukan mutu itu sendiri. |
| Pembuat besar lebih banyak diikuti dan lebih aktif | Ketimpangan awal ini sengaja dibuat, supaya terlihat apakah sebuah skema memperbesar atau meredamnya. |
| *Seed* tetap dan hanya pustaka standar `random` | Siapa pun dapat menjalankan ulang dan mendapat angka yang sama. |
| Penonton awal sebanding dengan pengikut, suka bergantung pada mutu | Mewakili dua hal yang masuk akal: kiriman bermutu lebih disukai, dan pembuat berpengikut banyak lebih dulu dilihat. Asumsi ini menentukan hasil dan ditulis terang. |
| Ada skema `acak` sebagai pembanding | Tanpa patokan "tidak memihak", angka tiap skema sulit ditafsirkan. |
| Dua versi skema suka: mutlak dan per penonton | Memperlihatkan bahwa satu keputusan kecil dalam rumus mengubah siapa yang tampil. |
| Metrik: porsi tayangan per kelompok dan Gini antarpembuat | Porsi mudah dibaca; Gini menangkap ketimpangan di dalam kelompok juga. |
| Data seluruhnya fiktif | Tidak ada data pribadi, dan tidak ada klaim tentang platform tertentu. |

## Keterbatasan

- Data fiktif hanya memperlihatkan **mekanisme**. Hasilnya tidak membuktikan bagaimana platform nyata berperilaku.
- Angka-angka dasar (jumlah pembuat, peluang diikuti, bobot keaktifan) adalah pilihan penyusun, bukan hasil pengukuran. Mengubahnya dapat mengubah hasil.
- Satu putaran saja: tidak ada umpan balik (kiriman yang tampil lalu makin banyak disukai). Efek penguatan berulang belum dimodelkan.
- Pengguna melihat 20 kiriman tanpa memperhitungkan posisi; di platform nyata posisi atas jauh lebih sering dilihat.
- Sinyal awal adalah buatan model, bukan perilaku pengguna sungguhan; angka ambang (mis. 0,3 peluang suka) dipilih penyusun.
- Hasil pada satu seed bisa berbeda; hanya temuan yang diuji pada beberapa seed yang diklaim di atas.

## Menjalankan

```bash
pip install -r requirements.txt
pip install -e .
python -m pytest
python -m cermin.data       # ringkasan data fiktif
python -m cermin.simulasi   # tabel perbandingan skema
```

46 uji otomatis mencakup generator data (determinisme, sebaran, relasi), metrik (Gini dengan hitungan tangan dan kasus batas), skema umpan, dan temuan utama pada beberapa seed.

## Transparansi bantuan AI

Rancangan, kode, dan pengujian disusun dengan bantuan AI (Claude). Pilihan kasus, keputusan desain, dan peninjauan dilakukan oleh saya.

## Lisensi

All rights reserved. Kode ini dapat dibaca dan dipelajari, tetapi tidak boleh disalin atau dipakai ulang tanpa izin tertulis. Lihat [LICENSE](LICENSE).
