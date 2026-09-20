class AntreanMelingkar:
    # circular buffer: list ukuran tetap, front & rear muter pakai modulo
    # jadi enqueue/dequeue nggak perlu geser-geser elemen (O(1))

    def __init__(self, kapasitas=50000):
        self.kapasitas = kapasitas
        self.data = [None] * kapasitas
        self.front = 0   # index pesanan paling depan
        self.rear = 0    # index slot kosong berikutnya
        self.jumlah = 0

    def is_empty(self):
        return self.jumlah == 0

    def is_full(self):
        return self.jumlah == self.kapasitas

    def enqueue(self, item):
        if self.is_full():
            raise OverflowError("Antrean pesanan sudah penuh!")
        self.data[self.rear] = item
        self.rear = (self.rear + 1) % self.kapasitas
        self.jumlah += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Antrean kosong, tidak ada pesanan untuk dilayani!")
        item = self.data[self.front]
        self.data[self.front] = None  # lepas referensinya biar bersih
        self.front = (self.front + 1) % self.kapasitas
        self.jumlah -= 1
        return item

    def peek(self):
        # lihat yang paling depan aja, nggak dikeluarkan
        if self.is_empty():
            return None
        return self.data[self.front]

    def kembalikan_ke_depan(self, item):
        # dipakai pas Undo: pesanan yang tadi udah dilayani
        # dibalikin ke posisi paling depan lagi
        if self.is_full():
            raise OverflowError("Antrean penuh, tidak bisa mengembalikan pesanan!")
        self.front = (self.front - 1 + self.kapasitas) % self.kapasitas
        self.data[self.front] = item
        self.jumlah += 1


class Tumpukan:
    # stack LIFO pakai array yang bisa membesar sendiri
    # dipakai buat nyimpan riwayat pesanan yang udah dilayani (buat Undo)

    def __init__(self, kapasitas_awal=32):
        self.kapasitas = kapasitas_awal
        self.jumlah = 0
        self.data = [None] * kapasitas_awal

    def is_empty(self):
        return self.jumlah == 0

    def _resize(self, kapasitas_baru):
        data_baru = [None] * kapasitas_baru
        for i in range(self.jumlah):
            data_baru[i] = self.data[i]
        self.data = data_baru
        self.kapasitas = kapasitas_baru

    def push(self, item):
        # kalau udah penuh, kapasitas digandakan dulu
        if self.jumlah == self.kapasitas:
            self._resize(self.kapasitas * 2)
        self.data[self.jumlah] = item
        self.jumlah += 1

    def pop(self):
        if self.is_empty():
            raise IndexError("Tidak ada riwayat untuk di-undo!")
        self.jumlah -= 1
        item = self.data[self.jumlah]
        self.data[self.jumlah] = None
        return item

    def peek(self):
        if self.is_empty():
            return None
        return self.data[self.jumlah - 1]