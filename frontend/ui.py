
import tkinter as tk
from tkinter import ttk, messagebox
import time
from backend.m1_pesanan import Pesanan


class AppUI(tk.Tk):
    def __init__(self, larik, rantai):
        super().__init__()
        self.title("2EZ4U Food Delivery - Engine Benchmark")
        self.geometry("960x640")
        self.minsize(850, 550)

        self.larik = larik
        self.rantai = rantai

        self._setup_layout()

    def _setup_layout(self):
        # log/status di bawah, biar keliatan pas action ditekan
        self.frame_bottom = tk.LabelFrame(self, text="COMMAND & TIMER LOG", padx=10, pady=5)
        self.frame_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.lbl_log = tk.Label(self.frame_bottom, text="Status: Siap melayani perintah.", anchor="w", font=("Consolas", 10, "bold"), fg="#1a5fb4")
        self.lbl_log.pack(fill=tk.X)

        # panel kiri isinya tombol2 buat array & linked list
        self.frame_left = tk.LabelFrame(self, text="M1 - DATA PESANAN", width=260, padx=5, pady=5)
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        self.frame_left.pack_propagate(False)

        tk.Label(self.frame_left, text="[ ARRAY ]", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 2))
        ttk.Button(self.frame_left, text="ARRAY - LIHAT PESANAN", command=self.cmd_array_get).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="ARRAY - TAMBAH REGULER", command=lambda: self.cmd_tambah("array", 3)).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="ARRAY - TAMBAH PRIORITAS", command=lambda: self.cmd_tambah("array", 2)).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="ARRAY - TAMBAH VIP", command=lambda: self.cmd_tambah("array", 1)).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="ARRAY - HAPUS PESANAN", command=lambda: self.cmd_hapus("array")).pack(fill=tk.X, pady=1)

        ttk.Separator(self.frame_left, orient='horizontal').pack(fill=tk.X, pady=8)

        tk.Label(self.frame_left, text="[ LINKED LIST ]", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 2))
        ttk.Button(self.frame_left, text="LINKEDLIST - LIHAT PESANAN", command=self.cmd_ll_get).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="LINKEDLIST - TAMBAH REGULER", command=lambda: self.cmd_tambah("ll", 3)).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="LINKEDLIST - TAMBAH PRIORITAS", command=lambda: self.cmd_tambah("ll", 2)).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="LINKEDLIST - TAMBAH VIP", command=lambda: self.cmd_tambah("ll", 1)).pack(fill=tk.X, pady=1)
        ttk.Button(self.frame_left, text="LINKEDLIST - HAPUS PESANAN", command=lambda: self.cmd_hapus("ll")).pack(fill=tk.X, pady=1)

        # sisi kanan: form input + area buat nampilin hasil
        self.frame_right = tk.Frame(self, padx=10, pady=5)
        self.frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        form_box = tk.LabelFrame(self.frame_right, text="Form Parameter", padx=10, pady=8)
        form_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form_box, text="Indeks / Posisi:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_idx = ttk.Entry(form_box, width=15)
        self.entry_idx.insert(0, "0")
        self.entry_idx.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Nama Pelanggan:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_nama = ttk.Entry(form_box, width=30)
        self.entry_nama.insert(0, "Pelanggan Demo")
        self.entry_nama.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Resto & Menu:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_menu = ttk.Entry(form_box, width=30)
        self.entry_menu.insert(0, "kafe-teknik / kopi")
        self.entry_menu.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        tk.Label(form_box, text="Harga:").grid(row=3, column=0, sticky="w", pady=2)
        self.entry_harga = ttk.Entry(form_box, width=15)
        self.entry_harga.insert(0, "15000")
        self.entry_harga.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        out_box = tk.LabelFrame(self.frame_right, text="Hasil Pemeriksaan & Detail Objek", padx=10, pady=5)
        out_box.pack(fill=tk.BOTH, expand=True)

        self.txt_output = tk.Text(out_box, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_output.pack(fill=tk.BOTH, expand=True)

    def _log(self, aksi, struktur, durasi_ms):
        # cuma nulis ulang label status tiap ada aksi
        teks = f"{aksi} -> [{struktur}] | Waktu: {durasi_ms:.3f} ms"
        self.lbl_log.config(text=teks)

    def _tampilkan_pesanan(self, p, header=""):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"=== {header} ===\n")
        self.txt_output.insert(tk.END, f"OID          : {p.oid}\n")
        self.txt_output.insert(tk.END, f"Pelanggan    : {p.pelanggan}\n")
        self.txt_output.insert(tk.END, f"Resto        : {p.resto}\n")
        self.txt_output.insert(tk.END, f"Menu         : {p.menu}\n")
        self.txt_output.insert(tk.END, f"Harga        : Rp {p.harga:,}\n")
        self.txt_output.insert(tk.END, f"Prioritas    : {p.prioritas}\n")
        self.txt_output.insert(tk.END, f"Status       : {p.status}\n")

    def cmd_array_get(self):
        # ambil pesanan dari array berdasarkan indeks yg diisi di form
        try:
            i = int(self.entry_idx.get())
            t0 = time.perf_counter()
            item = self.larik.get(i)
            ms = (time.perf_counter() - t0) * 1000
            self._log("array_get", "M1-Array", ms)
            self._tampilkan_pesanan(item, f"ARRAY - INDEKS KE-{i}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_ll_get(self):
        # sama kayak di atas tapi versi linked list, biar kebanding waktunya
        try:
            i = int(self.entry_idx.get())
            t0 = time.perf_counter()
            item = self.rantai.get(i)
            ms = (time.perf_counter() - t0) * 1000
            self._log("linkedlist_get", "M1-LinkedList", ms)
            self._tampilkan_pesanan(item, f"LINKED LIST - INDEKS KE-{i}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_tambah(self, tipe_ds, prioritas):
        # satu fungsi buat nangani 3 jenis tambah (reguler/prioritas/vip)
        # tinggal dibedain lewat parameter prioritas
        nama = self.entry_nama.get()
        menu = self.entry_menu.get()
        harga = self.entry_harga.get()
        oid_baru = f"O-{self.larik.jumlah + 1:06d}"
        p = Pesanan(oid_baru, nama, "resto-lokal", menu, harga, prioritas, "0", "", "ANTRE")
        tipe_teks = "REGULER" if prioritas == 3 else ("PRIORITAS" if prioritas == 2 else "VIP")

        t0 = time.perf_counter()
        if tipe_ds == "array":
            if prioritas == 3:
                self.larik.tambah_reguler(p)
            elif prioritas == 2:
                self.larik.tambah_prioritas(p)
            else:
                self.larik.tambah_vip(p)
            ms = (time.perf_counter() - t0) * 1000
            self._log(f"array_tambah_{tipe_teks.lower()}", "M1-Array", ms)
            self._tampilkan_pesanan(p, f"BERHASIL DITAMBAH KE ARRAY ({tipe_teks})")
        else:
            if prioritas == 3:
                self.rantai.tambah_reguler(p)
            elif prioritas == 2:
                self.rantai.tambah_prioritas(p)
            else:
                self.rantai.tambah_vip(p)
            ms = (time.perf_counter() - t0) * 1000
            self._log(f"ll_tambah_{tipe_teks.lower()}", "M1-LinkedList", ms)
            self._tampilkan_pesanan(p, f"BERHASIL DITAMBAH KE LINKED LIST ({tipe_teks})")

    def cmd_hapus(self, tipe_ds):
        # hapus pesanan sesuai indeks, struktur datanya dipilih dari tombol mana yg ditekan
        try:
            i = int(self.entry_idx.get())
            t0 = time.perf_counter()
            if tipe_ds == "array":
                dihapus = self.larik.hapus(i)
                ms = (time.perf_counter() - t0) * 1000
                self._log("array_hapus", "M1-Array", ms)
            else:
                dihapus = self.rantai.hapus(i)
                ms = (time.perf_counter() - t0) * 1000
                self._log("ll_hapus", "M1-LinkedList", ms)
            self._tampilkan_pesanan(dihapus, f"PESANAN DIHAPUS (INDEKS {i})")
        except Exception as e:
            messagebox.showerror("Error", str(e))