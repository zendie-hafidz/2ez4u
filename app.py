import csv
import time

from backend.m1_pesanan import Array, LinkList, Pesanan
from backend.m2_antrean import AntreanMelingkar, Tumpukan
from frontend.ui import AppUI

JUMLAH_ANTREAN_AWAL = 25


def muat_csv(filepath):
    larik = Array()
    rantai = LinkList()
    antrean = AntreanMelingkar(kapasitas=50000)
    undo_stack = Tumpukan()

    print(f"Membaca data '{filepath}' (200.000 baris)...")
    t0 = time.perf_counter()

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # lewati baris header

        for row in reader:
            if not row:
                continue  # baris kosong

            p = Pesanan(row[0], row[1], row[2], row[3], row[4],
                        row[5], row[6], row[7], row[8])
            larik.tambah_reguler(p)
            rantai.tambah_reguler(p)

            # 25 pesanan pertama juga dimasukin ke antrean, buat bahan demo M2
            if antrean.jumlah < JUMLAH_ANTREAN_AWAL:
                antrean.enqueue(p)

    durasi = time.perf_counter() - t0
    print(f"Selesai! {larik.jumlah:,} data siap dalam {durasi:.2f} detik.")
    print("Membuka jendela aplikasi...\n")
    return larik, rantai, antrean, undo_stack


if __name__ == "__main__":
    larik, rantai, antrean, undo_stack = muat_csv("data/pesanan.csv")
    app = AppUI(larik, rantai, antrean, undo_stack)
    app.mainloop()