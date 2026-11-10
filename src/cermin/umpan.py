"""Sinyal keterlibatan, skema bobot umpan, dan penyusunan umpan.

Model sengaja sederhana. Sinyal awal (dilihat, suka, waktu tonton) dibuat
dari mutu laten kiriman dan jumlah pengikut pembuatnya. Dua hal itu
mencerminkan kenyataan yang masuk akal: kiriman bermutu lebih disukai, dan
pembuat dengan pengikut banyak mendapat lebih banyak penonton awal.
Umpan tidak pernah melihat mutu laten; ia hanya melihat sinyal.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass

from .data import Dataset, Kiriman, Pengguna

JUMLAH_UMPAN = 20  # kiriman yang tampil per pengguna
SUKA_PER_DILIHAT = 0.3  # peluang suka bila mutu = 1
SEMI_RUMUS_TONTON = (0.3, 0.6)  # porsi tonton = 0.3 + 0.6 * mutu


@dataclass(frozen=True)
class Sinyal:
    dilihat: int  # penonton awal
    suka: int
    tonton_detik: float  # total waktu tonton dari penonton awal


@dataclass(frozen=True)
class Konteks:
    ds: Dataset
    sinyal: dict[str, Sinyal]
    minat: dict[str, dict[str, float]]
    maks_suka: int
    maks_tonton: float
    seed: int


DASAR_BAWAAN = 1  # penonton awal minimum tiap kiriman
KOEF_BAWAAN = 0.5  # penonton awal tambahan per pengikut pembuat


def hitung_sinyal(
    ds: Dataset,
    seed: int | None = None,
    dasar: int = DASAR_BAWAAN,
    koef: float = KOEF_BAWAAN,
) -> dict[str, Sinyal]:
    """Sinyal awal tiap kiriman. Deterministik untuk seed yang sama.

    Penonton awal = ``dasar`` + ``koef`` x pengikut pembuat. ``koef = 0`` berarti
    semua kiriman mulai dengan penonton yang sama, apa pun pembuatnya.
    """
    rng = random.Random((ds.seed if seed is None else seed) + 1)
    pengikut = ds.pengikut()
    sinyal: dict[str, Sinyal] = {}
    for k in ds.kiriman:
        dilihat = dasar + round(koef * pengikut[k.pembuat_id])
        suka = sum(rng.random() < SUKA_PER_DILIHAT * k.mutu for _ in range(dilihat))
        porsi = SEMI_RUMUS_TONTON[0] + SEMI_RUMUS_TONTON[1] * k.mutu
        sinyal[k.id] = Sinyal(dilihat, suka, dilihat * porsi * k.durasi_detik)
    return sinyal


def buat_konteks(
    ds: Dataset,
    seed: int | None = None,
    dasar: int = DASAR_BAWAAN,
    koef: float = KOEF_BAWAAN,
) -> Konteks:
    sinyal = hitung_sinyal(ds, seed, dasar, koef)
    return Konteks(
        ds=ds,
        sinyal=sinyal,
        minat={u.id: u.minat for u in ds.pengguna},
        maks_suka=max(1, max(s.suka for s in sinyal.values())),
        maks_tonton=max(1.0, max(s.tonton_detik for s in sinyal.values())),
        seed=ds.seed if seed is None else seed,
    )


Skema = Callable[[Konteks, Pengguna, Kiriman], float]


def _kebaruan(k: Kiriman) -> float:
    return 1.0 - k.umur_jam / 72.0  # 1 = baru, 0 = paling lama


def skema_acak(c: Konteks, u: Pengguna, k: Kiriman) -> float:
    """Pembanding: urutan acak, tidak peduli apa pun."""
    return random.Random(f"{c.seed}|{u.id}|{k.id}").random()


def skema_kronologis(c: Konteks, u: Pengguna, k: Kiriman) -> float:
    return _kebaruan(k)


def skema_suka(c: Konteks, u: Pengguna, k: Kiriman) -> float:
    return float(c.sinyal[k.id].suka)


def skema_suka_rasio(c: Konteks, u: Pengguna, k: Kiriman) -> float:
    """Suka per penonton awal, dengan penghalus agar sampel kecil tidak melonjak."""
    s = c.sinyal[k.id]
    return (s.suka + 1) / (s.dilihat + 10)


def skema_waktu_tonton(c: Konteks, u: Pengguna, k: Kiriman) -> float:
    return c.sinyal[k.id].tonton_detik


def skema_kesamaan(c: Konteks, u: Pengguna, k: Kiriman) -> float:
    """Hanya kecocokan topik dengan minat pengguna."""
    return c.minat[u.id][k.topik]


def skema_campuran(c: Konteks, u: Pengguna, k: Kiriman) -> float:
    s = c.sinyal[k.id]
    return (
        0.4 * c.minat[u.id][k.topik] / 0.5  # minat tertinggi kira-kira 0.5
        + 0.3 * math.log1p(s.suka) / math.log1p(c.maks_suka)
        + 0.3 * _kebaruan(k)
    )


SKEMA: dict[str, Skema] = {
    "acak": skema_acak,
    "kronologis": skema_kronologis,
    "suka": skema_suka,
    "suka_rasio": skema_suka_rasio,
    "waktu_tonton": skema_waktu_tonton,
    "kesamaan": skema_kesamaan,
    "campuran": skema_campuran,
}


# Skema yang skornya tidak bergantung pada pengguna: urutan cukup dihitung sekali.
SKEMA_GLOBAL = frozenset({"kronologis", "suka", "suka_rasio", "waktu_tonton"})


def susun_umpan(
    c: Konteks, skema: str, jumlah: int = JUMLAH_UMPAN
) -> dict[str, list[str]]:
    """Untuk tiap pengguna, ``jumlah`` kiriman teratas menurut skema.

    Seri diputus dengan id kiriman supaya hasil selalu sama.
    """
    fungsi = SKEMA[skema]
    umpan: dict[str, list[str]] = {}
    if skema in SKEMA_GLOBAL:
        u0 = c.ds.pengguna[0]
        urut = sorted(c.ds.kiriman, key=lambda k: (-fungsi(c, u0, k), k.id))
        teratas = [k.id for k in urut[:jumlah]]
        return {u.id: list(teratas) for u in c.ds.pengguna}
    for u in c.ds.pengguna:
        berurut = sorted(
            c.ds.kiriman, key=lambda k: (-fungsi(c, u, k), k.id)
        )
        umpan[u.id] = [k.id for k in berurut[:jumlah]]
    return umpan
