"""Grafik perbandingan skema. Menulis berkas PNG; tidak menampilkan jendela."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .data import KELOMPOK, buat_dataset  # noqa: E402
from .metrik import Paparan  # noqa: E402
from .simulasi import jalankan, jalankan_berulang  # noqa: E402

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


def main(keluaran: Path = Path("docs")) -> None:
    ds = buat_dataset()
    grafik_porsi(jalankan(ds), keluaran / "porsi-tayangan.png")
    grafik_putaran(jalankan_berulang(ds), keluaran / "gini-per-putaran.png")
    print(f"grafik ditulis ke {keluaran}/")


if __name__ == "__main__":
    main()
