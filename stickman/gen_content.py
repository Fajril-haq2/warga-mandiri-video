#!/usr/bin/env python3
"""Menghasilkan content.json (30 topik). Edit di sini lalu jalankan: python stickman/gen_content.py"""
import json, os

TAGS = {
    "keuangan": "#keuangan #hematuang #danadarurat",
    "mindset": "#mindset #selfreminder #mentalsehat",
    "rumahtangga": "#rumahtangga #parenting #keluarga",
    "lifestyle": "#kebiasaanbaik #hidupsederhana #rutinitas",
    "tips": "#tipsrumah #lifehack #tipspraktis",
    "humor": "#relatable #keresahan #kehidupansehari",
}


def P(s):
    out = []
    for part in [x for x in s.split(";") if x.strip()]:
        b = part.split(":", 2)
        out.append([b[0], b[1], b[2] if len(b) > 2 else ""])
    return out


def S(say, head, e="neutral", pose="stand", p=""):
    return dict(say=say, head=head, e=e, pose=pose, p=P(p))


def C(cid, tema, title, scenes, say, l1, l2, rows):
    first = scenes[0]["head"].replace("*", "").replace("^", "")
    cap = f"{first}\n\nLangkah kecil: {l1} {l2}\n\nIkuti terus, kita belajar bareng. {TAGS[tema]} #wargamandiri #mulaimandiri"
    desc = f"{first}\n\nLangkah kecil: {l1} {l2}\n\nWarga Mandiri: belajar hidup mandiri, pelan-pelan, bareng-bareng.\nIkuti juga @mulaimandiri_ di TikTok.\n\n#Shorts {TAGS[tema]} #wargamandiri"
    scenes = scenes + [dict(say=say, head="Mulai dari *yang kecil,* Warga.", e="happy", pose="cheer", p=[],
                            card=dict(l1=l1, l2=l2, rows=[[r[0], int(r[1])] for r in rows]))]
    return dict(id=cid, tema=tema, yt_title=f"{title} #Shorts"[:100], caption=cap, yt_description=desc, scenes=scenes)


