"""Jalankan semua skema pada dataset yang sama dan bandingkan paparannya."""

from __future__ import annotations

from .data import KELOMPOK, Dataset, buat_dataset
from .metrik import Paparan, ukur
from .umpan import SKEMA, buat_konteks, susun_umpan


def jalankan(ds: Dataset) -> dict[str, Paparan]:
    konteks = buat_konteks(ds)
    return {nama: ukur(ds, susun_umpan(konteks, nama)) for nama in SKEMA}


def tabel(hasil: dict[str, Paparan]) -> str:
    kepala = f"{'skema':<13}" + "".join(f"{'tayang ' + k:>16}" for k in KELOMPOK)
    kepala += f"{'Gini':>8}{'tak tampil':>12}"
    baris = [kepala, "-" * len(kepala)]
    for nama, p in hasil.items():
        sel = "".join(f"{p.porsi_tayangan[k] * 100:>15.1f}%" for k in KELOMPOK)
        baris.append(f"{nama:<13}{sel}{p.gini_pembuat:>8.2f}{p.pembuat_tak_tampil:>12}")
    any_p = next(iter(hasil.values()))
    porsi = "".join(f"{any_p.porsi_kiriman[k] * 100:>15.1f}%" for k in KELOMPOK)
    baris.append(f"{'(porsi kiriman)':<13}{porsi}")
    return "\n".join(baris)


def main() -> None:
    ds = buat_dataset()
    print(tabel(jalankan(ds)))


if __name__ == "__main__":
    main()
