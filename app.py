# app.py
import csv
import time
from backend.m1_pesanan import Array, LinkList, Pesanan
from frontend.ui import AppUI

def muat_csv(filepath):
    larik = Array()
    rantai = LinkList()
    
    print(f"Membaca data '{filepath}' (200.000 baris)...")
    t0 = time.perf_counter()
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row:
                continue
            p = Pesanan(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            larik.tambah_reguler(p)
            rantai.tambah_reguler(p)
    print(f"Selesai! {larik.jumlah:,} data siap dioperasikan dalam {time.perf_counter() - t0:.2f} detik.")
    print("Membuka jendela aplikasi...")
    return larik, rantai

if __name__ == "__main__":
    larik, rantai = muat_csv("data/pesanan.csv")
    app = AppUI(larik, rantai)
    app.mainloop()