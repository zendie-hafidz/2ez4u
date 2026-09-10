

class Pesanan:
    __slots__ = ('oid', 'pelanggan', 'resto', 'menu', 'harga', 'prioritas', 't_masuk', 't_selesai', 'status')

    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu

        # jaga2 kalo data dari csv/input ternyata bukan angka
        self.harga = int(harga) if str(harga).isdigit() else 0
        self.prioritas = int(prioritas) if str(prioritas).isdigit() else 3
        self.t_masuk = int(t_masuk) if str(t_masuk).isdigit() else 0
        self.t_selesai = int(t_selesai) if t_selesai and str(t_selesai).isdigit() else None
        self.status = status

    def __repr__(self):
        return f"<Pesanan {self.oid}: {self.pelanggan} - {self.status}>"


class Node:
    # simpul buat linked list, simpel aja
    def __init__(self, data):
        self.data = data
        self.next = None


class Array:
    # larik dinamis manual, kapasitas digandain tiap penuh (2x)
    # jadi tambah_reguler rata2 O(1) walau sesekali kena resize O(n)

    def __init__(self, kapasitas_awal=16):
        self.kapasitas = kapasitas_awal
        self.jumlah = 0
        self.data = [None] * self.kapasitas

    def _resize(self, kapasitas_baru):
        data_baru = [None] * kapasitas_baru
        for i in range(self.jumlah):
            data_baru[i] = self.data[i]
        self.data = data_baru
        self.kapasitas = kapasitas_baru

    def tambah_reguler(self, v):
        # taro di belakang antrian, paling murah operasinya
        if self.jumlah == self.kapasitas:
            self._resize(self.kapasitas * 2)
        self.data[self.jumlah] = v
        self.jumlah += 1

    def tambah_vip(self, v):
        # vip masuk paling depan -> semua elemen digeser dulu ke kanan
        if self.jumlah == self.kapasitas:
            self._resize(self.kapasitas * 2)
        for i in range(self.jumlah, 0, -1):
            self.data[i] = self.data[i - 1]
        self.data[0] = v
        self.jumlah += 1

    def tambah_prioritas(self, v):
        # nyerobot ke tengah2 antrian
        if self.jumlah == self.kapasitas:
            self._resize(self.kapasitas * 2)
        mid = self.jumlah // 2
        for i in range(self.jumlah, mid, -1):
            self.data[i] = self.data[i - 1]
        self.data[mid] = v
        self.jumlah += 1

    def get(self, i):
        if i < 0 or i >= self.jumlah:
            raise IndexError("indeks di luar jangkauan")
        return self.data[i]

    def hapus(self, i):
        if i < 0 or i >= self.jumlah:
            raise IndexError("indeks di luar jangkauan")

        item = self.data[i]
        # geser semua yg di belakang i maju satu langkah
        for idx in range(i, self.jumlah - 1):
            self.data[idx] = self.data[idx + 1]

        self.data[self.jumlah - 1] = None
        self.jumlah -= 1
        return item


class LinkList:
    # singly linked list, pake head & tail biar insert belakang tetep O(1)

    def __init__(self):
        self.head = None
        self.tail = None
        self.jumlah = 0

    def tambah_reguler(self, v):
        node_baru = Node(v)
        if self.head is None:
            self.head = node_baru
            self.tail = node_baru
        else:
            self.tail.next = node_baru
            self.tail = node_baru
        self.jumlah += 1

    def tambah_vip(self, v):
        # tinggal tuker head, gak perlu geser2 kayak di array
        node_baru = Node(v)
        if self.head is None:
            self.head = node_baru
            self.tail = node_baru
        else:
            node_baru.next = self.head
            self.head = node_baru
        self.jumlah += 1

    def tambah_prioritas(self, v):
        # tetep harus jalan dari head buat nyampe ke tengah, gak ada shortcut
        if self.head is None or self.jumlah <= 1:
            self.tambah_vip(v)
            return

        mid = self.jumlah // 2
        node_baru = Node(v)
        curr = self.head
        for _ in range(mid - 1):
            curr = curr.next

        node_baru.next = curr.next
        curr.next = node_baru
        self.jumlah += 1

    def get(self, i):
        if i < 0 or i >= self.jumlah:
            raise IndexError("indeks di luar jangkauan")
        curr = self.head
        for _ in range(i):
            curr = curr.next
        return curr.data

    def hapus(self, i):
        if i < 0 or i >= self.jumlah:
            raise IndexError("indeks di luar jangkauan")

        if i == 0:
            item = self.head.data
            self.head = self.head.next
            if self.jumlah == 1:
                self.tail = None
            self.jumlah -= 1
            return item

        curr = self.head
        for _ in range(i - 1):
            curr = curr.next

        item = curr.next.data
        if curr.next == self.tail:
            self.tail = curr
        curr.next = curr.next.next
        self.jumlah -= 1
        return item