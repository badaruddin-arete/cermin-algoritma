"""Metrik paparan: siapa yang kebagian tayangan."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .data import KELOMPOK, Dataset


def gini(nilai: list[float]) -> float:
    """Indeks Gini: 0 = sama rata, mendekati 1 = satu pihak memegang semua."""
    if not nilai:
        raise ValueError("daftar nilai kosong")
    if any(v < 0 for v in nilai):
        raise ValueError("nilai tidak boleh negatif")
    total = sum(nilai)
    if total == 0:
        return 0.0
    urut = sorted(nilai)
    n = len(urut)
    jumlah_berbobot = sum((i + 1) * v for i, v in enumerate(urut))
    return (2 * jumlah_berbobot) / (n * total) - (n + 1) / n


def tayangan_per_pembuat(ds: Dataset, umpan: dict[str, list[str]]) -> Counter[str]:
    """Jumlah tayangan tiap pembuat, termasuk yang nol."""
    pembuat_kiriman = {k.id: k.pembuat_id for k in ds.kiriman}
    hitung: Counter[str] = Counter({p.id: 0 for p in ds.pembuat})
    for daftar in umpan.values():
        for id_kiriman in daftar:
            hitung[pembuat_kiriman[id_kiriman]] += 1
    return hitung


@dataclass(frozen=True)
class Paparan:
    porsi_tayangan: dict[str, float]  # per kelompok, jumlahnya 1
    porsi_kiriman: dict[str, float]  # per kelompok, jumlahnya 1
    rasio: dict[str, float]  # porsi tayangan / porsi kiriman
    gini_pembuat: float  # Gini tayangan antarpembuat
    pembuat_tak_tampil: int  # pembuat dengan nol tayangan


def ukur(ds: Dataset, umpan: dict[str, list[str]]) -> Paparan:
    per_pembuat = tayangan_per_pembuat(ds, umpan)
    kelompok_pembuat = {p.id: p.kelompok for p in ds.pembuat}

    tayangan = Counter({k: 0 for k in KELOMPOK})
    for id_pembuat, n in per_pembuat.items():
        tayangan[kelompok_pembuat[id_pembuat]] += n
    kiriman = Counter({k: 0 for k in KELOMPOK})
    for k in ds.kiriman:
        kiriman[kelompok_pembuat[k.pembuat_id]] += 1

    total_tayangan = sum(tayangan.values())
    total_kiriman = sum(kiriman.values())
    porsi_t = {k: tayangan[k] / total_tayangan for k in KELOMPOK}
    porsi_k = {k: kiriman[k] / total_kiriman for k in KELOMPOK}
    return Paparan(
        porsi_tayangan=porsi_t,
        porsi_kiriman=porsi_k,
        rasio={k: porsi_t[k] / porsi_k[k] for k in KELOMPOK},
        gini_pembuat=gini([float(v) for v in per_pembuat.values()]),
        pembuat_tak_tampil=sum(1 for v in per_pembuat.values() if v == 0),
    )
