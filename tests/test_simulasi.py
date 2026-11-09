import pytest

from cermin.data import buat_dataset
from cermin.grafik import grafik_porsi, grafik_putaran
from cermin.simulasi import jalankan, jalankan_berulang, perbarui_sinyal
from cermin.umpan import SKEMA, buat_konteks, susun_umpan
import random


@pytest.fixture(scope="module")
def kecil():
    return buat_dataset(seed=5, jumlah_pengguna=40, jumlah_kiriman=200)


@pytest.fixture(scope="module")
def berulang(kecil):
    return jalankan_berulang(kecil, putaran=3)


def test_putaran_pertama_sama_dengan_jalankan(kecil, berulang):
    statis = jalankan(kecil)
    for nama in SKEMA:
        assert berulang[nama][0] == statis[nama]


def test_jumlah_putaran(berulang):
    assert all(len(v) == 3 for v in berulang.values())


def test_deterministik(kecil, berulang):
    assert jalankan_berulang(kecil, putaran=3) == berulang


def test_putaran_tidak_valid_ditolak(kecil):
    with pytest.raises(ValueError):
        jalankan_berulang(kecil, putaran=0)


def test_perbarui_sinyal_menambah_penonton_sebanyak_tayangan(kecil):
    c = buat_konteks(kecil)
    umpan = susun_umpan(c, "acak")
    baru = perbarui_sinyal(c, umpan, random.Random(0))
    tambahan = sum(baru.sinyal[i].dilihat - c.sinyal[i].dilihat for i in c.sinyal)
    assert tambahan == sum(len(v) for v in umpan.values())
    assert all(baru.sinyal[i].suka >= c.sinyal[i].suka for i in c.sinyal)
    assert all(baru.sinyal[i].tonton_detik >= c.sinyal[i].tonton_detik for i in c.sinyal)


def test_skema_tanpa_sinyal_tidak_berubah_antarputaran(berulang):
    # acak, kronologis, dan kesamaan tidak memakai sinyal keterlibatan.
    for nama in ("acak", "kronologis", "kesamaan"):
        assert len({p.gini_pembuat for p in berulang[nama]}) == 1


def test_grafik_menulis_berkas(tmp_path, kecil, berulang):
    a, b = tmp_path / "a.png", tmp_path / "sub" / "b.png"
    grafik_porsi(jalankan(kecil), a)
    grafik_putaran(berulang, b)
    for f in (a, b):
        assert f.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
