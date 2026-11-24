#!/usr/bin/env python3
"""Split one built pack's long clips into ~15 s parts, in place, at release time (docs/clip_chunks.md).

WHY A SECOND SCRIPT
-------------------
Retail packs are built as copies (build_sound_packs.py --clip-chunks), so cutting there touches nothing else. The WoW
Forever packs are the git clones in _release_20260930/ themselves, and Studio, the audits, the pause fixer and the
read-along scan all read those clones' WHOLE clip files. So Forever clips stay whole in the clones and on GitHub, and
this script cuts them only in the copy that is zipped for players: the pack repo's release workflow runs it on the
runner's checkout just before the BigWigs packager (owner 2026-11-24: "Do all of them"). The same script splits the
owner's live Forever install for testing.

It needs nothing but Python 3 and ffmpeg/ffprobe, and nothing outside the pack folder: the sentence starts come from
the pack's own SentenceTimings.lua. The cutting rules are those of tools/chunk_pack_clips.py (tests check they agree):
a cut sits in the middle of a real pause (silencedetect -30 dB, 0.08 s) that ends within 0.3 s of a sentence start;
greedy, parts <= 15 s, no last part under 1 s; stream copy (-c copy), no second lossy encode (owner 2026-11-16).

    python chunk_release_pack.py PACK_DIR --in-place [--workers N]

It refuses a folder inside _release_20260930/ (the clones must keep whole clips) and a pack that already has
ClipChunks.lua (run once per checkout).
"""
import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

TARGET = 15.0
NOISE_DB = -30
MIN_PAUSE = 0.08
MARK_SLACK = 0.3
MIN_LAST = 1.0


