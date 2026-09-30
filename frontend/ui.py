# frontend/ui.py
import time
import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk

from backend.m1_pesanan import Pesanan
from backend.m3_laporan import binary_search, insertion_sort, linear_search, merge_sort

HARGA_DEFAULT = 15000
RESTO_DEFAULT = "resto-lokal"
BARIS_TAMPIL_MAKS = 100
GALAT_OPERASI = (ValueError, TypeError, LookupError, RuntimeError)

NAMA_PRIORITAS = {1: "vip", 2: "prioritas", 3: "reguler"}
STRUKTUR = {
    "array": {"grup": "[ ARRAY ]", "tombol": "ARRAY", "judul": "ARRAY", "modul": "M1 - array"},
    "ll": {"grup": "[ LINKED LIST ]", "tombol": "LINKEDLIST", "judul": "LINKED LIST", "modul": "M1 - linkedlist"},
}


def format_detik(detik):
    if not detik or detik == "-":
        return "-"
    try:
        total = int(detik)
    except ValueError:
        return str(detik)
    jam, sisa = divmod(total, 3600)
    menit, detik_sisa = divmod(sisa, 60)
    return f"{jam % 24:02d}:{menit:02d}:{detik_sisa:02d}"


def ukur(fungsi, *args, **kwargs):
    mulai = time.perf_counter()
    hasil = fungsi(*args, **kwargs)
    return hasil, (time.perf_counter() - mulai) * 1000


def rincian_pesanan(pesanan, judul):
    return (
        f"=== {judul} ===\n"
        f"OID          : {pesanan.oid}\n"
        f"Pelanggan    : {pesanan.pelanggan}\n"
        f"Resto        : {pesanan.resto}\n"
        f"Menu         : {pesanan.menu}\n"
        f"Harga        : Rp {int(pesanan.harga):,}\n"
        f"Prioritas    : {pesanan.prioritas}\n"
        f"Status       : {pesanan.status}\n"
    )


def tabel_detail_pesanan(pesanan):
    kolom = [
        ("oid", pesanan.oid),
        ("pelanggan", pesanan.pelanggan),
        ("resto", pesanan.resto),
        ("menu", pesanan.menu),
        ("harga", f"{int(pesanan.harga):,}"),
        ("prioritas", pesanan.prioritas),
        ("masuk", format_detik(pesanan.t_masuk)),
        ("selesai", format_detik(pesanan.t_selesai)),
        ("status", pesanan.status),
    ]
    baris = [f"{'kolom':<15} | isi", "-" * 40]
    baris += [f"{nama:<15} | {isi}" for nama, isi in kolom]
    return "\n".join(baris) + "\n"


def tabel_hasil_sort(daftar, ringkasan, jumlah_banding, jumlah_pindah):
    baris = [
        ringkasan,
        f"{jumlah_banding:,} perbandingan, {jumlah_pindah:,} pemindahan.",
        "",
        f"{'#':<4} | {'oid':<10} | {'harga':<10} | {'selesai':<10} | {'resto':<16} | menu",
        "-" * 75,
    ]
    for nomor, p in enumerate(daftar[:BARIS_TAMPIL_MAKS], start=1):
        harga = f"{int(p.harga):,}"
        baris.append(
            f"{nomor:<4} | {p.oid:<10} | {harga:<10} | {format_detik(p.t_selesai):<10} | {p.resto:<16} | {p.menu}"
        )

    sisa = len(daftar) - BARIS_TAMPIL_MAKS
    if sisa > 0:
        baris.append(
            f"\n... dan {sisa:,} baris lainnya (hanya menampilkan {BARIS_TAMPIL_MAKS} data teratas agar GUI ringan)."
        )
    return "\n".join(baris) + "\n"


