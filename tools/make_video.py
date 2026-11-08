#!/usr/bin/env python3
"""把多张竖版卡片拼成幻灯片视频（1080x1920，带字幕条）。

用法:
  python3 tools/make_video.py --images a.png b.png c.png --out out.mp4 \
      --per 20 --subtitle "顶栏字幕|底栏字幕" --subtitle "…" --subtitle "…"
"""
import argparse
import os
import subprocess
import sys

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write((r.stderr or r.stdout)[-800:])
        raise SystemExit("ffmpeg failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--per", type=int, default=20, help="每张停留秒数")
    ap.add_argument("--subtitle", action="append", default=[],
                    help="每张图对应的 '顶栏字幕|底栏字幕'")
    a = ap.parse_args()

    for img in a.images:
        if not os.path.exists(img):
            raise SystemExit(f"missing {img}")

    inputs = []
    for img in a.images:
        inputs += ["-loop", "1", "-t", str(a.per), "-i", img]

    filt = []
    for i in range(len(a.images)):
        filt.append(
            f"[{i}:v]scale=1200:2133,zoompan=z='1+0.04*on/{a.per*30}':d={a.per*30}"
            f":s=1080x1920:fps=30,format=yuv420p[v{i}]")
    concat = "".join(f"[v{i}]" for i in range(len(a.images)))
    filt.append(f"{concat}concat=n={len(a.images)}:v=1:a=0[c0]")

    labels = ["[c0]"]
    for i, sub in enumerate(a.subtitle):
        parts = sub.split("|", 1)
        t0, t1 = i * a.per + 1, (i + 1) * a.per - 1
        if parts[0]:
            filt.append(
                f"{labels[-1]}drawtext=fontfile={FONT}:text='{parts[0]}':fontsize=44:"
                f"fontcolor=white:borderw=2:bordercolor=black@0.6:"
                f"x=(w-text_w)/2:y=160:enable='between(t,{t0},{t1})'[c{i+1}a]")
            labels.append(f"[c{i+1}a]")
        if len(parts) > 1 and parts[1]:
            filt.append(
                f"{labels[-1]}drawtext=fontfile={FONT}:text='{parts[1]}':fontsize=40:"
                f"fontcolor=white:borderw=2:bordercolor=black@0.6:"
                f"x=(w-text_w)/2:y=1780:enable='between(t,{t0},{t1})'[c{i+1}b]")
            labels.append(f"[c{i+1}b]")

    filt.append(f"{labels[-1]}null[v]")

    total = a.per * len(a.images)
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + [
        "-filter_complex", ";".join(filt),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-t", str(total), "-map", "[v]", "-map", f"{len(a.images)}:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", a.out,
    ]
    run(cmd)
    print(a.out)


if __name__ == "__main__":
    main()
