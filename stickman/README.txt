VIDEO STICKMAN OTOMATIS - @mulaimandiri_ (TikTok 20.00 WIB) + uda2biaso (YouTube 23.00 WIB)
=========================================================================================

ISI PAKET
  stickman/build_video.py     render video (tokoh hitam-putih, suara, musik, watermark)
  stickman/tts.py             suara narasi gratis: edge-tts -> gTTS -> espeak-ng (cadangan otomatis)
  stickman/post_stickman.py   taruh video di URL publik + jadwalkan ke Buffer
  stickman/content.json       30 konten (narasi, teks layar, ekspresi, properti, kotak LANGKAH KECIL)
  stickman/gen_content.py     sumber konten; edit lalu jalankan untuk membuat ulang content.json
  stickman/fonts/             Poppins Bold + Inter SemiBold
  .github/workflows/stickman-video.yml   workflow BARU (09.00 WIB)

SUARA KLON (rekam 1-2 konten, sisanya otomatis memakai suaramu)
  Yang perlu direkam: c01 + c02 (jeda 2 detik antar kalimat) dan "sampel" (bagian terakhir NASKAH.md, dibaca sekali jalan
  tanpa jeda panjang, +-75 detik). Total +-3 menit suara bersih, satu pembicara, tanpa musik/gema/kipas. Taruh di stickman/voice/.

  JALUR 1 - OpenVoice (GRATIS, lisensi MIT: boleh komersial)           <- disarankan bila ingin gratis penuh
    Cara kerja: suara dasar bahasa Indonesia (edge-tts) lalu warna suaranya diubah ke suaramu. Yang berpindah adalah warna suara;
    logat dan intonasi masih mengikuti suara dasar, jadi hasilnya "mirip suaramu", bukan salinan sempurna.
    Pria: biarkan STICK_VOICE=id-ID-ArdiNeural. Wanita: isi variabel STICK_VOICE=id-ID-GadisNeural (pitch dasar harus searah).
    1. Variabel repo: STICK_CLONE = openvoice
    2. Workflow stickman-video > mode "clone-test". Pertama kali lama (unduh PyTorch + model, sekitar 5-15 menit).
    3. Unduh artifact "clone-test": pasangan 1_dasar.wav (suara komputer) vs 1_klon.wav (hasil klon). Dengarkan, nilai.
    4. Puas -> biarkan STICK_CLONE=openvoice; mode otomatis "klon": konten berekaman memakai rekamanmu, sisanya suara klon.
       Tidak puas -> hapus variabel STICK_CLONE; sistem kembali ke rekaman saja / suara komputer.
    Gagal di tengah jalan: tiap adegan otomatis jatuh ke edge-tts (suara komputer) dan video tetap terbit; lognya memuat sebabnya.

  JALUR 2 - ElevenLabs (kualitas biasanya lebih mirip)
    Paket Free ($0): ada kloning + API + 10.000 kredit/bulan (kebutuhan kita +-7.600). Syarat: TIDAK boleh dipakai komersial dan
    wajib mencantumkan ElevenLabs; dan layanan bisa menolak permintaan dari server cloud. Paket Starter (+-US$5/bulan): lisensi komersial.
    1. elevenlabs.io > Voices > Add a new voice > Instant Voice Clone > unggah sampel + c01 + c02 > salin Voice ID.
    2. elevenlabs.io > Developers > API Keys > buat kunci.
    3. GitHub: Secret ELEVEN_API_KEY, Variable ELEVEN_VOICE_ID. Jalankan mode "voice-test": harus muncul [OK] eleven.
    ElevenLabs diprioritaskan lebih dulu jika kunci + voice id terisi.

  Urutan cadangan otomatis: ElevenLabs -> OpenVoice -> edge-tts -> gTTS -> espeak.
  Label "konten AI" tetap menyala untuk video bersuara klon (matikan: STICK_AI_LABEL=0). Video 100% rekaman asli tanpa label.
  Unggahan suara tunduk pada kebijakan layanan; hanya unggah suaramu sendiri.

SUARA SENDIRI TANPA KLON (alternatif)
  Rekam suara sendiri sesuai stickman/voice/NASKAH.md, taruh di stickman/voice/ (c01.m4a, c02.m4a, ...).
  Selama ada rekaman, video hanya memakai konten berekaman (bergilir) dan label "AI" suara otomatis dimatikan.
  Detail: stickman/voice/README.txt. Variabel STICK_VOICE_SOURCE = auto | rekaman | tts.

