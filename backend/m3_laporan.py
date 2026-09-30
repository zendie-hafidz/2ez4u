def ambil_nilai_kunci(pesanan, kunci):
    if kunci == "harga":
        return int(pesanan.harga)

    if kunci == "selesai":
        val = pesanan.t_selesai
        # kalau belum selesai (kosong / "-") taruh paling belakang
        if not val or val == "-":
            return 999999999
        try:
            return int(val)
        except ValueError:
            return str(val)

    # selain itu urut berdasarkan oid
    return str(pesanan.oid)


def insertion_sort(daftar, kunci="harga"):
    n = len(daftar)
    if n > 20000:
        raise ValueError("DITOLAK: batasnya 20.000 baris, pakai merge sort untuk data penuh")

    # copy dulu biar list aslinya nggak ikut berubah
    hasil = list(daftar)
    perbandingan = 0
    pemindahan = 0

    for i in range(1, n):
        sisip = hasil[i]
        val_sisip = ambil_nilai_kunci(sisip, kunci)
        j = i - 1
        pemindahan += 1

        while j >= 0:
            perbandingan += 1
            # pakai > (bukan >=) supaya yang nilainya sama urutannya tetap
            if ambil_nilai_kunci(hasil[j], kunci) > val_sisip:
                hasil[j + 1] = hasil[j]
                pemindahan += 1
                j -= 1
            else:
                break

        hasil[j + 1] = sisip
        pemindahan += 1

    return hasil, perbandingan, pemindahan


def merge_sort(daftar, kunci="harga"):
    perbandingan = 0
    pemindahan = 0

    def bagi(larik):
        if len(larik) <= 1:
            return larik

        tengah = len(larik) // 2
        kiri = bagi(larik[:tengah])
        kanan = bagi(larik[tengah:])
        return gabung(kiri, kanan)

    def gabung(kiri, kanan):
        nonlocal perbandingan, pemindahan
        hasil = []
        i = j = 0

        while i < len(kiri) and j < len(kanan):
            perbandingan += 1
            # supaya kalau kunci sama, yang dari kiri duluan (biar stabil)
            if ambil_nilai_kunci(kiri[i], kunci) <= ambil_nilai_kunci(kanan[j], kunci):
                hasil.append(kiri[i])
                i += 1
            else:
                hasil.append(kanan[j])
                j += 1
            pemindahan += 1

        # sisa salah satu sisi tinggal ditempel
        while i < len(kiri):
            hasil.append(kiri[i])
            pemindahan += 1
            i += 1

        while j < len(kanan):
            hasil.append(kanan[j])
            pemindahan += 1
            j += 1

        return hasil

    terurut = bagi(daftar)
    return terurut, perbandingan, pemindahan


def linear_search(daftar, target_oid):
    perbandingan = 0
    for idx in range(len(daftar)):
        perbandingan += 1
        if daftar[idx].oid == target_oid:
            return idx, daftar[idx], perbandingan
    return -1, None, perbandingan


def binary_search(daftar, target_oid):
    # daftar harus sudah urut berdasarkan oid
    lo = 0
    hi = len(daftar) - 1
    perbandingan = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        perbandingan += 1
        item = daftar[mid]

        if item.oid == target_oid:
            return mid, item, perbandingan
        elif item.oid < target_oid:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, None, perbandingan