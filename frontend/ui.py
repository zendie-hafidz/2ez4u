import tkinter as tk
from tkinter import ttk, messagebox
import time

from backend.m1_pesanan import Pesanan


class AppUI(tk.Tk):
    def __init__(self, larik, rantai, antrean, undo_stack):
        super().__init__()
        self.title("2EZ4U Food Delivery - Engine Benchmark")
        self.geometry("980x680")
        self.minsize(850, 580)

        # struktur data dari backend, dikirim dari main
        self.larik = larik
        self.rantai = rantai
        self.antrean = antrean
        self.undo_stack = undo_stack

        self._setup_layout()

    # ------------------------------------------------------------------
    # Tampilan
    # ------------------------------------------------------------------
    def _tombol(self, parent, teks, perintah, pady=1):
        # biar nggak nulis ttk.Button(...).pack(...) berulang-ulang
        ttk.Button(parent, text=teks, command=perintah).pack(fill=tk.X, pady=pady)

    def _setup_layout(self):
        # panel bawah: buat nampilin log + waktu eksekusi
        self.frame_bottom = tk.LabelFrame(self, text="COMMAND & TIMER LOG", padx=10, pady=5)
        self.frame_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.lbl_log = tk.Label(
            self.frame_bottom,
            text="Status: Siap melayani perintah.",
            anchor="w",
            font=("Consolas", 10, "bold"),
            fg="#1a5fb4",
        )
        self.lbl_log.pack(fill=tk.X)

        # panel kiri: tombol-tombol operasi
        self.frame_left = tk.Frame(self, width=280, padx=5, pady=5)
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        self.frame_left.pack_propagate(False)

        # --- M1 ---
        box_m1 = tk.LabelFrame(self.frame_left, text="M1 - DATA PESANAN", padx=5, pady=5)
        box_m1.pack(fill=tk.X, pady=(0, 8))

        tk.Label(box_m1, text="[ ARRAY ]", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 1))
        self._tombol(box_m1, "ARRAY - LIHAT PESANAN", self.cmd_array_get)
        self._tombol(box_m1, "ARRAY - TAMBAH REGULER", lambda: self.cmd_tambah("array", 3))
        self._tombol(box_m1, "ARRAY - TAMBAH PRIORITAS", lambda: self.cmd_tambah("array", 2))
        self._tombol(box_m1, "ARRAY - TAMBAH VIP", lambda: self.cmd_tambah("array", 1))
        self._tombol(box_m1, "ARRAY - HAPUS PESANAN", lambda: self.cmd_hapus("array"))

        tk.Label(box_m1, text="[ LINKED LIST ]", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 1))
        self._tombol(box_m1, "LINKEDLIST - LIHAT PESANAN", self.cmd_ll_get)
        self._tombol(box_m1, "LINKEDLIST - TAMBAH REGULER", lambda: self.cmd_tambah("ll", 3))
        self._tombol(box_m1, "LINKEDLIST - TAMBAH PRIORITAS", lambda: self.cmd_tambah("ll", 2))
        self._tombol(box_m1, "LINKEDLIST - TAMBAH VIP", lambda: self.cmd_tambah("ll", 1))
        self._tombol(box_m1, "LINKEDLIST - HAPUS PESANAN", lambda: self.cmd_hapus("ll"))

        # --- M2 ---
        box_m2 = tk.LabelFrame(self.frame_left, text="M2 - ANTREAN & UNDO", padx=5, pady=5)
        box_m2.pack(fill=tk.X, pady=(0, 5))

        self._tombol(box_m2, "ISI ANTREAN (FIFO)", self.cmd_enqueue, pady=2)
        self._tombol(box_m2, "LAYANI BERIKUTNYA", self.cmd_layani, pady=2)
        self._tombol(box_m2, "BATALKAN / UNDO", self.cmd_undo, pady=2)

        # panel kanan: form input + layar hasil
        self.frame_right = tk.Frame(self, padx=10, pady=5)
        self.frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        form_box = tk.LabelFrame(self.frame_right, text="Form Parameter", padx=10, pady=8)
        form_box.pack(fill=tk.X, pady=(0, 8))

        self.entry_idx = self._buat_input(form_box, 0, "Indeks / Posisi:", 15, "0")
        self.entry_nama = self._buat_input(form_box, 1, "Nama Pelanggan:", 30, "Pelanggan Demo")
        self.entry_menu = self._buat_input(form_box, 2, "Resto & Menu:", 30, "kafe-teknik / kopi")
        self.entry_harga = self._buat_input(form_box, 3, "Harga:", 15, "15000")

        out_box = tk.LabelFrame(self.frame_right, text="Hasil Pemeriksaan & Detail Objek", padx=10, pady=5)
        out_box.pack(fill=tk.BOTH, expand=True)

        self.txt_output = tk.Text(out_box, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_output.pack(fill=tk.BOTH, expand=True)

    def _buat_input(self, parent, baris, label, lebar, isi_awal):
        tk.Label(parent, text=label).grid(row=baris, column=0, sticky="w", pady=2)
        entry = ttk.Entry(parent, width=lebar)
        entry.insert(0, isi_awal)
        entry.grid(row=baris, column=1, sticky="w", padx=5, pady=2)
        return entry

    # ------------------------------------------------------------------
    # Helper output
    # ------------------------------------------------------------------
    def _log(self, aksi, struktur, durasi_ms):
        self.lbl_log.config(text=f"{aksi} -> [{struktur}] | Waktu: {durasi_ms:.3f} ms")

    def _tulis(self, *baris):
        # kosongkan layar dulu, lalu tulis baris-barisnya satu per satu
        self.txt_output.delete("1.0", tk.END)
        for b in baris:
            self.txt_output.insert(tk.END, b + "\n")

    def _tampilkan_pesanan(self, p, header=""):
        self._tulis(
            f"=== {header} ===",
            f"OID          : {p.oid}",
            f"Pelanggan    : {p.pelanggan}",
            f"Resto        : {p.resto}",
            f"Menu         : {p.menu}",
            f"Harga        : Rp {p.harga:,}",
            f"Prioritas    : {p.prioritas}",
            f"Status       : {p.status}",
        )

    # ------------------------------------------------------------------
    # Aksi Milestone 1
    # ------------------------------------------------------------------
    def cmd_array_get(self):
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
        nama = self.entry_nama.get()
        menu = self.entry_menu.get()
        harga = self.entry_harga.get()
        oid_baru = f"O-{self.larik.jumlah + 1:06d}"
        p = Pesanan(oid_baru, nama, "resto-lokal", menu, harga, prioritas, "0", "", "ANTRE")

        if prioritas == 3:
            tipe_teks = "REGULER"
        elif prioritas == 2:
            tipe_teks = "PRIORITAS"
        else:
            tipe_teks = "VIP"

        # pilih struktur datanya, sisanya sama
        if tipe_ds == "array":
            ds, nama_ds, label = self.larik, "M1-Array", "array"
        else:
            ds, nama_ds, label = self.rantai, "M1-LinkedList", "ll"

        t0 = time.perf_counter()
        if prioritas == 3:
            ds.tambah_reguler(p)
        elif prioritas == 2:
            ds.tambah_prioritas(p)
        else:
            ds.tambah_vip(p)
        ms = (time.perf_counter() - t0) * 1000

        self._log(f"{label}_tambah_{tipe_teks.lower()}", nama_ds, ms)
        judul = "ARRAY" if tipe_ds == "array" else "LINKED LIST"
        self._tampilkan_pesanan(p, f"BERHASIL DITAMBAH KE {judul} ({tipe_teks})")

    def cmd_hapus(self, tipe_ds):
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
            self._tampilkan_pesanan(dihapus, f"PESANAN TELAH DIHAPUS (INDEKS {i})")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------
    # Aksi Milestone 2
    # ------------------------------------------------------------------
    def cmd_enqueue(self):
        try:
            nama = self.entry_nama.get()
            menu = self.entry_menu.get()
            harga = self.entry_harga.get()
            oid_baru = f"Q-{self.antrean.jumlah + 1:04d}"
            p = Pesanan(oid_baru, nama, "resto-lokal", menu, harga, 3, "0", "", "ANTRE")

            t0 = time.perf_counter()
            self.antrean.enqueue(p)
            ms = (time.perf_counter() - t0) * 1000

            self._log("enqueue_fifo", "M2-CircularQueue", ms)
            self._tulis(
                "=== PESANAN MASUK KE ANTREAN (FIFO) ===",
                f"ID Antrean   : {p.oid}",
                f"Pelanggan    : {p.pelanggan}",
                f"Menu         : {p.menu}",
                f"Harga        : Rp {p.harga:,}",
                "",
                f"Total Antrean: {self.antrean.jumlah} pesanan",
                f"Terdepan     : {self.antrean.peek().pelanggan}",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cmd_layani(self):
        try:
            t0 = time.perf_counter()
            p = self.antrean.dequeue()
            p.status = "SELESAI"
            self.undo_stack.push(p)   # simpan dulu, siapa tau mau di-undo
            ms = (time.perf_counter() - t0) * 1000

            self._log("dequeue_layani", "M2-CircularQueue", ms)

            depan = self.antrean.peek()
            if depan:
                berikutnya = f"{depan.oid} ({depan.pelanggan})"
            else:
                berikutnya = "(Antrean sudah kosong)"

            self._tulis(
                "=== PESANAN SELESAI DILAYANI ===",
                f"ID Pesanan   : {p.oid}",
                f"Pelanggan    : {p.pelanggan}",
                f"Status       : {p.status}",
                "",
                f"Sisa Antrean : {self.antrean.jumlah} pesanan",
                f"Berikutnya   : {berikutnya}",
            )
        except Exception as e:
            messagebox.showwarning("Peringatan", str(e))

    def cmd_undo(self):
        try:
            t0 = time.perf_counter()
            p = self.undo_stack.pop()
            p.status = "ANTRE"
            self.antrean.kembalikan_ke_depan(p)
            ms = (time.perf_counter() - t0) * 1000

            self._log("undo_pelayanan", "M2-StackUndo", ms)
            self._tulis(
                "=== PELAYANAN DIBATALKAN (UNDO) ===",
                f"Pesanan {p.oid} ({p.pelanggan}) dikembalikan ke antrean paling depan!",
                "",
                f"Total Antrean: {self.antrean.jumlah} pesanan",
                f"Terdepan     : {self.antrean.peek().pelanggan}",
            )
        except Exception as e:
            messagebox.showwarning("Peringatan", str(e))