TIDAK MENYENTUH: daily.yml (08.00, slot 19.00), cat-quote-video.yml (08.30, slot 17.00), publish_buffer.py,
music.py, fonts/ lama, content.csv, catvideo/.

PASANG (sekali saja)
 1. Salin folder stickman/ dan file .github/workflows/stickman-video.yml ke repo (commit ke main).
    Repo harus PUBLIC (video dihosting lewat branch otomatis "stickman-media" dan CDN jsDelivr).
 2. Secret baru: BUFFER_YT_CHANNEL_ID  (ID channel YouTube uda2biaso di Buffer).
    Belum tahu ID-nya? Jalankan workflow stickman-video, mode "list-channels", lalu baca lognya:
    di sana tertulis semua channel Buffer beserta ID-nya. Salin ID yang bertuliskan youtube / uda2biaso.
    (BUFFER_API_KEY dan BUFFER_CHANNEL_ID yang lama dipakai bersama, tidak perlu diubah.)
 3. Variabel repo (Settings > Secrets and variables > Actions > Variables), semuanya opsional:
      STICK_START_DATE  tanggal hari ke-1 (default 2026-11-08)
      STICK_TT_TIME     jam tayang TikTok  (default 20:00, WIB)
      STICK_YT_TIME     jam tayang YouTube (default 23:00, WIB)
      STICK_VOICE       id-ID-ArdiNeural (pria, default) atau id-ID-GadisNeural (wanita)
      STICK_CLONE=openvoice / ELEVEN_API_KEY / ELEVEN_VOICE_ID  suara klon (lihat SUARA KLON)
      STICK_RATE        kecepatan suara, misalnya -5% (lebih pelan) atau +5%
      STICK_AI_LABEL    1 = tandai "konten buatan AI" di TikTok/YouTube (default), 0 = matikan
      STICK_YT_CATEGORY kategori YouTube (default 27 = Education; 22 = People & Blogs)

URUTAN UJI (jangan lompat)
 A. Actions > stickman-video > Run workflow > mode "voice-test".
    Lognya menampilkan mesin suara yang jalan. Yang diharapkan: [OK] edge. Kalau edge gagal tetapi gtts/espeak
    jalan, video tetap jadi tetapi suaranya kurang natural (lihat bagian Masalah).
 B. Mode "list-channels" -> ambil ID YouTube -> simpan sebagai secret BUFFER_YT_CHANNEL_ID.
 C. Mode "dry-run": merender video, menampilkan payload Buffer, TIDAK memposting. Unduh artifact
    "stickman-video" dan tonton: suara, teks, sinkron mulut, kotak LANGKAH KECIL.
 D. Mode "normal": menjadwalkan sungguhan untuk hari itu (jika jam 20.00/23.00 hari itu belum lewat).
    Cek Buffer: harus muncul 1 post di TikTok mulaimandiri (20.00) dan 1 post di YouTube uda2biaso (23.00).
 E. Selanjutnya otomatis tiap hari 09.00 WIB. Hari ke-1 memakai konten sesuai STICK_START_DATE.

CARA KERJA HARIAN
  09.00 WIB  workflow render video (konten ke-N sesuai tanggal) -> naik ke branch media -> cek URL publik
             -> Buffer customScheduled: TikTok 20.00 dan YouTube 23.00 -> catat di stickman/posted_log.txt
  Penjaga ganda: jika sudah tercatat untuk tanggal itu, tidak dijadwalkan dua kali.
  Jika jam tayang hari itu sudah lewat saat workflow jalan, post platform itu dilewati (ada peringatan di log).

MASALAH UMUM
  - Suara robotik: berarti edge-tts gagal di runner dan yang dipakai gTTS/espeak. Jalankan voice-test.
    Layanan suara Microsoft kadang menolak IP tertentu; coba jalankan ulang beberapa jam kemudian.
    Jika ingin video TIDAK terbit tanpa suara natural, isi variabel STICK_REQUIRE_VOICE=1 (hari itu dilewati).
  - "URL media tidak bisa diakses publik": repo masih private, atau jsDelivr/GitHub sedang gangguan. Jalankan ulang.
  - Buffer menolak: baca pesan di log (mis. batas post harian, channel terputus, format video).
  - Stok konten: 30 konten = 30 hari. Siklus berulang dari konten 1. Minta paket baru sekitar hari ke-25.
  - Ingin mengubah isi satu konten: edit gen_content.py, jalankan `python stickman/gen_content.py`, commit content.json.
