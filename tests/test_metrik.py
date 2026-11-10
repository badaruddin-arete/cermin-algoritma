import pytest

from cermin.data import buat_dataset
import math

from cermin.metrik import gini, tayangan_berbobot_per_pembuat, tayangan_per_pembuat, ukur


def test_gini_sama_rata_nol():
    assert gini([5, 5, 5, 5]) == pytest.approx(0.0)


def test_gini_satu_pihak_memegang_semua():
    # nilai maksimum untuk n pihak adalah (n - 1) / n
    assert gini([0, 0, 0, 10]) == pytest.approx(3 / 4)


def test_gini_contoh_hitungan_tangan():
    # [1, 2, 3]: urut 1,2,3; sum(i*v)=1+4+9=14; 2*14/(3*6) - 4/3 = 28/18 - 24/18
    assert gini([1, 2, 3]) == pytest.approx(4 / 18)


def test_gini_tidak_peduli_urutan():
    assert gini([3, 1, 2]) == pytest.approx(gini([1, 2, 3]))


def test_gini_semua_nol_dianggap_nol():
    assert gini([0, 0, 0]) == 0.0


def test_gini_menolak_masukan_buruk():
    with pytest.raises(ValueError):
        gini([])
    with pytest.raises(ValueError):
        gini([1, -1])


def test_tayangan_dihitung_dan_nol_ikut_tercatat():
    ds = buat_dataset(seed=3, jumlah_pengguna=4, jumlah_kiriman=50)
    k0, k1 = ds.kiriman[0], ds.kiriman[1]
    umpan = {"a": [k0.id, k1.id], "b": [k0.id]}
    hitung = tayangan_per_pembuat(ds, umpan)
    assert sum(hitung.values()) == 3
    assert set(hitung) == {p.id for p in ds.pembuat}
    assert hitung[k0.pembuat_id] >= 2


def test_ukur_porsi_berjumlah_satu():
    ds = buat_dataset(seed=3, jumlah_pengguna=10, jumlah_kiriman=100)
    umpan = {u.id: [k.id for k in ds.kiriman[:5]] for u in ds.pengguna}
    p = ukur(ds, umpan)
    assert sum(p.porsi_tayangan.values()) == pytest.approx(1.0)
    assert sum(p.porsi_kiriman.values()) == pytest.approx(1.0)
    assert 0.0 <= p.gini_pembuat < 1.0


def test_bobot_posisi_menurun():
    ds = buat_dataset(seed=3, jumlah_pengguna=2, jumlah_kiriman=30)
    a, b = ds.kiriman[0], ds.kiriman[1]
    hitung = tayangan_berbobot_per_pembuat(ds, {"u": [a.id, b.id]})
    if a.pembuat_id == b.pembuat_id:
        assert hitung[a.pembuat_id] == pytest.approx(1.0 + 1 / math.log2(3))
    else:
        assert hitung[a.pembuat_id] == pytest.approx(1.0)
        assert hitung[b.pembuat_id] == pytest.approx(1 / math.log2(3))
        assert hitung[a.pembuat_id] > hitung[b.pembuat_id]


def test_porsi_berbobot_berjumlah_satu():
    ds = buat_dataset(seed=3, jumlah_pengguna=10, jumlah_kiriman=100)
    umpan = {u.id: [k.id for k in ds.kiriman[:5]] for u in ds.pengguna}
    assert sum(ukur(ds, umpan).porsi_berbobot.values()) == pytest.approx(1.0)
