# frontend/ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
from backend.m1_pesanan import Pesanan
from backend.m3_laporan import insertion_sort, merge_sort, linear_search, binary_search
from backend.m4_pencarian import PetaHash


def format_detik(detik):
    if not detik or detik == "-":
        return "-"
    try:
        d = int(detik)
    except ValueError:
        return str(detik)
    jam = (d // 3600) % 24
    menit = (d % 3600) // 60
    det = d % 60
    return f"{jam:02d}:{menit:02d}:{det:02d}"


class AppUI(tk.Tk):
    def __init__(self, larik, rantai, antrean, undo_stack):
        super().__init__()
        self.title("2EZ4U Food Delivery - Engine Benchmark")
        self.geometry("1040x740")
        self.minsize(900, 620)

        self.larik = larik
        self.rantai = rantai
        self.antrean = antrean
        self.undo_stack = undo_stack

        # simpanan hasil M3 dan M4 biar tidak dibangun ulang terus
        self.cache_urut_oid = None
        self.waktu_bangun_mrg_ms = 0.0
        self.peta_hash = None
        self.waktu_bangun_hash_ms = 0.0

        self.buat_layout()

    def buat_layout(self):
        # panel bawah: log waktu
        self.frame_bottom = tk.LabelFrame(self, text="COMMAND & TIMER LOG", padx=10, pady=5)
        self.frame_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.lbl_log = tk.Label(self.frame_bottom, text="Status: Siap melayani perintah.",
                                anchor="w", font=("Consolas", 10, "bold"), fg="#1a5fb4")
        self.lbl_log.pack(fill=tk.X)

        # panel kiri: menu M1 sampai M4
        self.frame_left = tk.Frame(self, width=280, padx=5, pady=5)
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        self.frame_left.pack_propagate(False)

        # M1
        box_m1 = tk.LabelFrame(self.frame_left, text="M1 - DATA PESANAN", padx=5, pady=3)
        box_m1.pack(fill=tk.X, pady=(0, 4))

        tk.Label(box_m1, text="[ ARRAY ]", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        ttk.Button(box_m1, text="ARRAY - LIHAT PESANAN", command=self.cmd_array_get).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="ARRAY - TAMBAH REGULER", command=lambda: self.cmd_tambah("array", 3)).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="ARRAY - TAMBAH PRIORITAS", command=lambda: self.cmd_tambah("array", 2)).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="ARRAY - TAMBAH VIP", command=lambda: self.cmd_tambah("array", 1)).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="ARRAY - HAPUS PESANAN", command=lambda: self.cmd_hapus("array")).pack(fill=tk.X, pady=1)

        tk.Label(box_m1, text="[ LINKED LIST ]", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(3, 0))
        ttk.Button(box_m1, text="LINKEDLIST - LIHAT PESANAN", command=self.cmd_ll_get).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="LINKEDLIST - TAMBAH REGULER", command=lambda: self.cmd_tambah("ll", 3)).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="LINKEDLIST - TAMBAH PRIORITAS", command=lambda: self.cmd_tambah("ll", 2)).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="LINKEDLIST - TAMBAH VIP", command=lambda: self.cmd_tambah("ll", 1)).pack(fill=tk.X, pady=1)
        ttk.Button(box_m1, text="LINKEDLIST - HAPUS PESANAN", command=lambda: self.cmd_hapus("ll")).pack(fill=tk.X, pady=1)

        # M2
        box_m2 = tk.LabelFrame(self.frame_left, text="M2 - ANTREAN & UNDO", padx=5, pady=3)
        box_m2.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(box_m2, text="ISI ANTREAN (FIFO)", command=self.cmd_enqueue).pack(fill=tk.X, pady=1)
        ttk.Button(box_m2, text="LAYANI BERIKUTNYA", command=self.cmd_layani).pack(fill=tk.X, pady=1)
        ttk.Button(box_m2, text="BATALKAN / UNDO", command=self.cmd_undo).pack(fill=tk.X, pady=1)

        # M3
        box_m3 = tk.LabelFrame(self.frame_left, text="M3 - SORT DAN SEARCH", padx=5, pady=3)
        box_m3.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(box_m3, text="SORT - INSERTION SORT", command=self.cmd_insertion_sort).pack(fill=tk.X, pady=1)
        ttk.Button(box_m3, text="SORT - MERGE SORT", command=self.cmd_merge_sort).pack(fill=tk.X, pady=1)
        ttk.Button(box_m3, text="SEARCH - LINEAR SEARCH", command=self.cmd_linear_search).pack(fill=tk.X, pady=1)
        ttk.Button(box_m3, text="SEARCH - BINARY SEARCH", command=self.cmd_binary_search).pack(fill=tk.X, pady=1)

        # M4
        box_m4 = tk.LabelFrame(self.frame_left, text="M4 - HASH TABLE", padx=5, pady=3)
        box_m4.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(box_m4, text="BANGUN INDEKS HASH", command=self.cmd_bangun_hash).pack(fill=tk.X, pady=1)
        ttk.Button(box_m4, text="CARI PESANAN (HASH)", command=self.cmd_hash_search).pack(fill=tk.X, pady=1)

        # panel kanan: form dan output
        self.frame_right = tk.Frame(self, padx=10, pady=5)
        self.frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        form_box = tk.LabelFrame(self.frame_right, text="Form Parameter", padx=10, pady=6)
        form_box.pack(fill=tk.X, pady=(0, 6))

        tk.Label(form_box, text="Indeks / Posisi:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_idx = ttk.Entry(form_box, width=12)
        self.entry_idx.insert(0, "0")
        self.entry_idx.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Target OID:").grid(row=0, column=2, sticky="w", padx=(15, 2), pady=2)
        self.entry_oid = ttk.Entry(form_box, width=15)
        self.entry_oid.insert(0, "O-137442")
        self.entry_oid.grid(row=0, column=3, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Jumlah Baris Sort:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_n_sort = ttk.Entry(form_box, width=12)
        self.entry_n_sort.insert(0, "10")
        self.entry_n_sort.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Kunci Sort:").grid(row=1, column=2, sticky="w", padx=(15, 2), pady=2)
        self.combo_kunci = ttk.Combobox(form_box, values=["harga", "oid", "selesai"], width=13, state="readonly")
        self.combo_kunci.current(0)
        self.combo_kunci.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Nama Pelanggan:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_nama = ttk.Entry(form_box, width=22)
        self.entry_nama.insert(0, "Pelanggan Baru")
        self.entry_nama.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Resto & Menu:").grid(row=2, column=2, sticky="w", padx=(15, 2), pady=2)
        self.entry_menu = ttk.Entry(form_box, width=22)
        self.entry_menu.insert(0, "kafe-teknik / kopi")
        self.entry_menu.grid(row=2, column=3, sticky="w", padx=5, pady=2)

        # layar output
        out_box = tk.LabelFrame(self.frame_right, text="Hasil Pemeriksaan & Detail Objek", padx=10, pady=5)
        out_box.pack(fill=tk.BOTH, expand=True)

        self.txt_output = tk.Text(out_box, wrap=tk.NONE, font=("Consolas", 9))
        scroll_y = ttk.Scrollbar(out_box, orient=tk.VERTICAL, command=self.txt_output.yview)
        scroll_x = ttk.Scrollbar(out_box, orient=tk.HORIZONTAL, command=self.txt_output.xview)
        self.txt_output.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_output.pack(fill=tk.BOTH, expand=True)

    def tulis_log(self, aksi, modul, durasi_ms):
        self.lbl_log.config(text=f"{aksi:<20} -> {modul:<18} | Waktu: {durasi_ms:.2f} ms")

    def ambil_subset_larik(self, n):
        ambil = min(n, self.larik.jumlah)
        return [self.larik.get(i) for i in range(ambil)]

    def cmd_array_get(self):
        try:
            i = int(self.entry_idx.get())
            t0 = time.perf_counter()
            p = self.larik.get(i)
            ms = (time.perf_counter() - t0) * 1000
            self.tulis_log("array_get", "M1 - array", ms)
            self.tampilkan_satu(p, f"ARRAY - INDEKS KE-{i}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_ll_get(self):
        try:
            i = int(self.entry_idx.get())
            t0 = time.perf_counter()
            p = self.rantai.get(i)
            ms = (time.perf_counter() - t0) * 1000
            self.tulis_log("linkedlist_get", "M1 - linkedlist", ms)
            self.tampilkan_satu(p, f"LINKED LIST - INDEKS KE-{i}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_tambah(self, tipe_ds, prioritas):
        nama = self.entry_nama.get()
        menu = self.entry_menu.get()
        oid_baru = f"O-{self.larik.jumlah + 1:06d}"
        p = Pesanan(oid_baru, nama, "resto-lokal", menu, 15000, prioritas, "0", "", "ANTRE")

        if prioritas == 3:
            tipe_teks = "REGULER"
        elif prioritas == 2:
            tipe_teks = "PRIORITAS"
        else:
            tipe_teks = "VIP"

        if tipe_ds == "array":
            ds = self.larik
        else:
            ds = self.rantai

        t0 = time.perf_counter()
        if prioritas == 3:
            ds.tambah_reguler(p)
        elif prioritas == 2:
            ds.tambah_prioritas(p)
        else:
            ds.tambah_vip(p)
        ms = (time.perf_counter() - t0) * 1000

        if tipe_ds == "array":
            self.tulis_log(f"array_tambah_{tipe_teks.lower()}", "M1 - array", ms)
        else:
            self.tulis_log(f"ll_tambah_{tipe_teks.lower()}", "M1 - linkedlist", ms)
        self.tampilkan_satu(p, f"BERHASIL TAMBAH ({tipe_teks})")

    def cmd_hapus(self, tipe_ds):
        try:
            i = int(self.entry_idx.get())
            t0 = time.perf_counter()
            if tipe_ds == "array":
                p = self.larik.hapus(i)
            else:
                p = self.rantai.hapus(i)
            ms = (time.perf_counter() - t0) * 1000
            self.tulis_log("hapus_pesanan", f"M1 - {tipe_ds}", ms)
            self.tampilkan_satu(p, f"PESANAN TELAH DIHAPUS (INDEKS {i})")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_enqueue(self):
        try:
            oid_antre = f"Q-{self.antrean.size + 1:04d}"
            p = Pesanan(oid_antre, self.entry_nama.get(), "resto-lokal", self.entry_menu.get(),
                        15000, 3, "0", "", "ANTRE")
            t0 = time.perf_counter()
            self.antrean.enqueue(p)
            ms = (time.perf_counter() - t0) * 1000
            self.tulis_log("queue_enqueue", "M2 - queue", ms)
            self.tampilkan_satu(p, f"MASUK KE ANTREAN FIFO (Total: {self.antrean.size})")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_layani(self):
        try:
            t0 = time.perf_counter()
            p = self.antrean.dequeue()
            p.status = "DONE"
            self.undo_stack.push(p)
            ms = (time.perf_counter() - t0) * 1000
            self.tulis_log("queue_dequeue", "M2 - queue", ms)
            self.tampilkan_satu(p, f"SELESAI DILAYANI (Sisa: {self.antrean.size})")
        except Exception as e:
            messagebox.showwarning("Peringatan", str(e))

    def cmd_undo(self):
        try:
            t0 = time.perf_counter()
            p = self.undo_stack.pop()
            p.status = "ANTRE"
            self.antrean.kembalikan_ke_depan(p)
            ms = (time.perf_counter() - t0) * 1000
            self.tulis_log("stack_undo", "M2 - stack", ms)
            self.tampilkan_satu(p, f"BATALKAN PELAYANAN (UNDO) (Total: {self.antrean.size})")
        except Exception as e:
            messagebox.showwarning("Peringatan", str(e))

    def cmd_insertion_sort(self):
        try:
            n = int(self.entry_n_sort.get())
            kunci = self.combo_kunci.get()
            data = self.ambil_subset_larik(n)

            t0 = time.perf_counter()
            hasil, comp, mov = insertion_sort(data, kunci=kunci)
            ms = (time.perf_counter() - t0) * 1000

            self.tulis_log("insertion_sort", "M3 - insertion sort", ms)
            self.tampilkan_tabel_sort(hasil, f"{len(hasil):,} pesanan diurutkan menurut {kunci}.", comp, mov)
        except Exception as e:
            messagebox.showwarning("Peringatan M3", str(e))

    def cmd_merge_sort(self):
        try:
            n = int(self.entry_n_sort.get())
            kunci = self.combo_kunci.get()
            data = self.ambil_subset_larik(n)

            t0 = time.perf_counter()
            hasil, comp, mov = merge_sort(data, kunci=kunci)
            ms = (time.perf_counter() - t0) * 1000

            self.tulis_log("merge_sort", "M3 - merge sort", ms)
            self.tampilkan_tabel_sort(hasil, f"{len(hasil):,} pesanan diurutkan menurut {kunci}.", comp, mov)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_linear_search(self):
        target = self.entry_oid.get().strip()
        semua_data = [self.larik.get(i) for i in range(self.larik.jumlah)]

        t0 = time.perf_counter()
        idx, item, comp = linear_search(semua_data, target)
        ms = (time.perf_counter() - t0) * 1000

        self.tulis_log("linear_search", "M3 - linear search", ms)
        self.txt_output.delete("1.0", tk.END)
        if idx != -1:
            self.txt_output.insert(tk.END, f"Ditemukan pada indeks {idx:,}.\n")
            self.txt_output.insert(tk.END, f"{comp:,} perbandingan.\n\n")
            self.tampilkan_detail_search(item)
        else:
            self.txt_output.insert(tk.END, f"Pesanan {target} TIDAK DITEMUKAN.\n{comp:,} perbandingan.")

    def cmd_binary_search(self):
        target = self.entry_oid.get().strip()

        # data diurutkan sekali saja, setelah itu dipakai ulang
        if self.cache_urut_oid is None:
            semua_data = [self.larik.get(i) for i in range(self.larik.jumlah)]
            t_sort = time.perf_counter()
            self.cache_urut_oid, _, _ = merge_sort(semua_data, kunci="oid")
            self.waktu_bangun_mrg_ms = (time.perf_counter() - t_sort) * 1000

        t0 = time.perf_counter()
        idx, item, comp = binary_search(self.cache_urut_oid, target)
        ms = (time.perf_counter() - t0) * 1000

        self.tulis_log("binary_search", "M3 - binary search", ms)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"Daftar terurut oid dibangun sekali dengan merge sort, {self.waktu_bangun_mrg_ms:.2f} ms.\n")
        if idx != -1:
            self.txt_output.insert(tk.END, f"Ditemukan pada baris ke-{idx + 1:,} dari {len(self.cache_urut_oid):,} baris.\n")
            self.txt_output.insert(tk.END, f"{comp} perbandingan, bandingkan dengan linear search.\n\n")
            self.tampilkan_detail_search(item)
        else:
            self.txt_output.insert(tk.END, f"Pesanan {target} TIDAK DITEMUKAN.\n{comp} perbandingan.")

    def cmd_bangun_hash(self):
        t0 = time.perf_counter()
        self.peta_hash = PetaHash(kapasitas=400003)
        for i in range(self.larik.jumlah):
            p = self.larik.get(i)
            self.peta_hash.put(p.oid, p)
        self.waktu_bangun_hash_ms = (time.perf_counter() - t0) * 1000

        self.tulis_log("bangun_hash", "M4 - hash table", self.waktu_bangun_hash_ms)

        teks = "=== INDEKS HASH SELESAI DIBANGUN ===\n"
        teks += f"Total Data Masuk   : {self.peta_hash.jumlah:,} pesanan\n"
        teks += f"Kapasitas Larik    : {self.peta_hash.kapasitas:,} slot\n"
        teks += f"Total Tabrakan     : {self.peta_hash.total_tabrakan:,} kali\n"
        teks += f"Waktu Pembangunan  : {self.waktu_bangun_hash_ms:.2f} ms ({self.waktu_bangun_hash_ms / 1000:.2f} detik)\n\n"
        teks += "Sekarang indeks hash sudah siap digunakan untuk pencarian instan O(1)!"
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, teks)

    def cmd_hash_search(self):
        target = self.entry_oid.get().strip()

        # kalau indeks belum dibangun, bangun dulu
        if self.peta_hash is None:
            self.cmd_bangun_hash()

        t0 = time.perf_counter()
        item, comp = self.peta_hash.get(target)
        ms = (time.perf_counter() - t0) * 1000

        self.tulis_log("hash_search", "M4 - hash table", ms)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"Pencarian memakai Hash Table (O(1)). Indeks dibangun dalam {self.waktu_bangun_hash_ms:.2f} ms.\n")
        if item is not None:
            self.txt_output.insert(tk.END, f"Ditemukan langsung hanya dalam {comp} perbandingan!\n\n")
            self.tampilkan_detail_search(item)
        else:
            self.txt_output.insert(tk.END, f"Pesanan {target} TIDAK DITEMUKAN.\n{comp} perbandingan.")

    def tampilkan_satu(self, p, judul):
        teks = f"=== {judul} ===\n"
        teks += f"OID          : {p.oid}\n"
        teks += f"Pelanggan    : {p.pelanggan}\n"
        teks += f"Resto        : {p.resto}\n"
        teks += f"Menu         : {p.menu}\n"
        teks += f"Harga        : Rp {int(p.harga):,}\n"
        teks += f"Prioritas    : {p.prioritas}\n"
        teks += f"Status       : {p.status}\n"
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, teks)

    def tampilkan_detail_search(self, p):
        teks = f"{'kolom':<15} | isi\n"
        teks += "-" * 40 + "\n"
        teks += f"{'oid':<15} | {p.oid}\n"
        teks += f"{'pelanggan':<15} | {p.pelanggan}\n"
        teks += f"{'resto':<15} | {p.resto}\n"
        teks += f"{'menu':<15} | {p.menu}\n"
        teks += f"{'harga':<15} | {int(p.harga):,}\n"
        teks += f"{'prioritas':<15} | {p.prioritas}\n"
        teks += f"{'masuk':<15} | {format_detik(p.t_masuk)}\n"
        teks += f"{'selesai':<15} | {format_detik(p.t_selesai)}\n"
        teks += f"{'status':<15} | {p.status}\n"
        self.txt_output.insert(tk.END, teks)

    def tampilkan_tabel_sort(self, daftar, info, comp, mov):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"{info}\n")
        self.txt_output.insert(tk.END, f"{comp:,} perbandingan, {mov:,} pemindahan.\n\n")

        header = f"{'#':<4} | {'oid':<10} | {'harga':<10} | {'selesai':<10} | {'resto':<16} | menu\n"
        self.txt_output.insert(tk.END, header)
        self.txt_output.insert(tk.END, "-" * 75 + "\n")

        # tampilkan 100 baris saja biar GUI tidak berat
        maks_tampil = min(100, len(daftar))
        for i in range(maks_tampil):
            p = daftar[i]
            harga_str = f"{int(p.harga):,}"
            selesai_str = format_detik(p.t_selesai)
            baris = f"{i + 1:<4} | {p.oid:<10} | {harga_str:<10} | {selesai_str:<10} | {p.resto:<16} | {p.menu}\n"
            self.txt_output.insert(tk.END, baris)

        if len(daftar) > 100:
            self.txt_output.insert(tk.END, f"\n... dan {len(daftar) - 100:,} baris lainnya (hanya menampilkan 100 data teratas agar GUI ringan).")