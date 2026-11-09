"""Generator data fiktif untuk platform rekaan "Warung Kabar".

Semua angka di sini dibuat-buat. Tujuannya memperlihatkan mekanisme,
bukan meniru platform nyata mana pun.

Keputusan penting: mutu kiriman (``mutu``) diambil dari sebaran yang
sama untuk ketiga kelompok pembuat. Jadi bila nanti satu kelompok
mendapat paparan jauh lebih besar, sebabnya bukan karena kirimannya
lebih bagus, melainkan karena cara umpan menimbang sinyal.
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field

TOPIK: tuple[str, ...] = (
    "berita",
    "olahraga",
    "kuliner",
    "musik",
    "pendidikan",
    "humor",
)

KELOMPOK: tuple[str, ...] = ("besar", "menengah", "baru")

# Jumlah pembuat per kelompok.
JUMLAH_PEMBUAT: dict[str, int] = {"besar": 5, "menengah": 15, "baru": 20}

# Peluang seorang pengguna mengikuti satu pembuat dari kelompok ini.
PELUANG_DIIKUTI: dict[str, float] = {"besar": 0.40, "menengah": 0.10, "baru": 0.02}

# Bobot keaktifan: seberapa sering kelompok ini mengirim, relatif.
BOBOT_AKTIF: dict[str, float] = {"besar": 3.0, "menengah": 2.0, "baru": 1.0}

UMUR_MAKS_JAM = 72.0
DURASI_MIN_DETIK = 15
DURASI_MAKS_DETIK = 180


@dataclass(frozen=True)
class Pengguna:
    id: str
    minat: dict[str, float]  # bobot per topik, jumlahnya 1


@dataclass(frozen=True)
class Pembuat:
    id: str
    kelompok: str
    topik_utama: str


@dataclass(frozen=True)
class Kiriman:
    id: str
    pembuat_id: str
    topik: str
    umur_jam: float  # sejak diunggah, 0 = baru saja
    durasi_detik: int
    mutu: float  # mutu laten 0..1, tidak terlihat oleh umpan


@dataclass
class Dataset:
    seed: int
    pengguna: list[Pengguna]
    pembuat: list[Pembuat]
    kiriman: list[Kiriman]
    mengikuti: dict[str, set[str]] = field(default_factory=dict)  # pengguna -> pembuat

    def pembuat_menurut_id(self) -> dict[str, Pembuat]:
        return {p.id: p for p in self.pembuat}

    def pengikut(self) -> Counter[str]:
        """Jumlah pengikut tiap pembuat."""
        hitung: Counter[str] = Counter({p.id: 0 for p in self.pembuat})
        for diikuti in self.mengikuti.values():
            hitung.update(diikuti)
        return hitung


def _minat_acak(rng: random.Random) -> dict[str, float]:
    # Dua topik favorit diberi bobot lebih, sisanya kecil.
    mentah = {t: rng.random() * 0.2 for t in TOPIK}
    for t in rng.sample(TOPIK, 2):
        mentah[t] += 1.0
    total = sum(mentah.values())
    return {t: v / total for t, v in mentah.items()}


def buat_dataset(
    seed: int = 2026,
    jumlah_pengguna: int = 200,
    jumlah_kiriman: int = 1000,
) -> Dataset:
    """Bangun dataset fiktif yang sama persis untuk seed yang sama."""
    if jumlah_pengguna < 1 or jumlah_kiriman < 1:
        raise ValueError("jumlah pengguna dan kiriman harus positif")

    rng = random.Random(seed)

    pembuat: list[Pembuat] = []
    for kelompok in KELOMPOK:
        for i in range(JUMLAH_PEMBUAT[kelompok]):
            pembuat.append(
                Pembuat(
                    id=f"{kelompok}-{i + 1:02d}",
                    kelompok=kelompok,
                    topik_utama=rng.choice(TOPIK),
                )
            )

    pengguna = [
        Pengguna(id=f"u{i + 1:03d}", minat=_minat_acak(rng))
        for i in range(jumlah_pengguna)
    ]

    mengikuti: dict[str, set[str]] = {}
    for u in pengguna:
        mengikuti[u.id] = {
            p.id for p in pembuat if rng.random() < PELUANG_DIIKUTI[p.kelompok]
        }

    bobot = [BOBOT_AKTIF[p.kelompok] for p in pembuat]
    kiriman: list[Kiriman] = []
    for i in range(jumlah_kiriman):
        p = rng.choices(pembuat, weights=bobot, k=1)[0]
        # 70% kiriman sesuai topik utama pembuat, sisanya acak.
        topik = p.topik_utama if rng.random() < 0.7 else rng.choice(TOPIK)
        kiriman.append(
            Kiriman(
                id=f"k{i + 1:04d}",
                pembuat_id=p.id,
                topik=topik,
                umur_jam=round(rng.uniform(0.0, UMUR_MAKS_JAM), 2),
                durasi_detik=rng.randint(DURASI_MIN_DETIK, DURASI_MAKS_DETIK),
                mutu=round(rng.betavariate(2.0, 2.0), 4),
            )
        )

    return Dataset(
        seed=seed,
        pengguna=pengguna,
        pembuat=pembuat,
        kiriman=kiriman,
        mengikuti=mengikuti,
    )


def ringkasan(ds: Dataset) -> str:
    """Ringkasan singkat yang bisa dibaca manusia."""
    per_id = ds.pembuat_menurut_id()
    kiriman_per_kelompok = Counter(per_id[k.pembuat_id].kelompok for k in ds.kiriman)
    pengikut = ds.pengikut()
    baris = [
        f"Warung Kabar (fiktif), seed {ds.seed}",
        f"  pengguna: {len(ds.pengguna)}, pembuat: {len(ds.pembuat)}, kiriman: {len(ds.kiriman)}",
    ]
    for kelompok in KELOMPOK:
        anggota = [p.id for p in ds.pembuat if p.kelompok == kelompok]
        rerata_pengikut = sum(pengikut[a] for a in anggota) / len(anggota)
        baris.append(
            f"  {kelompok:<9} pembuat {len(anggota):>2}, "
            f"kiriman {kiriman_per_kelompok[kelompok]:>4}, "
            f"rerata pengikut {rerata_pengikut:5.1f}"
        )
    return "\n".join(baris)


if __name__ == "__main__":
    print(ringkasan(buat_dataset()))
