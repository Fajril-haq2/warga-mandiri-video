"""Suara narasi gratis dengan 3 lapis cadangan: edge-tts -> gTTS -> espeak-ng."""
import asyncio, os, subprocess, tempfile, time, wave
import numpy as np

SR = 44100
VOICE = os.environ.get("STICK_VOICE", "id-ID-ArdiNeural")   # pria; wanita: id-ID-GadisNeural
RATE = os.environ.get("STICK_RATE", "+0%")


def _edge(text, out):
    import edge_tts
    async def go():
        await edge_tts.Communicate(text, VOICE, rate=RATE).save(out)
    last = None
    for i in range(3):
        try:
            asyncio.run(go())
            if os.path.getsize(out) > 1000:
                return
        except Exception as e:  # noqa
            last = e
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"edge-tts gagal: {last}")


def _gtts(text, out):
    from gtts import gTTS
    gTTS(text, lang="id").save(out)


def _espeak(text, out):
    subprocess.run(["espeak-ng", "-v", "id", "-s", "150", "-p", "45", "-w", out, text], check=True)


def eleven_ready():
    return bool(os.environ.get("ELEVEN_API_KEY") and os.environ.get("ELEVEN_VOICE_ID"))


def _eleven(text, out):
    """Suara klon (ElevenLabs Instant Voice Clone). Butuh ELEVEN_API_KEY + ELEVEN_VOICE_ID."""
    import json, urllib.request, urllib.error
    base = os.environ.get("ELEVEN_BASE", "https://api.elevenlabs.io").rstrip("/")
    url = f"{base}/v1/text-to-speech/{os.environ['ELEVEN_VOICE_ID']}?output_format=mp3_44100_128"
    body = json.dumps({"text": text, "model_id": os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2"),
                       "voice_settings": {"stability": float(os.environ.get("ELEVEN_STABILITY", "0.5")),
                                          "similarity_boost": 0.8, "style": 0.0, "use_speaker_boost": True}}).encode()
    last = None
    for i in range(3):
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "xi-api-key": os.environ["ELEVEN_API_KEY"], "Content-Type": "application/json", "Accept": "audio/mpeg",
            "User-Agent": "mulaimandiri-stickman/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            if len(data) > 1000:
                with open(out, "wb") as f:
                    f.write(data)
                return
            last = "respons terlalu kecil"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:160]!r}"
            if e.code in (400, 401, 402, 403, 404, 422):   # salah kunci/kredit/voice id: tidak perlu diulang
                break
        except Exception as e:  # noqa
            last = str(e)[:120]
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"ElevenLabs gagal: {last}")


BASE_CHAIN = [("edge", _edge, ".mp3"), ("gtts", _gtts, ".mp3"), ("espeak", _espeak, ".wav")]


def chain():
    c = []
    if eleven_ready():
        c.append(("eleven", _eleven, ".mp3"))
    if openvoice_ready():
        c.append(("openvoice", _openvoice, ".wav"))
    return c + BASE_CHAIN


def clone_ready():
    return eleven_ready() or openvoice_ready()
FILT = "highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=90"


def _load(path):
    with wave.open(path, "rb") as w:
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def synth(text, workdir, name):
    """Kembalikan (array float mono 44.1k, nama_mesin). Array sudah dipangkas senyap."""
    os.makedirs(workdir, exist_ok=True)
    errs = []
    for eng, fn, ext in chain():
        raw = os.path.join(workdir, f"{name}_{eng}{ext}")
        wav = os.path.join(workdir, f"{name}_{eng}_conv.wav")
        try:
            fn(text, raw)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", str(SR), "-ac", "1",
                            "-af", FILT, "-c:a", "pcm_s16le", wav], check=True)
            a = _load(wav)
            idx = np.where(np.abs(a) > 0.012)[0]
            if len(idx) < SR * 0.2:
                raise RuntimeError("audio kosong")
            a = a[max(0, idx[0] - int(SR * 0.04)): idx[-1] + int(SR * 0.08)]
            pk = float(np.max(np.abs(a)))
            return (a / pk * 0.9).astype(np.float32), eng
        except Exception as e:  # noqa
            errs.append(f"{eng}: {str(e)[:90]}")
    raise RuntimeError("semua mesin suara gagal -> " + " | ".join(errs))


REC_EXT = (".m4a", ".mp3", ".wav", ".ogg", ".aac", ".opus", ".flac", ".mp4", ".webm")
REC_FILT = "highpass=f=75,afftdn=nr=10:nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=90"


def find_recording(voice_dir, cid):
    for ext in REC_EXT:
        p = os.path.join(voice_dir, cid + ext)
        if os.path.exists(p):
            return p
    return None


