"""Seberapa kuat temuan bergantung pada seed dan pada asumsi penonton awal.

Dua pertanyaan:
1. Banyak seed: apakah temuan satu seed (2026) mewakili, atau kebetulan?
2. Sapuan koefisien: bila penonton awal tidak lagi sebanding dengan jumlah
   pengikut (koefisien 0), apakah skema berbasis hitungan mutlak tetap
   menjepit pembuat baru?
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

from .data import buat_dataset
from .simulasi import jalankan
from .umpan import DASAR_BAWAAN, KOEF_BAWAAN, SKEMA

SEED_BANYAK = tuple(range(1, 51))
KOEFISIEN_SAPUAN = (0.0, 0.05, 0.1, 0.25, 0.5, 1.0)
SEED_SAPUAN = tuple(range(1, 21))
DASAR_SAPUAN = 20  # penonton awal minimum, supaya sinyal berarti saat koefisien 0


@dataclass(frozen=True)
class Rentang:
    rata: float
    minimum: float
    maksimum: float


@dataclass(frozen=True)
class RingkasanSkema:
    porsi_baru: Rentang  # porsi tayangan kelompok baru, 0..1
    porsi_besar: Rentang
    gini: Rentang


def _rentang(nilai: list[float]) -> Rentang:
    return Rentang(mean(nilai), min(nilai), max(nilai))


def banyak_seed(
    seeds: tuple[int, ...] = SEED_BANYAK,
    dasar: int = DASAR_BAWAAN,
    koef: float = KOEF_BAWAAN,
    jumlah_pengguna: int = 200,
    jumlah_kiriman: int = 1000,
) -> dict[str, RingkasanSkema]:
    """Jalankan semua skema pada tiap seed, lalu ringkas sebagai rentang."""
    if not seeds:
        raise ValueError("seeds tidak boleh kosong")
    baru: dict[str, list[float]] = {n: [] for n in SKEMA}
    besar: dict[str, list[float]] = {n: [] for n in SKEMA}
    gini: dict[str, list[float]] = {n: [] for n in SKEMA}
    for seed in seeds:
        ds = buat_dataset(seed, jumlah_pengguna, jumlah_kiriman)
        for nama, p in jalankan(ds, dasar, koef).items():
            baru[nama].append(p.porsi_tayangan["baru"])
            besar[nama].append(p.porsi_tayangan["besar"])
            gini[nama].append(p.gini_pembuat)
    return {
        n: RingkasanSkema(_rentang(baru[n]), _rentang(besar[n]), _rentang(gini[n]))
        for n in SKEMA
    }


def sapu_koefisien(
    koefisien: tuple[float, ...] = KOEFISIEN_SAPUAN,
    seeds: tuple[int, ...] = SEED_SAPUAN,
    dasar: int = DASAR_SAPUAN,
    jumlah_pengguna: int = 200,
    jumlah_kiriman: int = 1000,
) -> dict[float, dict[str, RingkasanSkema]]:
    """Ulangi ``banyak_seed`` untuk tiap koefisien penonton awal."""
    return {
        k: banyak_seed(seeds, dasar, k, jumlah_pengguna, jumlah_kiriman)
        for k in koefisien
    }


BERKAS_BUKTI = Path("docs/kepekaan.json")


def simpan(
    seed_banyak: dict[str, RingkasanSkema],
    sapuan: dict[float, dict[str, RingkasanSkema]],
    berkas: Path = BERKAS_BUKTI,
) -> None:
    """Simpan angka mentah agar tabel README dapat diperiksa tanpa menjalankan ulang."""
    isi = {
        "seed_banyak": {"seed": list(SEED_BANYAK), "hasil": {n: asdict(r) for n, r in seed_banyak.items()}},
        "sapuan": {
            "seed": list(SEED_SAPUAN),
            "dasar": DASAR_SAPUAN,
            "hasil": {str(k): {n: asdict(r) for n, r in v.items()} for k, v in sapuan.items()},
        },
    }
    berkas.parent.mkdir(parents=True, exist_ok=True)
    berkas.write_text(json.dumps(isi, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def muat(berkas: Path = BERKAS_BUKTI) -> tuple[dict[str, dict], dict[str, dict[str, dict]]]:
    isi = json.loads(berkas.read_text(encoding="utf-8"))
    return isi["seed_banyak"]["hasil"], isi["sapuan"]["hasil"]


def _persen(r: Rentang) -> str:
    return f"{r.rata * 100:5.1f}% ({r.minimum * 100:.0f}-{r.maksimum * 100:.0f})"


def tabel_seed(hasil: dict[str, RingkasanSkema]) -> str:
    kepala = f"{'skema':<13}{'porsi baru, rata (min-maks)':>30}{'Gini rata (min-maks)':>26}"
    baris = [kepala, "-" * len(kepala)]
    for nama, r in hasil.items():
        g = r.gini
        baris.append(
            f"{nama:<13}{_persen(r.porsi_baru):>30}"
            f"{g.rata:>12.2f} ({g.minimum:.2f}-{g.maksimum:.2f})"
        )
    return "\n".join(baris)


def tabel_sapuan(hasil: dict[float, dict[str, RingkasanSkema]]) -> str:
    koefisien = list(hasil)
    kepala = f"{'porsi baru (rata)':<18}" + "".join(f"{'koef ' + str(k):>11}" for k in koefisien)
    baris = [kepala, "-" * len(kepala)]
    for nama in SKEMA:
        sel = "".join(f"{hasil[k][nama].porsi_baru.rata * 100:>10.1f}%" for k in koefisien)
        baris.append(f"{nama:<18}{sel}")
    return "\n".join(baris)


def main() -> None:
    seed_banyak = banyak_seed()
    print(f"== {len(SEED_BANYAK)} seed, konfigurasi bawaan ==")
    print(tabel_seed(seed_banyak))
    sapuan = sapu_koefisien()
    print(f"\n== sapuan koefisien, {len(SEED_SAPUAN)} seed, dasar {DASAR_SAPUAN} ==")
    print(tabel_sapuan(sapuan))
    simpan(seed_banyak, sapuan)
    print(f"\nangka mentah ditulis ke {BERKAS_BUKTI}")


if __name__ == "__main__":
    main()
