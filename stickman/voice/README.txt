FOLDER REKAMAN SUARA
Taruh rekaman di sini dengan nama: c01.m4a, c02.m4a, ... (satu file per konten; m4a/mp3/wav/ogg boleh).
Isi tiap file: kalimat-kalimat konten itu dibaca berurutan, diselingi jeda diam sekitar 2 detik. Lihat NASKAH.md.
Aturan pemakaian otomatis (variabel STICK_VOICE_SOURCE):
  auto (default)  jika ada rekaman di folder ini -> hanya konten yang punya rekaman yang dipakai (bergilir); jika kosong -> suara TTS
  rekaman         paksa memakai rekaman
  tts             paksa suara komputer
Makin banyak yang direkam, makin lama siklus tanpa pengulangan (30 rekaman = 30 hari berbeda).

Berkas khusus: sampel.m4a (bacaan panjang sekali jalan, dipakai sebagai referensi suara klon).
