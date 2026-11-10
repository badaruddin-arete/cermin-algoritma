import pytest

from cermin.grafik import grafik_kepekaan, grafik_seed
from cermin.kepekaan import banyak_seed, muat, sapu_koefisien, simpan
from cermin.umpan import SKEMA

UKURAN = {"jumlah_pengguna": 60, "jumlah_kiriman": 300}


@pytest.fixture(scope="module")
def seed_kecil():
    return banyak_seed((1, 2, 3), **UKURAN)


@pytest.fixture(scope="module")
def sapuan_kecil():
    return sapu_koefisien((0.0, 1.0), (1, 2, 3), dasar=20, **UKURAN)


def test_rentang_berurutan(seed_kecil):
    assert set(seed_kecil) == set(SKEMA)
    for r in seed_kecil.values():
        for rentang in (r.porsi_baru, r.porsi_besar, r.gini):
            assert rentang.minimum <= rentang.rata <= rentang.maksimum


def test_seed_kosong_ditolak():
    with pytest.raises(ValueError):
        banyak_seed(())


def test_keunggulan_awal_menentukan_ketimpangan_suka_mutlak(sapuan_kecil):
    # Temuan penting: bila semua kiriman mulai dengan penonton yang sama,
    # suka mutlak hampir tidak menjepit pembuat baru; bila penonton awal
    # mengikuti pengikut, pembuat baru tersingkir.
    sama = sapuan_kecil[0.0]["suka"].porsi_baru.rata
    timpang = sapuan_kecil[1.0]["suka"].porsi_baru.rata
    assert timpang < sama
    assert timpang < 0.05


def test_skema_tanpa_sinyal_tidak_terpengaruh_koefisien(sapuan_kecil):
    for nama in ("acak", "kronologis", "kesamaan"):
        a = sapuan_kecil[0.0][nama].porsi_baru.rata
        b = sapuan_kecil[1.0][nama].porsi_baru.rata
        assert a == pytest.approx(b)


def test_simpan_dan_muat_dan_grafik(tmp_path, seed_kecil, sapuan_kecil):
    berkas = tmp_path / "bukti" / "kepekaan.json"
    simpan(seed_kecil, sapuan_kecil, berkas)
    seed_json, sapuan_json = muat(berkas)
    assert seed_json["suka"]["porsi_baru"]["rata"] == pytest.approx(
        seed_kecil["suka"].porsi_baru.rata
    )
    assert set(sapuan_json) == {"0.0", "1.0"}
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    grafik_kepekaan(sapuan_json, a)
    grafik_seed(seed_json, b)
    for f in (a, b):
        assert f.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
