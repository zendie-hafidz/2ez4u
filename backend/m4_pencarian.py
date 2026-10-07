class PetaHash:
    # hash table sendiri, tanpa dict bawaan Python (separate chaining)
    def __init__(self, kapasitas=400003):
        # bilangan prima di atas 200.000 supaya load factor sekitar 0.5
        self.kapasitas = kapasitas
        self.tabel = [None] * kapasitas
        self.jumlah = 0
        self.total_tabrakan = 0

    def hash_teks(self, teks):
        # ubah string OID jadi indeks array
        h = 0
        for huruf in str(teks):
            h = (h * 31 + ord(huruf)) % self.kapasitas
        return h

    def put(self, kunci, nilai):
        idx = self.hash_teks(kunci)

        # slot masih kosong, langsung buat rantai baru
        if self.tabel[idx] is None:
            self.tabel[idx] = [(kunci, nilai)]
            self.jumlah += 1
            return

        # slot sudah terisi, berarti tabrakan
        self.total_tabrakan += 1
        rantai = self.tabel[idx]

        # kalau kunci sudah ada, timpa nilainya
        for i in range(len(rantai)):
            if rantai[i][0] == kunci:
                rantai[i] = (kunci, nilai)
                return

        # kunci belum ada, tambahkan ke ujung rantai
        rantai.append((kunci, nilai))
        self.jumlah += 1

    def get(self, kunci):
        # cari pesanan berdasarkan OID, sekalian hitung jumlah perbandingan
        idx = self.hash_teks(kunci)
        rantai = self.tabel[idx]

        if rantai is None:
            return None, 1

        perbandingan = 0
        for pasangan in rantai:
            perbandingan += 1
            if pasangan[0] == kunci:
                return pasangan[1], perbandingan

        return None, perbandingan