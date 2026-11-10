"""Grafik perbandingan skema. Menulis berkas PNG; tidak menampilkan jendela."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .data import KELOMPOK, buat_dataset  # noqa: E402
from .metrik import Paparan  # noqa: E402
from .kepekaan import BERKAS_BUKTI, muat  # noqa: E402
from .simulasi import jalankan, jalankan_berulang  # noqa: E402
from .umpan import SKEMA  # noqa: E402

# Palet Okabe-Ito: dapat dibedakan oleh pembaca buta warna.
WARNA = {"besar": "#0072B2", "menengah": "#E69F00", "baru": "#009E73"}
WARNA_SKEMA = [
    "#000000", "#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7",
]


def grafik_porsi(hasil: dict[str, Paparan], berkas: Path) -> None:
    """Porsi tayangan tiap kelompok per skema, dengan patokan porsi kiriman."""
    skema = list(hasil)
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    lebar = 0.26
    for j, kelompok in enumerate(KELOMPOK):
        nilai = [hasil[s].porsi_tayangan[kelompok] * 100 for s in skema]
        posisi = [i + (j - 1) * lebar for i in range(len(skema))]
        ax.bar(posisi, nilai, lebar, label=kelompok, color=WARNA[kelompok])
        patokan = next(iter(hasil.values())).porsi_kiriman[kelompok] * 100
        ax.hlines(
            patokan, -0.5, len(skema) - 0.5, color=WARNA[kelompok],
            linestyles=":", linewidth=1,
        )
    ax.set_xticks(range(len(skema)), skema, rotation=20)
    ax.set_ylabel("porsi tayangan (%)")
    ax.set_title("Siapa kebagian tayangan, bila mutu kiriman setara\n"
                 "(garis putus-putus: porsi kiriman tiap kelompok)")
    ax.legend(title="kelompok pembuat", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    berkas.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(berkas)
    plt.close(fig)


def grafik_putaran(hasil: dict[str, list[Paparan]], berkas: Path) -> None:
    """Gini antarpembuat dari putaran ke putaran, satu garis per skema."""
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    for (skema, daftar), warna in zip(hasil.items(), WARNA_SKEMA):
        x = range(1, len(daftar) + 1)
        ax.plot(x, [p.gini_pembuat for p in daftar], marker="o", label=skema, color=warna)
    ax.set_xlabel("putaran umpan balik")
    ax.set_ylabel("indeks Gini tayangan antarpembuat")
    ax.set_ylim(0, 1)
    ax.set_xticks(range(1, len(next(iter(hasil.values()))) + 1))
    ax.set_title("Ketimpangan paparan dari putaran ke putaran")
    ax.legend(frameon=False, ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    berkas.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(berkas)
    plt.close(fig)


def grafik_kepekaan(sapuan: dict[str, dict[str, dict]], berkas: Path) -> None:
    """Porsi tayangan pembuat baru menurut koefisien penonton awal (dari docs/kepekaan.json)."""
    koefisien = sorted(sapuan, key=float)
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    for nama, warna in zip(SKEMA, WARNA_SKEMA):
        y = [sapuan[k][nama]["porsi_baru"]["rata"] * 100 for k in koefisien]
        ax.plot([float(k) for k in koefisien], y, marker="o", label=nama, color=warna)
    ax.set_xlabel("koefisien penonton awal per pengikut (0 = semua kiriman mulai sama)")
    ax.set_ylabel("porsi tayangan pembuat baru (%), rata-rata antarseed")
    ax.set_ylim(0, 45)
    ax.set_title("Ketimpangan skema hitungan mutlak bergantung pada keunggulan awal")
    ax.legend(frameon=False, ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    berkas.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(berkas)
    plt.close(fig)


def grafik_seed(seed_banyak: dict[str, dict], berkas: Path) -> None:
    """Rentang porsi tayangan pembuat baru pada banyak seed (dari docs/kepekaan.json)."""
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    for i, (nama, warna) in enumerate(zip(SKEMA, WARNA_SKEMA)):
        r = seed_banyak[nama]["porsi_baru"]
        ax.vlines(i, r["minimum"] * 100, r["maksimum"] * 100, color=warna, linewidth=3)
        ax.plot(i, r["rata"] * 100, "o", color=warna)
    ax.set_xticks(range(len(SKEMA)), list(SKEMA), rotation=20)
    ax.set_ylabel("porsi tayangan pembuat baru (%)")
    ax.set_title("Rentang pada 50 seed (titik: rata-rata, garis: terendah sampai tertinggi)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    berkas.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(berkas)
    plt.close(fig)


def main(keluaran: Path = Path("docs")) -> None:
    ds = buat_dataset()
    grafik_porsi(jalankan(ds), keluaran / "porsi-tayangan.png")
    grafik_putaran(jalankan_berulang(ds), keluaran / "gini-per-putaran.png")
    if BERKAS_BUKTI.exists():
        seed_banyak, sapuan = muat()
        grafik_kepekaan(sapuan, keluaran / "kepekaan-koefisien.png")
        grafik_seed(seed_banyak, keluaran / "rentang-seed.png")
    else:
        print(f"{BERKAS_BUKTI} belum ada; jalankan `python -m cermin.kepekaan` dulu untuk dua grafik lainnya")
    print(f"grafik ditulis ke {keluaran}/")


if __name__ == "__main__":
    main()
