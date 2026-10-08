#!/usr/bin/env python3
"""Render assets/toolbox-light.png and assets/toolbox-dark.png: the "Toolbox" card of the profile.

Grouped rows of pill chips (monochrome icon + name), in the same palette and card as the banner.
Icons are Simple Icons (CC0) in assets/icons/ (None = text-only chip); type is Inter.
Edit GROUPS and run:  python3 assets/toolbox.py
"""
import subprocess as sp
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GROUPS = [
    ("Data", [("googlebigquery", "BigQuery"), ("dbt", "dbt"), ("googlecloud", "Google Cloud"),
              ("postgresql", "Postgres"), ("duckdb", "DuckDB"), ("python", "Python"), ("pandas", "pandas"),
              ("jupyter", "Jupyter"), ("looker", "Looker Studio")]),
    ("Web & apps", [("typescript", "TypeScript"), ("javascript", "JavaScript"), ("react", "React"),
                    ("nextdotjs", "Next.js"), ("vuedotjs", "Vue"), ("astro", "Astro"), ("bun", "Bun"),
                    ("nodedotjs", "Node.js"), ("vite", "Vite"), ("tailwindcss", "Tailwind"), ("mdx", "MDX"),
                    ("swift", "Swift"), ("xcode", "Xcode")]),
    ("Cloud & backend", [("supabase", "Supabase"), (None, "PostgREST"), ("vercel", "Vercel"),
                         ("cloudflare", "Cloudflare"), ("stripe", "Stripe"), ("postman", "Postman"),
                         ("ethereum", "Ethereum"), ("solana", "Solana")]),
    ("AI", [("claude", "Claude Code"), ("modelcontextprotocol", "MCP"), ("cursor", "Cursor"),
            ("openai", "OpenAI"), ("huggingface", "Hugging Face"), ("ollama", "Ollama")]),
    ("Home lab & desktop", [("docker", "Docker"), ("debian", "Debian"), ("linux", "Linux"),
                            ("tailscale", "Tailscale"), ("nvidia", "CUDA"), ("i3", "i3"), ("zsh", "zsh"),
                            ("gnubash", "Bash"), ("git", "Git"), ("githubactions", "GitHub Actions")]),
    ("Product & GTM", [("figma", "Figma"), ("linear", "Linear"), ("notion", "Notion"), (None, "Clay"),
                       ("hubspot", "HubSpot")]),
]
THEMES = {  # bg, chip text, label, chip fill, chip edge, card edge, divider
    "light": ("#fbfbfd", "#1d1d1f", "#86868b", "#f0f0f3", "#0000000f", "#0000001a", "#00000012"),
    "dark":  ("#000000", "#f5f5f7", "#86868b", "#161618", "#ffffff14", "#ffffff1f", "#ffffff14"),
}
# 2× pixels: card width, padding, label column, chip height, gaps
W, PAD_X, PAD_Y, LABEL_W, CHIP_H, GAP, GROUP_GAP = 2560, 128, 112, 470, 84, 16, 76


def font(pattern):
    return sp.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True).stdout.strip()


MEDIUM, SEMI = font("Inter:style=Medium"), font("Inter:style=SemiBold")


def magick(*args):
    sp.run(["magick", *map(str, args)], check=True)


def size(path):
    w, h = sp.run(["magick", "identify", "-format", "%w %h", str(path)],
                  capture_output=True, text=True, check=True).stdout.split()
    return int(w), int(h)


def chip(tmp, n, slug, name, fg, fill, edge):
    text, out = tmp / f"c{n}-t.png", tmp / f"c{n}.png"
    magick("-background", "none", "-fill", fg, "-font", MEDIUM, "-pointsize", 34, f"label:{name}", text)
    tw, th = size(text)
    lead = 30 + (38 + 14 if slug else 0)
    w = lead + tw + 32
    args = ["-size", f"{w}x{CHIP_H}", "xc:none", "-fill", fill, "-stroke", edge, "-strokewidth", 2,
            "-draw", f"roundrectangle 1,1 {w - 2},{CHIP_H - 2} {CHIP_H // 2},{CHIP_H // 2}"]
    if slug:
        icon = tmp / f"c{n}-i.png"
        magick("-background", "none", "-density", 600, HERE / "icons" / f"{slug}.svg", "-resize", "38x38",
               "-fill", fg, "-colorize", 100, icon)
        args += [icon, "-geometry", f"+30+{(CHIP_H - 38) // 2}", "-composite"]
    magick(*args, text, "-geometry", f"+{lead}+{(CHIP_H - th) // 2}", "-composite", out)
    return out, w


def render(theme):
    bg, fg, label_col, fill, chip_edge, card_edge, divider = THEMES[theme]
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        placed, dividers, y, n = [], [], PAD_Y, 0
        for gi, (title, items) in enumerate(GROUPS):
            if gi:
                dividers.append(y - GROUP_GAP // 2)
            lab = tmp / f"label-{gi}.png"
            magick("-background", "none", "-fill", label_col, "-font", SEMI, "-pointsize", 34, f"label:{title}", lab)
            placed.append((lab, PAD_X, y + (CHIP_H - size(lab)[1]) // 2))
            x = PAD_X + LABEL_W
            for slug, name in items:
                n += 1
                img, w = chip(tmp, n, slug, name, fg, fill, chip_edge)
                if x + w > W - PAD_X:                    # wrap within the card
                    x, y = PAD_X + LABEL_W, y + CHIP_H + GAP
                placed.append((img, x, y))
                x += w + GAP
            y += CHIP_H + GROUP_GAP
        H = y - GROUP_GAP + PAD_Y
        args = ["-size", f"{W}x{H}", "xc:none", "-fill", bg, "-stroke", card_edge, "-strokewidth", 2,
                "-draw", f"roundrectangle 1,1 {W - 2},{H - 2} 48,48", "-stroke", "none", "-fill", divider]
        for dy in dividers:
            args += ["-draw", f"rectangle {PAD_X},{dy} {W - PAD_X},{dy + 1}"]
        for img, x, y in placed:
            args += [img, "-geometry", f"+{x}+{y}", "-composite"]
        magick(*args, "-strip", HERE / f"toolbox-{theme}.png")


if __name__ == "__main__":
    for theme in THEMES:
        render(theme)
    print("✓ toolbox-light.png, toolbox-dark.png")