def split_recording(path, n, workdir):
    """Satu file rekaman berisi n kalimat (diberi jeda) -> n potongan. Gagal jika jeda tidak terdeteksi."""
    os.makedirs(workdir, exist_ok=True)
    wav = os.path.join(workdir, "rec_conv.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ar", str(SR), "-ac", "1", "-af", REC_FILT,
                    "-c:a", "pcm_s16le", wav], check=True)
    a = _load(wav)
    hop = int(SR * 0.02)
    nf = len(a) // hop
    rms = np.sqrt(np.mean(a[: nf * hop].reshape(nf, hop) ** 2, axis=1))
    thr = max(0.006, 0.10 * float(np.percentile(rms, 95)))
    sp = rms > thr
    segs, i = [], 0
    while i < nf:
        if sp[i]:
            j = i
            while j < nf and sp[j]:
                j += 1
            segs.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for s_ in segs:                       # tarikan napas / jeda pendek < 0,25 dtk = satu kalimat
        if merged and s_[0] - merged[-1][1] < 12:
            merged[-1][1] = s_[1]
        else:
            merged.append(s_)
    merged = [m for m in merged if (m[1] - m[0]) * 0.02 >= 0.3]   # buang bunyi klik/ketukan
    while len(merged) > n:                # kelebihan potongan: gabungkan jeda terpendek
        gaps = [merged[k + 1][0] - merged[k][1] for k in range(len(merged) - 1)]
        k = int(np.argmin(gaps))
        merged[k][1] = merged[k + 1][1]
        del merged[k + 1]
    if len(merged) < n:
        raise RuntimeError(f"hanya {len(merged)} kalimat terdeteksi di {os.path.basename(path)}, seharusnya {n}. "
                           "Beri jeda diam minimal 1,5 detik antar kalimat.")
    gain = 0.9 / max(1e-6, float(np.percentile(np.abs(a), 99.8)))
    parts = []
    for s_, e_ in merged:
        seg = a[max(0, s_ * hop - int(SR * 0.05)): e_ * hop + int(SR * 0.12)]
        parts.append(np.clip(seg * gain, -0.98, 0.98).astype(np.float32))
    return parts


# ---------------------------------------------------------------- OpenVoice (gratis, lisensi MIT)
# Alur: suara dasar (edge-tts/gTTS/espeak) -> ubah warna suara ke suaramu (OpenVoice V2 tone-color converter).
# Aktif jika STICK_CLONE=openvoice dan ada rekaman referensi di stickman/voice/ (sampel.* dan/atau c01, c02, ...).
VOICE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice")
CAL_TEXT = ("Halo Warga, apa kabar hari ini? Semoga harimu berjalan lebih ringan dari kemarin. "
            "Aku mau cerita soal satu kebiasaan kecil yang diam-diam mengubah banyak hal. "
            "Pelan-pelan saja ya. Satu langkah kecil hari ini, satu langkah kecil besok.")
_OV = {}


def _reference_files():
    if not os.path.isdir(VOICE_DIR):
        return []
    names = sorted(os.listdir(VOICE_DIR))
    first = [n for n in names if os.path.splitext(n)[0].lower() == "sampel" and os.path.splitext(n)[1].lower() in REC_EXT]
    rest = [n for n in names if os.path.splitext(n)[1].lower() in REC_EXT and n not in first
            and os.path.splitext(n)[0][:1] == "c" and os.path.splitext(n)[0][1:].isdigit()]
    return [os.path.join(VOICE_DIR, n) for n in first + rest]


def openvoice_ready():
    return os.environ.get("STICK_CLONE", "").strip().lower() == "openvoice" and bool(_reference_files())


def _base_tts(text, out_wav):
    """Suara dasar bahasa Indonesia -> wav. Urutan: edge-tts, gTTS, espeak."""
    last = []
    for eng, fn, ext in BASE_CHAIN:
        raw = out_wav + "." + eng + ext
        try:
            fn(text, raw)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", "22050", "-ac", "1", out_wav],
                           check=True)
            return eng
        except Exception as e:  # noqa
            last.append(f"{eng}: {str(e)[:60]}")
    raise RuntimeError("suara dasar gagal: " + " | ".join(last))


def _ov_checkpoint(workdir):
    d = os.environ.get("OPENVOICE_CKPT_DIR")
    if d and os.path.exists(os.path.join(d, "checkpoint.pth")):
        return os.path.join(d, "config.json"), os.path.join(d, "checkpoint.pth")
    errs = []
    try:
        from huggingface_hub import hf_hub_download
        cfg = hf_hub_download("myshell-ai/OpenVoiceV2", "converter/config.json")
        ck = hf_hub_download("myshell-ai/OpenVoiceV2", "converter/checkpoint.pth")
        return cfg, ck
    except Exception as e:  # noqa
        errs.append(f"huggingface: {str(e)[:100]}")
    try:
        import urllib.request, zipfile
        z = os.path.join(workdir, "ov.zip")
        urllib.request.urlretrieve("https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip", z)
        zipfile.ZipFile(z).extractall(os.path.join(workdir, "ovck"))
        base = os.path.join(workdir, "ovck", "checkpoints_v2", "converter")
        return os.path.join(base, "config.json"), os.path.join(base, "checkpoint.pth")
    except Exception as e:  # noqa
        errs.append(f"s3: {str(e)[:100]}")
    raise RuntimeError("model OpenVoice tidak bisa diunduh -> " + " | ".join(errs))