class AppUI(tk.Tk):
    def __init__(self, larik, rantai, antrean, undo_stack):
        super().__init__()
        self.title("2EZ4U Food Delivery - Engine Benchmark")
        self.geometry("1020x720")
        self.minsize(900, 600)

        self.larik = larik
        self.rantai = rantai
        self.antrean = antrean
        self.undo_stack = undo_stack
        self.struktur = {"array": larik, "ll": rantai}

        self.cache_urut_oid = None
        self.waktu_bangun_cache_ms = 0.0

        self._susun_panel_log()
        self._susun_menu()
        self._susun_form_dan_output()

    def _susun_panel_log(self):
        panel = tk.LabelFrame(self, text="COMMAND & TIMER LOG", padx=10, pady=5)
        panel.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.lbl_log = tk.Label(
            panel, text="Status: Siap melayani perintah.", anchor="w",
            font=("Consolas", 10, "bold"), fg="#1a5fb4",
        )
        self.lbl_log.pack(fill=tk.X)

    def _susun_menu(self):
        panel = tk.Frame(self, width=280, padx=5, pady=5)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        panel.pack_propagate(False)

        kotak_m1 = self._kotak_menu(panel, "M1 - DATA PESANAN")
        for tipe_ds, info in STRUKTUR.items():
            tk.Label(kotak_m1, text=info["grup"], font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(4, 0))
            aksi = [("LIHAT PESANAN", partial(self.cmd_lihat, tipe_ds))]
            aksi += [
                (f"TAMBAH {NAMA_PRIORITAS[p].upper()}", partial(self.cmd_tambah, tipe_ds, p))
                for p in (3, 2, 1)
            ]
            aksi.append(("HAPUS PESANAN", partial(self.cmd_hapus, tipe_ds)))
            for teks, perintah in aksi:
                self._tombol(kotak_m1, f"{info['tombol']} - {teks}", perintah)

        kotak_m2 = self._kotak_menu(panel, "M2 - ANTREAN & UNDO")
        self._tombol(kotak_m2, "ISI ANTREAN (FIFO)", self.cmd_enqueue)
        self._tombol(kotak_m2, "LAYANI BERIKUTNYA", self.cmd_layani)
        self._tombol(kotak_m2, "BATALKAN / UNDO", self.cmd_undo)

        kotak_m3 = self._kotak_menu(panel, "M3 - SORT DAN SEARCH")
        self._tombol(kotak_m3, "SORT - INSERTION SORT", partial(self._jalankan_sort, "insertion_sort", insertion_sort))
        self._tombol(kotak_m3, "SORT - MERGE SORT", partial(self._jalankan_sort, "merge_sort", merge_sort))
        self._tombol(kotak_m3, "SEARCH - LINEAR SEARCH", self.cmd_linear_search)
        self._tombol(kotak_m3, "SEARCH - BINARY SEARCH", self.cmd_binary_search)

    @staticmethod
    def _kotak_menu(induk, judul):
        kotak = tk.LabelFrame(induk, text=judul, padx=5, pady=4)
        kotak.pack(fill=tk.X, pady=(0, 5))
        return kotak

    @staticmethod
    def _tombol(induk, teks, perintah):
        ttk.Button(induk, text=teks, command=perintah).pack(fill=tk.X, pady=1)

    def _susun_form_dan_output(self):
        panel = tk.Frame(self, padx=10, pady=5)
        panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        form = tk.LabelFrame(panel, text="Form Parameter", padx=10, pady=6)
        form.pack(fill=tk.X, pady=(0, 6))

        self.entry_idx = self._field_teks(form, "Indeks / Posisi:", 0, 0, 12, "0")
        self.entry_oid = self._field_teks(form, "Target OID:", 0, 2, 15, "O-137442")
        self.entry_n_sort = self._field_teks(form, "Jumlah Baris Sort:", 1, 0, 12, "10")
        self.entry_nama = self._field_teks(form, "Nama Pelanggan:", 2, 0, 22, "Pelanggan Baru")
        self.entry_menu = self._field_teks(form, "Resto & Menu:", 2, 2, 22, "kafe-teknik / kopi")

        tk.Label(form, text="Kunci Sort:").grid(row=1, column=2, sticky="w", padx=(15, 2), pady=2)
        self.combo_kunci = ttk.Combobox(form, values=["harga", "oid", "selesai"], width=13, state="readonly")
        self.combo_kunci.current(0)
        self.combo_kunci.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        kotak_output = tk.LabelFrame(panel, text="Hasil Pemeriksaan & Detail Objek", padx=10, pady=5)
        kotak_output.pack(fill=tk.BOTH, expand=True)

        self.txt_output = tk.Text(kotak_output, wrap=tk.NONE, font=("Consolas", 9))
        scroll_y = ttk.Scrollbar(kotak_output, orient=tk.VERTICAL, command=self.txt_output.yview)
        scroll_x = ttk.Scrollbar(kotak_output, orient=tk.HORIZONTAL, command=self.txt_output.xview)
        self.txt_output.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_output.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def _field_teks(form, label, baris, kolom, lebar, isi_awal):
        padx_label = (15, 2) if kolom else 0
        tk.Label(form, text=label).grid(row=baris, column=kolom, sticky="w", padx=padx_label, pady=2)
        entry = ttk.Entry(form, width=lebar)
        entry.insert(0, isi_awal)
        entry.grid(row=baris, column=kolom + 1, sticky="w", padx=5, pady=2)
        return entry

    def _log(self, aksi, modul, durasi_ms):
        self.lbl_log.config(text=f"{aksi:<20} -> {modul:<18} | Waktu: {durasi_ms:.2f} ms")

    def _tampilkan(self, teks):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, teks)

    @staticmethod
    def _baca_bilangan(entry, nama_field):
        try:
            return int(entry.get())
        except ValueError:
            raise ValueError(f"{nama_field} harus berupa bilangan bulat") from None

    def _ambil_pesanan(self, batas=None):
        jumlah = self.larik.jumlah if batas is None else min(batas, self.larik.jumlah)
        return [self.larik.get(i) for i in range(jumlah)]

    def cmd_lihat(self, tipe_ds):
        info = STRUKTUR[tipe_ds]
        try:
            indeks = self._baca_bilangan(self.entry_idx, "Indeks")
            pesanan, ms = ukur(self.struktur[tipe_ds].get, indeks)
        except GALAT_OPERASI as galat:
            messagebox.showerror("Error", str(galat))
            return

        self._log(f"{tipe_ds}_get", info["modul"], ms)
        self._tampilkan(rincian_pesanan(pesanan, f"{info['judul']} - INDEKS KE-{indeks}"))

    def cmd_tambah(self, tipe_ds, prioritas):
        info = STRUKTUR[tipe_ds]
        jenis = NAMA_PRIORITAS[prioritas]
        pesanan = Pesanan(
            f"O-{self.larik.jumlah + 1:06d}", self.entry_nama.get(), RESTO_DEFAULT,
            self.entry_menu.get(), HARGA_DEFAULT, prioritas, "0", "", "ANTRE",
        )

        try:
            _, ms = ukur(getattr(self.struktur[tipe_ds], f"tambah_{jenis}"), pesanan)
        except GALAT_OPERASI as galat:
            messagebox.showerror("Error", str(galat))
            return

        # urutan oid di cache sudah tidak berlaku setelah data berubah
        self.cache_urut_oid = None
        self._log(f"{tipe_ds}_tambah_{jenis}", info["modul"], ms)
        self._tampilkan(rincian_pesanan(pesanan, f"BERHASIL TAMBAH ({jenis.upper()})"))

    def cmd_hapus(self, tipe_ds):
        info = STRUKTUR[tipe_ds]
        try:
            indeks = self._baca_bilangan(self.entry_idx, "Indeks")
            pesanan, ms = ukur(self.struktur[tipe_ds].hapus, indeks)
        except GALAT_OPERASI as galat:
            messagebox.showerror("Error", str(galat))
            return

        self.cache_urut_oid = None
        self._log("hapus_pesanan", info["modul"], ms)
        self._tampilkan(rincian_pesanan(pesanan, f"PESANAN TELAH DIHAPUS (INDEKS {indeks})"))

    def cmd_enqueue(self):
        pesanan = Pesanan(
            f"Q-{self.antrean.size + 1:04d}", self.entry_nama.get(), RESTO_DEFAULT,
            self.entry_menu.get(), HARGA_DEFAULT, 3, "0", "", "ANTRE",
        )
        try:
            _, ms = ukur(self.antrean.enqueue, pesanan)
        except GALAT_OPERASI as galat:
            messagebox.showerror("Error", str(galat))
            return

        self._log("queue_enqueue", "M2 - queue", ms)
        self._tampilkan(rincian_pesanan(pesanan, f"MASUK KE ANTREAN FIFO (Total: {self.antrean.size})"))

    def cmd_layani(self):
        try:
            pesanan, ms = ukur(self.antrean.dequeue)
        except GALAT_OPERASI as galat:
            messagebox.showwarning("Peringatan", str(galat))
            return

        pesanan.status = "DONE"
        self.undo_stack.push(pesanan)
        self._log("queue_dequeue", "M2 - queue", ms)
        self._tampilkan(rincian_pesanan(pesanan, f"SELESAI DILAYANI (Sisa: {self.antrean.size})"))

    def cmd_undo(self):
        try:
            pesanan, ms = ukur(self.undo_stack.pop)
        except GALAT_OPERASI as galat:
            messagebox.showwarning("Peringatan", str(galat))
            return

        pesanan.status = "ANTRE"
        self.antrean.kembalikan_ke_depan(pesanan)
        self._log("stack_undo", "M2 - stack", ms)
        self._tampilkan(rincian_pesanan(pesanan, f"BATALKAN PELAYANAN (UNDO) (Total: {self.antrean.size})"))

    def _jalankan_sort(self, nama_algoritma, algoritma):
        try:
            jumlah_baris = self._baca_bilangan(self.entry_n_sort, "Jumlah baris sort")
            kunci = self.combo_kunci.get()
            (terurut, jumlah_banding, jumlah_pindah), ms = ukur(
                algoritma, self._ambil_pesanan(jumlah_baris), kunci=kunci
            )
        except GALAT_OPERASI as galat:
            messagebox.showwarning("Peringatan M3", str(galat))
            return

        self._log(nama_algoritma, f"M3 - {nama_algoritma.replace('_', ' ')}", ms)
        ringkasan = f"{len(terurut):,} pesanan diurutkan menurut {kunci}."
        self._tampilkan(tabel_hasil_sort(terurut, ringkasan, jumlah_banding, jumlah_pindah))

    def cmd_linear_search(self):
        target = self.entry_oid.get().strip()
        (indeks, pesanan, jumlah_banding), ms = ukur(linear_search, self._ambil_pesanan(), target)

        self._log("linear_search", "M3 - linear search", ms)
        if indeks == -1:
            self._tampilkan(f"Pesanan {target} TIDAK DITEMUKAN.\n{jumlah_banding:,} perbandingan.")
            return

        self._tampilkan(
            f"Ditemukan pada indeks {indeks:,}.\n"
            f"{jumlah_banding:,} perbandingan.\n\n"
            f"{tabel_detail_pesanan(pesanan)}"
        )

    def cmd_binary_search(self):
        target = self.entry_oid.get().strip()

        if self.cache_urut_oid is None:
            (self.cache_urut_oid, _, _), self.waktu_bangun_cache_ms = ukur(
                merge_sort, self._ambil_pesanan(), kunci="oid"
            )

        (indeks, pesanan, jumlah_banding), ms = ukur(binary_search, self.cache_urut_oid, target)

        self._log("binary_search", "M3 - binary search", ms)
        keterangan_cache = f"Daftar terurut oid dibangun sekali dengan merge sort, {self.waktu_bangun_cache_ms:.2f} ms.\n"
        if indeks == -1:
            self._tampilkan(f"{keterangan_cache}Pesanan {target} TIDAK DITEMUKAN.\n{jumlah_banding} perbandingan.")
            return

        self._tampilkan(
            f"{keterangan_cache}"
            f"Ditemukan pada baris ke-{indeks + 1:,} dari {len(self.cache_urut_oid):,} baris.\n"
            f"{jumlah_banding} perbandingan, bandingkan dengan linear search.\n\n"
            f"{tabel_detail_pesanan(pesanan)}"
        )