def silences(path):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-threads", "1", "-i", path,
           "-af", f"silencedetect=noise={NOISE_DB}dB:d={MIN_PAUSE}", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[0-9.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    return list(zip(starts, ends))


def cut_points(marks, pauses):
    cuts = []
    for m in marks:
        best = None
        for s, e in pauses:
            if abs(e - m) <= MARK_SLACK and (best is None or abs(e - m) < abs(best[1] - m)):
                best = (s, e)
        if best:
            cuts.append(round((max(best[0], 0) + best[1]) / 2, 3))
    return sorted(set(c for c in cuts if c > 0))


def plan(duration, cuts, target=TARGET):
    chosen, start = [], 0.0
    while duration - start > target:
        fit = [c for c in cuts if start < c <= start + target]
        after = [c for c in cuts if c > start]
        c = fit[-1] if fit else (after[0] if after else None)
        if c is None or duration - c < MIN_LAST:
            break
        chosen.append(c)
        start = c
    return chosen


def probe_len(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def read_lengths(pack):
    with open(os.path.join(pack, "SoundLengths.lua"), encoding="utf-8") as fh:
        return {k: float(v) for k, v in re.findall(r'\["([^"]+)"\]\s*=\s*([0-9.]+)', fh.read())}


def read_marks(pack):
    """{clip stem: [sentence starts in seconds]} from the pack's SentenceTimings.lua (its own unit), or {}."""
    path = os.path.join(pack, "SentenceTimings.lua")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"SpeakStone_RegisterSentenceTimings\(addonName,\s*T,\s*(\d+)\)", text)
    unit = float(m.group(1)) if m else 10.0
    return {k: [int(x) / unit for x in v.split(",") if x] for k, v in re.findall(r'\["([^"]+)"\]="([0-9,]*)"', text)}


def split_clip(src, duration, marks, target=TARGET):
    """Cut src into <stem>_c1.ogg.. beside it and remove src. -> starts of part 2..N in centiseconds, or None."""
    if duration <= target or not marks:
        return None
    cuts = plan(duration, cut_points(marks, silences(src)), target)
    if not cuts:
        return None
    stem = src[:-4]
    bounds = [0.0] + cuts + [None]
    parts = []
    try:
        for i in range(len(bounds) - 1):
            dst = f"{stem}_c{i + 1}.ogg"
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-ss", f"{bounds[i]:.3f}"]
            if bounds[i + 1] is not None:
                cmd += ["-to", f"{bounds[i + 1]:.3f}"]
            cmd += ["-map", "0:a", "-c", "copy", dst]
            parts.append(dst)
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0 or not os.path.isfile(dst):
                raise RuntimeError(r.stderr.strip()[:200])
        lengths = [probe_len(p) for p in parts]
    except Exception:
        for p in parts:                       # a failed clip stays whole, with no stray part
            if os.path.isfile(p):
                os.remove(p)
        raise
    os.remove(src)
    starts, acc = [], 0.0
    for n in lengths[:-1]:
        acc += n
        starts.append(int(round(acc * 100)))
    return starts


def clip_chunks_lua(chunks):
    lines = ["-- Long clips stored as parts cut at sentence pauses (chunk_release_pack.py, docs/clip_chunks.md).",
             "-- C[clip] = start of part 2, 3, ... in 1/100 seconds; the files are <clip>_c1.ogg .. _cN.ogg. The base",
             "-- add-on (6.1.1+) plays them back to back, and Resume starts the part it was paused in.",
             "local addonName = ...", "local C = {"]
    lines += ['["%s"]="%s",' % (k, ",".join(str(s) for s in chunks[k])) for k in sorted(chunks)]
    lines += ["}", "if SpeakStone_RegisterClipChunks then", "    SpeakStone_RegisterClipChunks(addonName, C, 100)", "else",
              "    SpeakStonePendingClipChunks = SpeakStonePendingClipChunks or {}",
              "    table.insert(SpeakStonePendingClipChunks, { name = addonName, chunks = C, unit = 100 })", "end", ""]
    return "\n".join(lines)


def add_to_toc(pack):
    tocs = [f for f in os.listdir(pack) if f.endswith(".toc")]
    for t in tocs:
        path = os.path.join(pack, t)
        with open(path, encoding="utf-8", newline="") as fh:
            raw = fh.read()
        nl = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(nl)
        if "ClipChunks.lua" in lines or "Register.lua" not in lines:
            continue
        lines.insert(lines.index("Register.lua"), "ClipChunks.lua")
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(nl.join(lines))


def split_pack(pack, workers=4, target=TARGET):
    lengths, marks = read_lengths(pack), read_marks(pack)
    sounds = os.path.join(pack, "Sounds")
    jobs = [(n, s) for n, s in sorted(lengths.items())
            if s > target and n.lower().endswith(".ogg") and os.path.isfile(os.path.join(sounds, n))]
    stats = {"long": len(jobs), "chunked": 0, "parts": 0, "whole": 0, "errors": 0}
    chunks = {}

    def work(job):
        n, s = job
        try:
            return n, split_clip(os.path.join(sounds, n), s, marks.get(n[:-4]), target), None
        except Exception as exc:
            return n, None, str(exc)

    with ThreadPoolExecutor(workers) as ex:
        for n, starts, err in ex.map(work, jobs):
            if err:
                stats["errors"] += 1
                print(f"  {n} kept whole ({err})", file=sys.stderr)
            if not starts:
                stats["whole"] += 1
                continue
            chunks[n[:-4]] = starts
            stats["chunked"] += 1
            stats["parts"] += len(starts) + 1
    if chunks:
        with open(os.path.join(pack, "ClipChunks.lua"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(clip_chunks_lua(chunks))
        add_to_toc(pack)
    return chunks, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("--in-place", action="store_true", required=True,
                    help="required: the pack's long clips are replaced by their parts")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--target", type=float, default=TARGET)
    a = ap.parse_args()
    pack = os.path.abspath(a.pack)
    if "_release_20260930" in pack.replace("\\", "/").split("/"):
        sys.exit("refusing: the Forever clones keep whole clips (Studio and the tools read them); split a copy")
    if os.path.isfile(os.path.join(pack, "ClipChunks.lua")):
        sys.exit("refusing: this pack already has ClipChunks.lua")
    chunks, stats = split_pack(pack, a.workers, a.target)
    print(f"{os.path.basename(pack)}: {stats['chunked']:,} of {stats['long']:,} long clip(s) as {stats['parts']:,} parts "
          f"({stats['whole']} kept whole, {stats['errors']} errors)")


if __name__ == "__main__":
    main()
