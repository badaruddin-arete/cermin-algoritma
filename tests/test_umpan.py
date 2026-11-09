import pytest

from cermin.data import buat_dataset
from cermin.simulasi import jalankan, tabel
from cermin.umpan import (
    JUMLAH_UMPAN,
    SKEMA,
    buat_konteks,
    hitung_sinyal,
    susun_umpan,
)


@pytest.fixture(scope="module")
def ds():
    return buat_dataset(seed=2026)


@pytest.fixture(scope="module")
def konteks(ds):
    return buat_konteks(ds)


@pytest.fixture(scope="module")
def hasil(ds):
    return jalankan(ds)


def test_sinyal_deterministik(ds):
    assert hitung_sinyal(ds) == hitung_sinyal(ds)


def test_sinyal_masuk_akal(ds):
    for s in hitung_sinyal(ds).values():
        assert s.dilihat >= 1
        assert 0 <= s.suka <= s.dilihat
        assert s.tonton_detik > 0


@pytest.mark.parametrize("nama", list(SKEMA))
def test_umpan_berukuran_tetap_tanpa_duplikat(konteks, nama):
    umpan = susun_umpan(konteks, nama)
    assert len(umpan) == len(konteks.ds.pengguna)
    for daftar in umpan.values():
        assert len(daftar) == JUMLAH_UMPAN
        assert len(set(daftar)) == JUMLAH_UMPAN


@pytest.mark.parametrize("nama", list(SKEMA))
def test_umpan_deterministik(konteks, nama):
    assert susun_umpan(konteks, nama) == susun_umpan(konteks, nama)


def test_kronologis_menaruh_yang_terbaru_dulu(konteks):
    umpan = susun_umpan(konteks, "kronologis")
    umur = {k.id: k.umur_jam for k in konteks.ds.kiriman}
    daftar = next(iter(umpan.values()))
    umur_daftar = [umur[i] for i in daftar]
    assert umur_daftar == sorted(umur_daftar)


def test_kesamaan_menaruh_topik_favorit(konteks):
    umpan = susun_umpan(konteks, "kesamaan")
    topik = {k.id: k.topik for k in konteks.ds.kiriman}
    u = konteks.ds.pengguna[0]
    favorit = sorted(u.minat, key=u.minat.get, reverse=True)[:2]
    assert all(topik[i] in favorit for i in umpan[u.id][:5])


def test_skema_global_memberi_umpan_sama_untuk_semua(konteks):
    umpan = susun_umpan(konteks, "suka")
    assert len({tuple(v) for v in umpan.values()}) == 1


def test_acak_mendekati_porsi_kiriman(hasil):
    p = hasil["acak"]
    for kelompok, porsi in p.porsi_kiriman.items():
        assert p.porsi_tayangan[kelompok] == pytest.approx(porsi, abs=0.05)


def test_acak_paling_merata(hasil):
    assert hasil["acak"].gini_pembuat == min(p.gini_pembuat for p in hasil.values())


def test_suka_mutlak_lebih_timpang_dari_suka_per_penonton(hasil):
    # Perbandingan inti: skema yang sama-sama "berbasis suka", beda cara menghitung.
    assert hasil["suka"].gini_pembuat > hasil["suka_rasio"].gini_pembuat
    assert hasil["suka"].porsi_tayangan["besar"] > hasil["suka_rasio"].porsi_tayangan["besar"]


def test_tabel_memuat_semua_skema(hasil):
    teks = tabel(hasil)
    for nama in SKEMA:
        assert nama in teks


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_temuan_suka_mutlak_bertahan_di_seed_lain(seed):
    h = jalankan(buat_dataset(seed=seed))
    assert h["suka"].gini_pembuat > h["suka_rasio"].gini_pembuat
    for skema in ("suka", "waktu_tonton"):
        assert h[skema].porsi_tayangan["baru"] == 0.0
