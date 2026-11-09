from collections import Counter
from statistics import mean

import pytest

from cermin.data import (
    JUMLAH_PEMBUAT,
    KELOMPOK,
    TOPIK,
    buat_dataset,
    ringkasan,
)


@pytest.fixture(scope="module")
def ds():
    return buat_dataset(seed=2026)


def test_seed_sama_hasil_sama():
    a = buat_dataset(seed=7)
    b = buat_dataset(seed=7)
    assert a.kiriman == b.kiriman
    assert a.pengguna == b.pengguna
    assert a.mengikuti == b.mengikuti


def test_seed_berbeda_hasil_berbeda():
    assert buat_dataset(seed=1).kiriman != buat_dataset(seed=2).kiriman


def test_ukuran_bawaan(ds):
    assert len(ds.pengguna) == 200
    assert len(ds.kiriman) == 1000
    assert len(ds.pembuat) == sum(JUMLAH_PEMBUAT.values())


def test_ketiga_kelompok_ada(ds):
    hitung = Counter(p.kelompok for p in ds.pembuat)
    assert set(hitung) == set(KELOMPOK)
    per_id = ds.pembuat_menurut_id()
    kelompok_kiriman = {per_id[k.pembuat_id].kelompok for k in ds.kiriman}
    assert kelompok_kiriman == set(KELOMPOK)


def test_kiriman_merujuk_pembuat_yang_ada(ds):
    ids = {p.id for p in ds.pembuat}
    assert all(k.pembuat_id in ids for k in ds.kiriman)


def test_id_unik(ds):
    assert len({k.id for k in ds.kiriman}) == len(ds.kiriman)
    assert len({u.id for u in ds.pengguna}) == len(ds.pengguna)


def test_nilai_dalam_rentang(ds):
    for k in ds.kiriman:
        assert k.topik in TOPIK
        assert 0.0 <= k.umur_jam <= 72.0
        assert 15 <= k.durasi_detik <= 180
        assert 0.0 <= k.mutu <= 1.0


def test_minat_pengguna_berjumlah_satu(ds):
    for u in ds.pengguna:
        assert set(u.minat) == set(TOPIK)
        assert sum(u.minat.values()) == pytest.approx(1.0)


def test_pembuat_besar_lebih_banyak_pengikut(ds):
    pengikut = ds.pengikut()

    def rerata(kelompok):
        return mean(pengikut[p.id] for p in ds.pembuat if p.kelompok == kelompok)

    assert rerata("besar") > rerata("menengah") > rerata("baru")


def test_mutu_tidak_bergantung_kelompok(ds):
    # Rancangan sengaja: mutu laten disebar sama untuk semua kelompok,
    # jadi rerata per kelompok harus berdekatan (beta(2,2), rerata 0.5).
    per_id = ds.pembuat_menurut_id()
    for kelompok in KELOMPOK:
        mutu = [k.mutu for k in ds.kiriman if per_id[k.pembuat_id].kelompok == kelompok]
        assert mean(mutu) == pytest.approx(0.5, abs=0.05)


def test_jumlah_tidak_valid_ditolak():
    with pytest.raises(ValueError):
        buat_dataset(jumlah_pengguna=0)


def test_ringkasan_memuat_semua_kelompok(ds):
    teks = ringkasan(ds)
    for kelompok in KELOMPOK:
        assert kelompok in teks
