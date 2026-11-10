"""Jalankan semua skema pada dataset yang sama dan bandingkan paparannya."""

from __future__ import annotations

import random
from dataclasses import replace

from .data import KELOMPOK, Dataset, buat_dataset
from .metrik import Paparan, ukur
from .umpan import (
    DASAR_BAWAAN,
    KOEF_BAWAAN,
    SEMI_RUMUS_TONTON,
    SKEMA,
    SUKA_PER_DILIHAT,
    Konteks,
    Sinyal,
    buat_konteks,
    susun_umpan,
)

PUTARAN_BAWAAN = 5


def jalankan(
    ds: Dataset, dasar: int = DASAR_BAWAAN, koef: float = KOEF_BAWAAN
) -> dict[str, Paparan]:
    konteks = buat_konteks(ds, dasar=dasar, koef=koef)
    return {nama: ukur(ds, susun_umpan(konteks, nama)) for nama in SKEMA}


def perbarui_sinyal(
    c: Konteks, umpan: dict[str, list[str]], rng: random.Random
) -> Konteks:
    """Tiap tayangan menambah penonton, dan dengan peluang tertentu suka dan waktu tonton.

    Peluang suka dan porsi tonton sama dengan di sinyal awal: bergantung pada
    mutu laten saja, tidak pada kelompok pembuat.
    """
    per_id = {k.id: k for k in c.ds.kiriman}
    dilihat = {i: s.dilihat for i, s in c.sinyal.items()}
    suka = {i: s.suka for i, s in c.sinyal.items()}
    tonton = {i: s.tonton_detik for i, s in c.sinyal.items()}
    for u in c.ds.pengguna:  # urutan tetap supaya hasil deterministik
        for id_kiriman in umpan[u.id]:
            k = per_id[id_kiriman]
            dilihat[id_kiriman] += 1
            if rng.random() < SUKA_PER_DILIHAT * k.mutu:
                suka[id_kiriman] += 1
            tonton[id_kiriman] += (
                SEMI_RUMUS_TONTON[0] + SEMI_RUMUS_TONTON[1] * k.mutu
            ) * k.durasi_detik
    sinyal = {i: Sinyal(dilihat[i], suka[i], tonton[i]) for i in dilihat}
    return replace(
        c,
        sinyal=sinyal,
        maks_suka=max(1, max(s.suka for s in sinyal.values())),
        maks_tonton=max(1.0, max(s.tonton_detik for s in sinyal.values())),
    )


def jalankan_berulang(
    ds: Dataset, putaran: int = PUTARAN_BAWAAN
) -> dict[str, list[Paparan]]:
    """Ulangi: susun umpan, ukur paparan, lalu perbarui sinyal dari tayangan itu.

    Putaran pertama sama dengan ``jalankan``. Mengembalikan paparan tiap putaran.
    """
    if putaran < 1:
        raise ValueError("putaran minimal 1")
    awal = buat_konteks(ds)
    hasil: dict[str, list[Paparan]] = {}
    for nama in SKEMA:
        c = awal
        rng = random.Random(f"{ds.seed}|umpan-balik|{nama}")
        daftar: list[Paparan] = []
        for _ in range(putaran):
            umpan = susun_umpan(c, nama)
            daftar.append(ukur(ds, umpan))
            c = perbarui_sinyal(c, umpan, rng)
        hasil[nama] = daftar
    return hasil


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