R = lambda *a: [(x, 1) for x in a]
contents = [
 C("c01", "keuangan", "Butuh vs Pengen: tahan belanja impulsif", [
  S("Tanggal dua puluh lima. Saldo tinggal dua belas ribu lima ratus.", "*Tanggal 25.* Saldo tinggal segini.", "sad", "phone", "phone:hand:Saldo|Rp 12.500|red|down;calendar:mr:25"),
  S("Padahal tadi cuma checkout satu keranjang.", "Padahal tadi cuma *checkout* satu keranjang.", "shock", "head", "bag:gl1:orange;bag:gl2:green;bag:gr2:pink;bag:gr1:yellow"),
  S("Tanya dulu ke diri sendiri. Ini butuh, atau pengen?", "Ini *BUTUH* atau ^PENGEN?^", "think", "think", "sign:ml:BUTUH|blue;sign:mr:PENGEN|orange;q:top"),
  S("Butuh itu yang bikin hidup tetap jalan. Pengen itu bonus.", "*Butuh* itu bikin hidup jalan. ^Pengen^ itu bonus.", "smirk", "present", "sack:gl1:BERAS;bulb:gl2;cup:gr2;boba:gr1"),
  S("Pengen boleh, asal giliran setelah dana darurat.", "^Pengen^ boleh. Asal setelah *dana darurat.*", "happy", "up_r", "jar:gr2:DANA|DARURAT;coin:hand:Rp")],
  "Langkah kecilnya: catat tiga pengeluaran terakhir, lalu coret satu yang cuma pengen.", "Catat 3 pengeluaran terakhir.", "Coret satu yang cuma pengen.", [("Beras", 1), ("Listrik", 1), ("Kopi kekinian", 0)]),
 C("c02", "keuangan", "Dana darurat itu bantalan, bukan liburan", [
  S("Motor tiba-tiba mogok pas akhir bulan.", "Motor *mogok* pas akhir bulan.", "shock", "head", "excl:top"),
  S("Kalau tidak punya simpanan, larinya ke pinjaman.", "Tanpa simpanan, larinya ke *pinjaman.*", "sad", "phone", "phone:hand:Tagihan|Rp 850.000|red|up"),
  S("Dana darurat itu bantalan. Bukan buat jalan-jalan.", "Dana darurat itu *bantalan,* bukan liburan.", "smirk", "present", "jar:gr2:DANA|DARURAT;piggy:gl1"),
  S("Mulai kecil saja. Lima ribu sehari, lama-lama jadi.", "Mulai dari *Rp 5.000* sehari.", "happy", "up_r", "coin:hand:Rp;jar:gr2:TABUNG"),
  S("Targetnya pelan-pelan, sebesar kebutuhan hidup beberapa bulan.", "Target: kebutuhan *beberapa bulan.*", "think", "think", "calendar:mr:3 BLN;q:top")],
  "Langkah kecil: sisihkan lima ribu hari ini dan taruh di wadah terpisah.", "Sisihkan Rp 5.000 hari ini.", "Taruh di wadah terpisah.", R("Hari ini", "Besok", "Lusa")),
 C("c03", "keuangan", "Uang kecil yang diam-diam bocor", [
  S("Uang besar jarang bikin bocor. Yang kecil-kecil itu yang diam-diam.", "Bocornya justru di *uang kecil.*", "smirk", "point_r", "cup:gr1;boba:gr2"),
  S("Kopi dua puluh ribu tiap hari, sebulan jadi enam ratus ribu.", "Rp 20.000 x 30 hari = *Rp 600.000*", "shock", "head", "calendar:mr:30;excl:top"),
  S("Bukan berarti dilarang jajan. Cuma sadar ke mana perginya.", "Bukan *dilarang.* Cuma sadar.", "happy", "present", "bag:gl1:pink;heart:top"),
  S("Catat seminggu saja, nanti kelihatan sendiri bocornya di mana.", "Catat *seminggu.* Kelihatan bocornya.", "think", "think", "book:gl1;q:top")],
  "Langkah kecil: catat semua pengeluaranmu selama tujuh hari.", "Catat semua pengeluaran", "selama 7 hari.", R("Senin", "Selasa", "Rabu")),
 C("c04", "keuangan", "Aturan 24 jam sebelum checkout", [
  S("Lihat barang bagus, langsung pengen checkout?", "Lihat barang bagus, *langsung checkout?*", "shock", "phone", "phone:hand:Keranjang|Diskon 70%|green"),
  S("Coba tahan dulu dua puluh empat jam.", "Tahan dulu *24 jam.*", "smirk", "point_r", "clock:mr:06.00"),
  S("Kalau besok masih pengen dan memang perlu, baru beli.", "Besok masih *perlu?* Baru beli.", "think", "think", "q:top;bag:gr2:green"),
  S("Sering kali, besoknya keinginannya sudah hilang sendiri.", "Sering kali, keinginannya *hilang sendiri.*", "happy", "cheer", "heart:top")],
  "Langkah kecil: simpan dulu di wishlist, jangan langsung bayar.", "Simpan di wishlist dulu.", "Cek lagi besok.", [("Barang A", 1), ("Barang B", 0), ("Barang C", 1)]),
 C("c05", "keuangan", "Cicilan kecil-kecil kalau dijumlah", [
  S("Cicilan kecil-kecil kelihatan ringan, ya.", "Cicilan kecil-kecil kelihatan *ringan.*", "happy", "stand", "card:gl1:CICILAN;card:gl2:KARTU"),
  S("Tapi kalau dijumlahkan, bisa makan separuh gaji.", "Dijumlah, bisa makan *separuh gaji.*", "shock", "head", "bill:gr1;bill:gr2;excl:top"),
  S("Patokan umum, total cicilan jangan melebihi sepertiga penghasilan.", "Patokan: cicilan maksimal *sepertiga* gaji.", "think", "think", "q:top"),
  S("Sebelum ambil cicilan baru, hitung dulu semua yang sudah jalan.", "Hitung dulu *semua cicilan* yang jalan.", "smirk", "point_r", "book:gr1")],
  "Langkah kecil: tulis semua cicilan beserta tanggal jatuh temponya.", "Tulis semua cicilanmu.", "Lengkap dengan jatuh tempo.", R("Cicilan motor", "Paylater", "Cicilan HP")),
 C("c06", "keuangan", "Bayar diri sendiri dulu, baru yang lain", [
  S("Nabung dari sisa di akhir bulan, biasanya sisanya nol.", "Nabung dari *sisa?* Biasanya nol.", "sad", "slump", "piggy:gr2"),
  S("Balik caranya. Begitu gajian, sisihkan dulu.", "Balik caranya: *sisihkan dulu.*", "smirk", "present", "calendar:mr:1"),
  S("Anggap itu tagihan untuk dirimu sendiri.", "Anggap itu *tagihan* buat dirimu.", "happy", "up_r", "coin:hand:Rp;piggy:gr2"),
  S("Nominalnya kecil juga tidak apa-apa. Yang penting rutin.", "Kecil tak apa. Yang penting *rutin.*", "happy", "cheer", "jar:gr2:TABUNG")],
  "Langkah kecil: atur pindah dana otomatis tepat setelah gajian.", "Atur transfer otomatis", "tepat setelah gajian.", R("Gajian", "Pindah ke tabungan", "Sisanya dipakai")),
 C("c07", "mindset", "Berhenti membandingkan hidup dengan orang lain", [
  S("Scroll sebentar, semua orang kelihatan lebih maju.", "Scroll sebentar, semua kelihatan *lebih maju.*", "sad", "phone", "phone:hand:Liburan|Teman A|ink"),
  S("Yang kita lihat cuma bagian terbaik, bukan seluruh ceritanya.", "Itu cuma *bagian terbaik.*", "think", "think", "q:top"),
  S("Setiap orang punya titik mulai dan beban yang berbeda.", "Titik mulai tiap orang *beda.*", "neutral", "present", "house:gl1;house:gr1"),
  S("Bandingkan dirimu dengan dirimu yang kemarin.", "Bandingkan dengan *dirimu kemarin.*", "happy", "cheer", "heart:top")],
  "Langkah kecil: tulis satu hal yang lebih baik dari bulan lalu.", "Tulis 1 hal yang lebih baik", "dari bulan lalu.", R("Lebih rajin", "Lebih tenang", "Lebih hemat")),
 C("c08", "mindset", "Overthinking tengah malam, ini yang bisa dicoba", [
  S("Jam tiga pagi, mata terbuka, otak malah rapat sendiri.", "Jam 3 pagi, otak *rapat sendiri.*", "sleepy", "stand", "clock:mr:03.00;zzz:top"),
  S("Masalah rasanya dua kali lebih besar kalau malam.", "Malam hari, masalah terasa *lebih besar.*", "sad", "slump", "q:top"),
  S("Tulis semuanya di kertas, biar tidak berputar di kepala.", "Tulis di kertas, biar tak *berputar.*", "think", "up_r", "book:hand"),
  S("Besok pagi dibahas lagi. Malam ini tugasmu cuma istirahat.", "Besok dibahas lagi. Malam ini *istirahat.*", "happy", "stand", "heart:top")],
  "Langkah kecil: taruh buku catatan di dekat bantal.", "Taruh catatan dekat bantal.", "Tulis, lalu tutup.", R("Tulis kekhawatiran", "Tutup bukunya", "Istirahat")),
 C("c09", "mindset", "Hidup bukan lomba, garis finisnya beda-beda", [
  S("Teman sudah punya rumah, kita masih ngontrak.", "Teman sudah punya rumah, kita *masih ngontrak.*", "sad", "slump", "house:gr1"),
  S("Hidup bukan lomba lari. Garis finisnya tidak sama.", "Hidup bukan lomba. *Garis finisnya beda.*", "think", "think", "q:top"),
  S("Yang penting arahnya benar dan langkahnya tidak berhenti.", "Yang penting *arahnya benar.*", "smirk", "point_r", "sign:ml:ARAH|blue"),
  S("Pelan-pelan juga tetap sampai.", "Pelan-pelan, *tetap sampai.*", "happy", "walk", "plant:gr1")],
  "Langkah kecil: tentukan satu target untuk tiga bulan ke depan.", "Tentukan 1 target", "untuk 3 bulan ke depan.", R("Tulis targetnya", "Pecah jadi langkah", "Mulai hari ini")),
 C("c10", "mindset", "Gagal itu data, bukan vonis", [
  S("Usahanya gagal lagi. Rasanya ingin menyerah.", "Gagal lagi. Rasanya *ingin menyerah.*", "sad", "slump", ""),
  S("Coba lihat sebagai data, bukan vonis.", "Anggap sebagai *data,* bukan vonis.", "think", "think", "idea:top"),
  S("Apa yang berhasil, apa yang belum, apa yang bisa diubah?", "Apa yang *bisa diubah?*", "smirk", "present", "sign:ml:BERHASIL|green;sign:mr:DIUBAH|orange"),
  S("Satu perbaikan kecil, lalu coba lagi.", "Satu perbaikan kecil, *coba lagi.*", "happy", "cheer", "")],
  "Langkah kecil: tulis satu pelajaran dari kegagalan terakhirmu.", "Tulis 1 pelajaran", "dari kegagalan terakhir.", R("Apa yang terjadi", "Apa pelajarannya", "Coba lagi")),
 C("c11", "mindset", "Belum mapan bukan berarti gagal", [
  S("Umur sudah segini, tapi belum mapan. Apa aku gagal?", "Belum mapan, apa aku *gagal?*", "sad", "slump", "calendar:mr:30"),
  S("Mapan itu definisinya beda-beda, tiap orang punya ukuran sendiri.", "Ukuran *mapan* tiap orang beda.", "think", "think", "q:top"),
  S("Yang bisa dilakukan, perbaiki hari ini sedikit demi sedikit.", "Perbaiki *sedikit demi sedikit.*", "smirk", "point_r", "plant:gr1"),
  S("Kamu masih berjalan, itu sudah lebih dari cukup untuk hari ini.", "Masih berjalan itu *sudah cukup.*", "happy", "walk", "")],
  "Langkah kecil: tulis tiga hal yang sudah kamu syukuri hari ini.", "Tulis 3 hal yang kamu", "syukuri hari ini.", R("Hal pertama", "Hal kedua", "Hal ketiga")),
 C("c12", "rumahtangga", "Bagi tugas rumah, bukan tugas satu orang", [
  S("Cucian numpuk, piring numpuk, satu orang yang kewalahan.", "Satu orang kewalahan, *tugas numpuk.*", "sad", "head", "pot:gr1;bag:gl1:blue"),
  S("Rumah itu tugas bersama, bukan tugas satu orang.", "Rumah itu *tugas bersama.*", "smirk", "present", "house:gr1;house:gl1"),
  S("Bicarakan terang-terangan, jangan menunggu orang menebak.", "Bicarakan *terang-terangan.*", "neutral", "point_r", "sign:ml:TUGAS|blue"),
  S("Bagi sesuai kemampuan dan waktu masing-masing.", "Bagi sesuai *waktu masing-masing.*", "happy", "cheer", "heart:top")],
  "Langkah kecil: tulis daftar tugas rumah, lalu bagi berdua.", "Tulis daftar tugas rumah.", "Bagi berdua, bukan sendiri.", R("Masak", "Cuci piring", "Buang sampah")),
 C("c13", "rumahtangga", "Jangan lanjut debat saat sedang capek", [
  S("Capek pulang kerja, ditanya hal kecil, langsung emosi.", "Capek, ditanya hal kecil, *langsung emosi.*", "sad", "slump", "clock:mr:09.00"),
  S("Kalau lagi capek, pembicaraan jarang berujung baik.", "Lagi capek, bicara jarang *berujung baik.*", "shock", "head", "excl:top"),
  S("Bilang saja, kita lanjut dua puluh menit lagi, ya.", "Bilang: *lanjut 20 menit lagi.*", "smirk", "present", "clock:mr:00.20"),
  S("Setelah tenang, lebih mudah saling mendengar.", "Setelah tenang, *saling mendengar.*", "happy", "stand", "heart:top")],
  "Langkah kecil: sepakati satu kalimat jeda berdua.", "Sepakati satu kalimat jeda,", "misalnya: lanjut nanti ya.", R("Sepakati kalimatnya", "Pakai saat panas", "Lanjut saat tenang")),
 C("c14", "rumahtangga", "Anak tantrum di tempat umum", [
  S("Anak menangis keras di tengah toko. Semua orang menoleh.", "Anak menangis di toko, *semua menoleh.*", "shock", "head", "bag:gr1:pink;excl:top"),
  S("Tarik napas dulu. Tenangkan dirimu sebelum menenangkan anak.", "Tarik napas, *tenangkan diri dulu.*", "smirk", "present", ""),
  S("Turunkan badan sampai sejajar dengan matanya.", "Turun sejajar *mata anak.*", "happy", "stand", "heart:top"),
  S("Akui perasaannya dulu. Lalu pelan-pelan beri pilihan.", "Akui perasaannya, lalu *beri pilihan.*", "happy", "up_r", "heart:hand")],
  "Langkah kecil: siapkan satu kalimat tenang yang akan kamu ucapkan.", "Siapkan 1 kalimat tenang,", "misalnya: aku di sini.", R("Tarik napas", "Sejajar matanya", "Beri pilihan")),
 C("c15", "rumahtangga", "Lima belas menit tanpa HP", [
  S("Di rumah yang sama, tapi sibuk dengan layar masing-masing.", "Serumah, tapi sibuk *layar masing-masing.*", "sad", "phone", "phone:hand:Notifikasi|99+|red"),
  S("Coba sepakat lima belas menit tanpa HP setiap hari.", "*15 menit* tanpa HP tiap hari.", "smirk", "present", "clock:mr:00.15"),
  S("Ngobrol, main, atau cuma duduk bersama.", "Ngobrol, main, atau *duduk bersama.*", "happy", "cheer", "heart:top;book:gl1"),
  S("Waktu singkat, tapi terasa lebih hadir.", "Singkat, tapi *lebih hadir.*", "happy", "stand", "heart:top")],
  "Langkah kecil: pilih satu jam tetap untuk waktu tanpa HP.", "Pilih 1 jam tetap", "untuk waktu tanpa HP.", R("Pilih jamnya", "Taruh HP", "Ngobrol santai")),
 C("c16", "rumahtangga", "Terima kasih kecil yang jarang diucapkan", [
  S("Pasangan sudah melakukan banyak hal, tapi jarang kita ucapkan.", "Banyak hal dilakukan, *jarang diucapkan.*", "think", "think", ""),
  S("Terima kasih sudah masak. Terima kasih sudah antar anak.", "Terima kasih sudah *masak,* sudah *antar.*", "happy", "present", "pot:gr1;heart:top"),
  S("Kalimat sependek itu bisa bikin hari seseorang lebih ringan.", "Kalimat pendek, hari *lebih ringan.*", "happy", "cheer", "heart:top")],
  "Langkah kecil: ucapkan satu terima kasih yang tulus hari ini.", "Ucapkan 1 terima kasih", "yang tulus hari ini.", R("Pilih orangnya", "Sebut alasannya", "Ucapkan")),
 C("c17", "lifestyle", "Rapikan kasur, kemenangan pertama hari ini", [
  S("Pagi hari, kasur berantakan, hari belum mulai tapi sudah malas.", "Kasur berantakan, hari *sudah malas.*", "sleepy", "slump", "zzz:top"),
  S("Rapikan kasur, lima menit saja. Itu kemenangan pertamamu.", "Rapikan kasur, *kemenangan pertama.*", "smirk", "point_r", "clock:mr:05.00"),
  S("Kamar yang rapi bikin kepala ikut lebih tenang.", "Kamar rapi, *kepala lebih tenang.*", "happy", "cheer", "")],
  "Langkah kecil: besok pagi rapikan kasur sebelum pegang HP.", "Rapikan kasur dulu,", "baru pegang HP.", R("Bangun", "Rapikan kasur", "Baru buka HP")),
 C("c18", "lifestyle", "Belanja pakai daftar biar tidak boros", [
  S("Niat beli sayur, pulang bawa camilan lima macam.", "Niat beli sayur, pulang *bawa camilan.*", "shock", "head", "bag:gl1:orange;bag:gl2:pink;bag:gr1:yellow"),
  S("Tanpa daftar, tangan ikut kata hati.", "Tanpa daftar, tangan *ikut hati.*", "smirk", "point_r", "book:gr2"),
  S("Tulis dulu, cek isi kulkas, baru berangkat.", "Tulis dulu, *cek kulkas.*", "think", "think", "book:gl1"),
  S("Belanja jadi lebih cepat, uang juga lebih terkontrol.", "Lebih cepat, *lebih terkontrol.*", "happy", "up_r", "coin:hand:Rp")],
  "Langkah kecil: tulis daftar belanja sebelum berangkat.", "Tulis daftar belanja", "sebelum berangkat.", R("Cek kulkas", "Tulis daftar", "Beli sesuai daftar")),
 C("c19", "lifestyle", "Taruh botol minum di tempat yang terlihat", [
  S("Seharian kerja, baru sadar belum minum sama sekali.", "Seharian kerja, *belum minum.*", "sleepy", "slump", "laptop:gr1:KERJA"),
  S("Taruh botol minum di tempat yang selalu terlihat.", "Taruh botol di *tempat terlihat.*", "smirk", "point_r", "cup:gr2"),
  S("Yang kelihatan, biasanya lebih sering kita lakukan.", "Yang kelihatan, *lebih sering dilakukan.*", "happy", "up_r", "cup:hand")],
  "Langkah kecil: isi botol minum sekarang, taruh di mejamu.", "Isi botol minum sekarang,", "taruh di mejamu.", R("Isi botol", "Taruh di meja", "Minum")),
 C("c20", "lifestyle", "Kurangi scroll sebelum tidur", [
  S("Cuma mau lihat sebentar, tahu-tahu sudah jam satu.", "Cuma sebentar, tahu-tahu *jam 1.*", "sleepy", "phone", "phone:hand:Scroll|Lagi...|ink;clock:mr:01.00"),
  S("Besoknya bangun lemas, hari terasa panjang.", "Besoknya bangun *lemas.*", "sad", "slump", "zzz:top"),
  S("Taruh HP agak jauh dari kasur saat mau tidur.", "Taruh HP *jauh dari kasur.*", "smirk", "point_r", "clock:mr:22.00"),
  S("Tidur jadi lebih tenang, paginya lebih ringan.", "Tidur lebih *tenang.*", "happy", "stand", "zzz:top")],
  "Langkah kecil: malam ini taruh HP di seberang kamar.", "Taruh HP di seberang", "kamar malam ini.", R("Isi daya di luar", "Matikan notifikasi", "Tidur")),
 C("c21", "lifestyle", "Masak sekali, makan dua kali", [
  S("Pulang kerja capek, akhirnya pesan makanan lagi.", "Pulang capek, *pesan makanan lagi.*", "sad", "phone", "phone:hand:Pesan|Rp 45.000|red"),
  S("Coba masak porsi lebih, simpan untuk besok.", "Masak *porsi lebih,* simpan besok.", "smirk", "present", "pot:gr1;pot:gl1"),
  S("Hemat uang, hemat waktu, dan lebih tahu isi makananmu.", "Hemat *uang* dan *waktu.*", "happy", "cheer", "heart:top")],
  "Langkah kecil: akhir pekan ini masak satu menu untuk dua kali makan.", "Masak 1 menu", "untuk 2 kali makan.", R("Pilih menu", "Masak lebih", "Simpan wadah tertutup")),
 C("c22", "tips", "Kran bocor? Tutup kran utama dulu", [
  S("Kran bocor, air menetes terus, tagihan ikut naik.", "Kran bocor, tagihan *ikut naik.*", "shock", "head", "bill:gr1;excl:top"),
  S("Sebelum panik, cari dulu kran utama di rumahmu.", "Cari dulu *kran utama.*", "think", "think", "q:top"),
  S("Tutup kran utama, air berhenti, kamu punya waktu untuk tenang.", "Tutup kran utama, *air berhenti.*", "smirk", "point_r", "sign:mr:TUTUP|blue"),
  S("Lalu panggil tukang, atau perbaiki sendiri kalau kamu bisa.", "Lalu *perbaiki* atau panggil tukang.", "happy", "cheer", "")],
  "Langkah kecil: cari tahu letak kran utama rumahmu hari ini.", "Cari tahu letak", "kran utama rumahmu.", R("Cari kran utama", "Beri tanda", "Beritahu keluarga")),
 C("c23", "tips", "Pilih 3 prioritas, bukan 20 tugas", [
  S("Daftar tugasnya dua puluh, selesainya tidak ada.", "Daftar tugas 20, selesai *nol.*", "sad", "head", "book:gl1;laptop:gr1:TUGAS"),
  S("Pilih tiga saja yang paling penting hari ini.", "Pilih *3 saja* yang penting.", "smirk", "present", "calendar:mr:3"),
  S("Kerjakan yang paling penting duluan, saat tenaga masih penuh.", "Yang penting, *kerjakan duluan.*", "happy", "up_r", "book:hand")],
  "Langkah kecil: tulis tiga prioritas sebelum membuka HP.", "Tulis 3 prioritas", "sebelum buka HP.", R("Prioritas 1", "Prioritas 2", "Prioritas 3")),
 C("c24", "tips", "Hemat listrik dari hal kecil", [
  S("Tagihan listrik naik, padahal rasanya biasa saja.", "Tagihan listrik naik, *padahal biasa saja.*", "shock", "head", "bill:gr1:Rp;bulb:gl1"),
  S("Charger dan colokan yang menyala terus ikut menyedot daya.", "Colokan menyala terus *ikut menyedot.*", "think", "think", "bulb:gr1"),
  S("Cabut yang tidak dipakai, matikan lampu ruangan kosong.", "Cabut yang tak dipakai, *matikan lampu.*", "smirk", "point_r", "bulb:gl1"),
  S("Hal kecil, tapi dilakukan tiap hari hasilnya terasa.", "Hal kecil, *tiap hari terasa.*", "happy", "cheer", "")],
  "Langkah kecil: keliling rumah dan cabut satu charger yang tidak terpakai.", "Cabut charger yang", "tidak terpakai.", R("Cek kamar", "Cek ruang tamu", "Matikan lampu kosong")),
 C("c25", "tips", "Simpan nasi sisa dengan benar", [
  S("Nasi sisa dibiarkan terbuka semalaman di meja.", "Nasi sisa *terbuka* semalaman.", "shock", "head", "pot:gr1;excl:top"),
  S("Makanan yang dibiarkan lama di suhu ruang gampang basi.", "Di suhu ruang, makanan *gampang basi.*", "sad", "slump", ""),
  S("Simpan di wadah tertutup, dan masukkan kulkas secepatnya.", "Wadah tertutup, *masuk kulkas.*", "smirk", "present", "pot:gr1")],
  "Langkah kecil: sediakan wadah tertutup khusus untuk nasi sisa.", "Sediakan wadah tertutup", "untuk nasi sisa.", R("Dinginkan sebentar", "Tutup rapat", "Masuk kulkas")),
 C("c26", "tips", "Pasang pengingat tagihan, bebas denda", [
  S("Lupa bayar tagihan, kena denda, kesal sendiri.", "Lupa bayar, kena *denda.*", "sad", "slump", "bill:gr1:Rp;calendar:mr:17"),
  S("Pasang pengingat dua hari sebelum jatuh tempo.", "Pasang pengingat *H-2.*", "smirk", "point_r", "phone:hand:Pengingat|Listrik H-2|ink"),
  S("Sekali pasang, tenangnya sepanjang tahun.", "Sekali pasang, *tenang sepanjang tahun.*", "happy", "cheer", "heart:top")],
  "Langkah kecil: hari ini pasang pengingat untuk satu tagihan.", "Pasang pengingat", "untuk 1 tagihan hari ini.", R("Listrik", "Air", "Internet")),
 C("c27", "humor", "Kukira umur 30 sudah mapan", [
  S("Waktu kecil kukira umur tiga puluh itu sudah punya segalanya.", "Kukira umur 30 *sudah punya segalanya.*", "think", "stand", "house:gr1;q:top"),
  S("Ternyata umur tiga puluh masih belajar bayar tagihan tepat waktu.", "Ternyata, masih belajar *bayar tagihan.*", "sad", "slump", "bill:gl1;bill:gr1"),
  S("Tidak apa-apa. Banyak orang jalan di jalur yang sama.", "Tak apa. *Banyak yang sama.*", "smirk", "present", "heart:top"),
  S("Kita bukan ketinggalan. Kita masih belajar bareng.", "Bukan ketinggalan. *Belajar bareng.*", "happy", "cheer", "")],
  "Langkah kecil: sebutkan satu hal yang sudah kamu kuasai.", "Sebutkan 1 hal", "yang sudah kamu kuasai.", R("Bisa masak", "Bisa hemat", "Terus belajar")),
 C("c28", "humor", "Baterai sosial tinggal 1 persen", [
  S("Baterai sosial tinggal satu persen, tapi masih ada acara.", "Baterai *tinggal 1%,* masih ada acara.", "sleepy", "slump", "phone:hand:Baterai|1%|red"),
  S("Boleh kok bilang tidak, tanpa perlu alasan panjang.", "Boleh bilang *tidak.*", "smirk", "point_r", "sign:mr:TIDAK|orange"),
  S("Istirahat itu bagian dari kerja, bukan hadiah.", "Istirahat itu *bagian dari kerja.*", "happy", "stand", "zzz:top")],
  "Langkah kecil: jadwalkan satu jam sendirian minggu ini.", "Jadwalkan 1 jam", "untuk dirimu sendiri.", R("Pilih hari", "Matikan notifikasi", "Istirahat")),
 C("c29", "humor", "Teman liburan, kita lihat saldo", [
  S("Lihat teman liburan terus, kita lihat saldo rekening.", "Teman liburan, kita *lihat saldo.*", "sad", "phone", "phone:hand:Liburan|Bali|green;calendar:mr:25"),
  S("Liburan mereka bukan tagihanmu.", "Liburan mereka *bukan tagihanmu.*", "smirk", "point_r", ""),
  S("Punya rencana sendiri, sabar menabung, nanti giliranmu.", "Punya rencana sendiri, *nanti giliranmu.*", "happy", "up_r", "piggy:gr2;coin:hand:Rp")],
  "Langkah kecil: buat satu tabungan khusus untuk satu tujuan.", "Buat 1 tabungan", "khusus untuk 1 tujuan.", R("Tentukan tujuan", "Tentukan nominal", "Mulai menabung")),
 C("c30", "humor", "Janji bangun pagi vs alarm kelima", [
  S("Janjinya bangun pagi, alarm pertama sampai kelima diabaikan.", "Janji bangun pagi, *alarm ke-5.*", "sleepy", "slump", "clock:mr:05.30;zzz:top"),
  S("Bukan malas, mungkin tidurmu yang kurang.", "Bukan malas, *mungkin kurang tidur.*", "think", "think", "q:top"),
  S("Mulai dari bangun lima belas menit lebih awal saja.", "Mulai *15 menit* lebih awal.", "smirk", "point_r", "clock:mr:05.15"),
  S("Pelan-pelan, kebiasaan baru lama-lama terbentuk.", "Pelan-pelan, *kebiasaan terbentuk.*", "happy", "cheer", "")],
  "Langkah kecil: besok bangun lima belas menit lebih awal.", "Bangun 15 menit", "lebih awal besok.", R("Pasang alarm", "Taruh di seberang", "Bangun")),
]

for c in contents:  # validasi panjang teks
    for s in c["scenes"]:
        assert len(s["head"].replace("*", "").replace("^", "")) <= 62, (c["id"], s["head"])
        assert len(s["say"].split()) <= 17, (c["id"], s["say"])
        if s.get("card"):
            assert len(s["card"]["l1"]) <= 32 and len(s["card"]["l2"]) <= 32, (c["id"], s["card"])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(dict(contents=contents), f, ensure_ascii=False, indent=1)
print("OK", len(contents), "konten ->", out)
