#!/usr/bin/env python3
"""Hosting video + penjadwalan ke Buffer: TikTok (mulaimandiri) 20.00 WIB dan YouTube (uda2biaso) 23.00 WIB.

  python stickman/post_stickman.py --video out/video.mp4 --meta out/meta.json [--dry-run]
  python stickman/post_stickman.py --list-channels
Tidak menyentuh slot lain (17.00 / 19.00) dan tidak memakai kode alur lama.
"""
import argparse, datetime as dt, json, os, shutil, subprocess, sys, tempfile, time
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
API = "https://api.buffer.com"
WIB = dt.timezone(dt.timedelta(hours=7))
LOG = os.path.join(ROOT, "posted_log.txt")
UA = "mulaimandiri-stickman/1.0"


def warn(msg):
    print(f"::warning::{msg}", flush=True)


# ------------------------------------------------------------ Buffer API
def gql(query):
    req = urllib.request.Request(API, data=json.dumps({"query": query}).encode(), method="POST", headers={
        "Authorization": f"Bearer {os.environ['BUFFER_API_KEY']}", "Content-Type": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}")
    if body.get("errors"):
        raise RuntimeError(f"GraphQL error: {json.dumps(body['errors'])[:400]}")
    return body["data"]


def list_channels():
    orgs = gql("query { account { organizations { id name } } }")["account"]["organizations"]
    for o in orgs:
        print(f"Organisasi: {o['name']} ({o['id']})")
        chans = gql('query { channels(input: {organizationId: %s}) { id name displayName service } }' % json.dumps(o["id"]))["channels"]
        for c in chans:
            print(f"   {c['service']:<10} {c.get('displayName') or c['name']:<28} ID = {c['id']}")


def q(s):
    return json.dumps(s, ensure_ascii=False)


def create_post(channel_id, text, due_iso, video_url, service, title=None, own_voice=False):
    ai = os.environ.get("STICK_AI_LABEL", "1") == "1" and not own_voice
    if service == "tiktok":
        asset = "video: { url: %s, metadata: { thumbnailOffset: 100 } }" % q(video_url)
        meta = "tiktok: { isAiGenerated: %s }" % str(ai).lower()
    else:
        asset = "video: { url: %s }" % q(video_url)
        meta = "youtube: { title: %s, categoryId: %s, madeForKids: false, notifySubscribers: true, isAiGenerated: %s }" % (
            q(title[:100]), q(os.environ.get("STICK_YT_CATEGORY", "27")), str(ai).lower())
    return """mutation CreatePost {
  createPost(input: {
    text: %s
    channelId: %s
    schedulingType: automatic
    mode: customScheduled
    dueAt: %s
    assets: [{ %s }]
    metadata: { %s }
  }) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}""" % (q(text), q(channel_id), q(due_iso), asset, meta)


# --------------------------------------------------------- hosting video
def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} {cmd[1]} gagal: {r.stderr.strip()[-300:]}")
    return r.stdout.strip()


def verify(url, tries=8):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Range": "bytes=0-1023", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                ctype = r.headers.get("Content-Type", "")
                if r.status in (200, 206) and r.geturl() == url and ("video" in ctype or "octet-stream" in ctype):
                    return True, ctype
                print(f"   cek {i + 1}: status {r.status}, tipe {ctype}, url akhir {'sama' if r.geturl() == url else 'BERBEDA'}")
        except Exception as e:  # noqa
            print(f"   cek {i + 1}: {str(e)[:90]}")
        time.sleep(15)
    return False, ""