def _prepare_reference(workdir, max_sec=150, chunk_sec=12):
    """Rekaman referensi -> potongan wav bersih (hanya bagian bicara, <= chunk_sec per potong)."""
    segs = []
    for i, f in enumerate(_reference_files()):
        wav = os.path.join(workdir, f"ref_{i}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-ar", str(SR), "-ac", "1", "-af", REC_FILT,
                        "-c:a", "pcm_s16le", wav], check=True)
        a = _load(wav)
        hop = int(SR * 0.02)
        n = len(a) // hop
        rms = np.sqrt(np.mean(a[: n * hop].reshape(n, hop) ** 2, axis=1))
        keep = rms > max(0.006, 0.10 * float(np.percentile(rms, 95)))
        segs.append(np.concatenate([a[i * hop:(i + 1) * hop] for i in range(n) if keep[i]] or [a[:hop]]))
    audio = np.concatenate(segs)[: int(SR * max_sec)]
    audio = audio / max(1e-6, float(np.max(np.abs(audio)))) * 0.9
    out, step = [], int(SR * chunk_sec)
    for k, st in enumerate(range(0, len(audio), step)):
        piece = audio[st: st + step]
        if len(piece) < SR * 3 and out:
            continue
        p = os.path.join(workdir, f"refchunk_{k}.wav")
        with wave.open(p, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((piece * 32767).astype(np.int16).tobytes())
        out.append(p)
    if not out:
        raise RuntimeError("rekaman referensi terlalu pendek (butuh minimal sekitar 30 detik suara)")
    return out


def _ov_boot(workdir):
    if _OV:
        return
    from openvoice.api import ToneColorConverter
    cfg, ck = _ov_checkpoint(workdir)
    conv = ToneColorConverter(cfg, device="cpu", enable_watermark=False)
    conv.load_ckpt(ck)
    refs = _prepare_reference(workdir)
    print(f"[openvoice] referensi: {len(refs)} potongan", flush=True)
    tgt = conv.extract_se(refs)
    cal = os.path.join(workdir, "cal_base.wav")
    eng = _base_tts(CAL_TEXT, cal)          # suara dasar yang SAMA dipakai untuk semua adegan
    src = conv.extract_se([cal])
    _OV.update(conv=conv, tgt=tgt, src=src, base=eng)
    print(f"[openvoice] siap (suara dasar: {eng})", flush=True)


def _openvoice(text, out):
    d = os.path.dirname(out) or "."
    _ov_boot(d)
    base = out + ".base.wav"
    _base_tts(text, base)
    _OV["conv"].convert(audio_src_path=base, src_se=_OV["src"], tgt_se=_OV["tgt"], output_path=out, message="default")
    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        raise RuntimeError("OpenVoice tidak menghasilkan audio")


def clone_test(outdir="out/clone_test"):
    """Bandingkan suara dasar vs suara hasil klon (untuk didengarkan, tidak memposting apa pun)."""
    os.makedirs(outdir, exist_ok=True)
    lines = ["Tanggal dua puluh lima. Saldo tinggal dua belas ribu lima ratus.",
             "Pengen boleh, asal giliran setelah dana darurat.",
             "Langkah kecil: catat tiga pengeluaran terakhir, lalu coret satu yang cuma pengen."]
    for i, t in enumerate(lines, 1):
        t0 = time.time()
        b = os.path.join(outdir, f"{i}_dasar.wav")
        c = os.path.join(outdir, f"{i}_klon.wav")
        eng = _base_tts(t, b)
        _openvoice(t, c)
        print(f"[{i}] dasar={eng} klon OK ({time.time() - t0:.1f} dtk) -> {c}", flush=True)


def probe(text="Halo warga, ini uji suara."):
    """Coba tiap mesin sendiri-sendiri dan laporkan mana yang jalan (untuk mode voice-test)."""
    import tempfile
    d = tempfile.mkdtemp()
    ok = []
    for eng, fn, ext in chain():
        raw = os.path.join(d, f"p_{eng}{ext}")
        try:
            fn(text, raw)
            print(f"[OK]    {eng}: {os.path.getsize(raw)} byte")
            ok.append(eng)
        except Exception as e:  # noqa
            print(f"[GAGAL] {eng}: {str(e)[:120]}")
    print("Mesin yang akan dipakai (urutan prioritas):", ok[0] if ok else "TIDAK ADA")
    return ok


if __name__ == "__main__":
    import sys
    if "--clone-test" in sys.argv:
        clone_test()
        sys.exit(0)
    sys.exit(0 if probe() else 1)
