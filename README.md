# Cermin Algoritma: siapa yang terlihat ketika umpan memilih bobotnya

![tests](https://github.com/badaruddin-arete/cermin-algoritma/actions/workflows/tests.yml/badge.svg)

> Status: tahap awal. Baru generator data fiktif dan pengujiannya. Skema bobot umpan, metrik paparan, dan grafik menyusul.

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

## Keputusan desain

| Keputusan | Alasan |
|---|---|
| Mutu laten diambil dari sebaran yang sama, Beta(2, 2), untuk semua kelompok | Bila paparan nanti timpang, sebabnya dapat dilacak ke bobot umpan, bukan ke perbedaan mutu. |
| Mutu laten tidak terlihat oleh umpan | Platform nyata juga hanya melihat sinyal (tonton, *like*), bukan mutu itu sendiri. |
| Pembuat besar lebih banyak diikuti dan lebih aktif | Ketimpangan awal ini sengaja dibuat, supaya terlihat apakah sebuah skema memperbesar atau meredamnya. |
| *Seed* tetap dan hanya pustaka standar `random` | Siapa pun dapat menjalankan ulang dan mendapat angka yang sama. |
| Data seluruhnya fiktif | Tidak ada data pribadi, dan tidak ada klaim tentang platform tertentu. |

## Keterbatasan

- Data fiktif hanya memperlihatkan **mekanisme**. Hasilnya tidak membuktikan bagaimana platform nyata berperilaku.
- Angka-angka dasar (jumlah pembuat, peluang diikuti, bobot keaktifan) adalah pilihan penyusun, bukan hasil pengukuran. Mengubahnya dapat mengubah hasil.
- Belum ada skema bobot dan metrik paparan pada tahap ini.

## Menjalankan

```bash
pip install -r requirements.txt
python -m pytest
PYTHONPATH=src python -m cermin.data
```

## Transparansi bantuan AI

Rancangan, kode, dan pengujian disusun dengan bantuan AI (Claude). Pilihan kasus, keputusan desain, dan peninjauan dilakukan oleh saya.

## Lisensi

All rights reserved. Kode ini dapat dibaca dan dipelajari, tetapi tidak boleh disalin atau dipakai ulang tanpa izin tertulis. Lihat [LICENSE](LICENSE).