def host_video(path, name):
    """Taruh video di branch yatim 'stickman-media' (1 commit, dibuat ulang tiap hari), URL dikunci ke SHA commit."""
    repo, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]
    d = tempfile.mkdtemp()
    run(["git", "init", "-q", "-b", "stickman-media"], cwd=d)
    run(["git", "config", "user.name", "stickman-bot"], cwd=d)
    run(["git", "config", "user.email", "stickman-bot@users.noreply.github.com"], cwd=d)
    os.makedirs(os.path.join(d, "v"))
    shutil.copy(path, os.path.join(d, "v", name))
    run(["git", "add", "."], cwd=d)
    run(["git", "commit", "-q", "-m", f"media {name}"], cwd=d)
    run(["git", "push", "-q", "-f", f"https://x-access-token:{token}@github.com/{repo}.git",
         "HEAD:refs/heads/stickman-media"], cwd=d)
    sha = run(["git", "rev-parse", "HEAD"], cwd=d)
    for url in (f"https://cdn.jsdelivr.net/gh/{repo}@{sha}/v/{name}",
                f"https://raw.githubusercontent.com/{repo}/{sha}/v/{name}"):
        print("Mengecek URL media:", url, flush=True)
        ok, ctype = verify(url)
        if ok:
            print(f"URL media bisa diakses ({ctype}).")
            return url
    raise RuntimeError("URL media tidak bisa diakses publik. Pastikan repo berstatus PUBLIC.")


# ------------------------------------------------------------------ log
def logged(date, service):
    if not os.path.exists(LOG):
        return False
    return any(l.startswith(f"{date}\t{service}\t") for l in open(LOG, encoding="utf-8"))


def write_log(date, service, post_id, cid):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{date}\t{service}\t{post_id}\t{cid}\n")


def due_utc(date, hhmm):
    h, m = [int(x) for x in hhmm.split(":")]
    d = dt.datetime.combine(date, dt.time(h, m), tzinfo=WIB).astimezone(dt.timezone.utc)
    return d, d.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video")
    ap.add_argument("--meta", default="out/meta.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list-channels", action="store_true")
    ap.add_argument("--date", help="YYYY-MM-DD (WIB), untuk uji")
    a = ap.parse_args()
    if a.list_channels:
        return list_channels()
    meta = json.load(open(a.meta, encoding="utf-8"))
    contents = json.load(open(os.path.join(ROOT, "content.json"), encoding="utf-8"))["contents"]
    c = next(x for x in contents if x["id"] == meta["id"])
    now = dt.datetime.now(dt.timezone.utc)
    date = dt.date.fromisoformat(a.date) if a.date else now.astimezone(WIB).date()
    targets = [("tiktok", os.environ.get("BUFFER_CHANNEL_ID", ""), os.environ.get("STICK_TT_TIME", "20:00"), c["caption"], None),
               ("youtube", os.environ.get("BUFFER_YT_CHANNEL_ID", ""), os.environ.get("STICK_YT_TIME", "23:00"),
                c["yt_description"], c["yt_title"])]
    plan = []
    for svc, ch, hhmm, text, title in targets:
        d, iso = due_utc(date, hhmm)
        if logged(date, svc):
            print(f"[{svc}] sudah terjadwal untuk {date}, dilewati (penjaga ganda)."); continue
        if not ch and not a.dry_run:
            warn(f"[{svc}] ID channel kosong, dilewati."); continue
        if d - now < dt.timedelta(minutes=3) and not a.dry_run:
            warn(f"[{svc}] jam tayang {hhmm} WIB {date} sudah lewat, dilewati."); continue
        plan.append((svc, ch, hhmm, text, title, iso))
    if not plan:
        print("Tidak ada yang perlu dijadwalkan."); return
    name = f"{c['id']}_{date}.mp4"
    url = "https://contoh.invalid/" + name if a.dry_run else host_video(a.video, name)
    for svc, ch, hhmm, text, title, iso in plan:
        m = create_post(ch or "ID_CHANNEL", text, iso, url, svc, title, own_voice=(meta.get("voice", []) == ["rekaman"]))
        if a.dry_run:
            print(f"\n=== DRY-RUN {svc} ({hhmm} WIB = {iso}) ===\n{m}\n"); continue
        try:
            data = gql(m)["createPost"]
        except Exception as e:  # noqa
            warn(f"[{svc}] gagal: {e}"); sys.exit(1)
        if data.get("post"):
            pid = data["post"]["id"]
            print(f"[{svc}] terjadwal {hhmm} WIB, post id {pid}")
            write_log(date, svc, pid, c["id"])
        else:
            warn(f"[{svc}] Buffer menolak: {data.get('message')}"); sys.exit(1)


if __name__ == "__main__":
    main()
