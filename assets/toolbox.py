#!/usr/bin/env python3
"""Render assets/toolbox-light.png and assets/toolbox-dark.png: the "Toolbox" card of the profile.

Grouped rows of pill chips (monochrome icon + name), in the same palette and card as the banner.
Icons are Simple Icons (CC0) in assets/icons/; type is Inter. Edit GROUPS and run:
    python3 assets/toolbox.py
"""
import subprocess as sp
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GROUPS = [
    ("Data", [("googlebigquery", "BigQuery"), ("dbt", "dbt"), ("googlecloud", "Google Cloud"),
              ("postgresql", "Postgres"), ("python", "Python"), ("jupyter", "Jupyter")]),
    ("Product & web", [("typescript", "TypeScript"), ("astro", "Astro"), ("bun", "Bun"), ("react", "React"),
                       ("nextdotjs", "Next.js"), ("vuedotjs", "Vue"), ("tailwindcss", "Tailwind"),
                       ("supabase", "Supabase"), ("vercel", "Vercel")]),
    ("Apps & systems", [("swift", "Swift"), ("linux", "Linux"), ("i3", "i3"), ("claude", "Claude Code")]),
]
THEMES = {  # bg, card text, label, chip fill, chip edge, card edge
    "light": ("#fbfbfd", "#1d1d1f", "#86868b", "#f0f0f3", "#0000000f", "#0000001a"),
    "dark":  ("#000000", "#f5f5f7", "#86868b", "#161618", "#ffffff14", "#ffffff1f"),
}
W, PAD, LABEL_W, CHIP_H, GAP, ROW_GAP = 2560, 128, 440, 88, 18, 34   # 2× pixels


def font(pattern):
    return sp.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True).stdout.strip()


MEDIUM, SEMI = font("Inter:style=Medium"), font("Inter:style=SemiBold")


def magick(*args):
    sp.run(["magick", *map(str, args)], check=True)


def size(path):
    w, h = sp.run(["magick", "identify", "-format", "%w %h", str(path)],
                  capture_output=True, text=True, check=True).stdout.split()
    return int(w), int(h)


def chip(tmp, slug, name, fg, fill, edge):
    icon, text, out = tmp / f"{slug}-i.png", tmp / f"{slug}-t.png", tmp / f"{slug}.png"
    magick("-background", "none", "-density", 600, HERE / "icons" / f"{slug}.svg", "-resize", "40x40",
           "-fill", fg, "-colorize", 100, icon)
    magick("-background", "none", "-fill", fg, "-font", MEDIUM, "-pointsize", 36, f"label:{name}", text)
    tw, th = size(text)
    w = 30 + 40 + 16 + tw + 34
    magick("-size", f"{w}x{CHIP_H}", "xc:none", "-fill", fill, "-stroke", edge, "-strokewidth", 2,
           "-draw", f"roundrectangle 1,1 {w - 2},{CHIP_H - 2} {CHIP_H // 2},{CHIP_H // 2}",
           icon, "-geometry", f"+30+{(CHIP_H - 40) // 2}", "-composite",
           text, "-geometry", f"+{30 + 40 + 16}+{(CHIP_H - th) // 2}", "-composite", out)
    return out, w


def render(theme):
    bg, fg, label_col, fill, chip_edge, card_edge = THEMES[theme]
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        placed, y = [], PAD - 24
        for title, items in GROUPS:
            lab = tmp / f"label-{len(placed)}.png"
            magick("-background", "none", "-fill", label_col, "-font", SEMI, "-pointsize", 36, f"label:{title}", lab)
            placed.append((lab, PAD, y + (CHIP_H - size(lab)[1]) // 2))
            x = PAD + LABEL_W
            for slug, name in items:
                img, w = chip(tmp, slug, name, fg, fill, chip_edge)
                if x + w > W - PAD:                      # wrap within the card
                    x, y = PAD + LABEL_W, y + CHIP_H + GAP
                placed.append((img, x, y))
                x += w + GAP
            y += CHIP_H + ROW_GAP + 26
        H = y - ROW_GAP - 26 + PAD - 24
        args = ["-size", f"{W}x{H}", "xc:none", "-fill", bg, "-stroke", card_edge, "-strokewidth", 2,
                "-draw", f"roundrectangle 1,1 {W - 2},{H - 2} 48,48"]
        for img, x, y in placed:
            args += [img, "-geometry", f"+{x}+{y}", "-composite"]
        magick(*args, "-strip", HERE / f"toolbox-{theme}.png")


if __name__ == "__main__":
    for theme in THEMES:
        render(theme)
    print("✓ toolbox-light.png, toolbox-dark.png")
