# app.py
import csv
import time
from backend.m1_pesanan import Array, LinkList, Pesanan


def muat_csv(filepath):
    larik = Array()
    rantai = LinkList()

    print(f"Membaca '{filepath}' (200.000 baris)... Harap tunggu sebentar.")
    t0 = time.perf_counter()

    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # lewatin header
        for baris in reader:
            if not baris:
                continue
            # urutan kolom di csv: oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status
            p = Pesanan(
                baris[0], baris[1], baris[2], baris[3],
                baris[4], baris[5], baris[6], baris[7], baris[8]
            )
            larik.tambah_reguler(p)
            rantai.tambah_reguler(p)

    durasi = time.perf_counter() - t0
    print(f"Berhasil memuat {larik.jumlah:,} data dalam {durasi:.2f} detik!\n")
    return larik, rantai


if __name__ == "__main__":
    # muat dataset dulu
    larik, rantai = muat_csv("data/pesanan.csv")

    # data dummy buat ngetes insert vip/prioritas/reguler
    dummy_vip = Pesanan("O-999991", "Pelanggan VIP", "kafe-teknik", "kopi", "15000", "1", "1000", "", "ANTRE")
    dummy_prio = Pesanan("O-999992", "Pelanggan Prioritas", "warung-bu-ida", "mie", "13000", "2", "1001", "", "ANTRE")
    dummy_reg = Pesanan("O-999993", "Pelanggan Reguler", "bakso-pak-yon", "bakso", "10000", "3", "1002", "", "ANTRE")

    print("=" * 65)
    print("BENCHMARK MILESTONE 1 (ARRAY vs LINKED LIST)")
    print("=" * 65)

    # tambah VIP -> masuk paling depan, ini yg biasanya paling keliatan bedanya
    t0 = time.perf_counter()
    larik.tambah_vip(dummy_vip)
    t_larik_vip = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    rantai.tambah_vip(dummy_vip)
    t_rantai_vip = (time.perf_counter() - t0) * 1000
    print(f"Tambah VIP (Depan)       | Array: {t_larik_vip:6.2f} ms | Linked List: {t_rantai_vip:6.2f} ms")

    # tambah prioritas -> nyelip di tengah antrian
    t0 = time.perf_counter()
    larik.tambah_prioritas(dummy_prio)
    t_larik_prio = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    rantai.tambah_prioritas(dummy_prio)
    t_rantai_prio = (time.perf_counter() - t0) * 1000
    print(f"Tambah PRIORITAS (Tengah)| Array: {t_larik_prio:6.2f} ms | Linked List: {t_rantai_prio:6.2f} ms")

    # tambah reguler -> paling belakang, harusnya sama2 cepet di kedua struktur
    t0 = time.perf_counter()
    larik.tambah_reguler(dummy_reg)
    t_larik_reg = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    rantai.tambah_reguler(dummy_reg)
    t_rantai_reg = (time.perf_counter() - t0) * 1000
    print(f"Tambah REGULER (Belakang)| Array: {t_larik_reg:6.2f} ms | Linked List: {t_rantai_reg:6.2f} ms")

    # nah ini yg paling nunjukin bedanya array vs linked list
    # array tinggal loncat ke indeks, linked list kudu jalan satu2 dari head
    t0 = time.perf_counter()
    _ = larik.get(100000)
    t_larik_get = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    _ = rantai.get(100000)
    t_rantai_get = (time.perf_counter() - t0) * 1000
    print(f"Lihat Pesanan ke-100.000 | Array: {t_larik_get:6.2f} ms | Linked List: {t_rantai_get:6.2f} ms")
    print("=" * 65)

