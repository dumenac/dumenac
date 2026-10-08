#!/usr/bin/env python3
"""Render the profile's two toolbox cards — assets/toolbox-{build,operate}-{light,dark}.png.

Grouped rows of pill chips (monochrome icon + name), in the same palette and card as the banner.
Icons are Simple Icons (CC0) in assets/icons/ (None = text-only chip); type is Inter.
Edit CARDS and run:  python3 assets/toolbox.py
"""
import subprocess as sp
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARDS = {
    # what I build with — kept to what I actually use
    "build": [
        ("Data", [("googlebigquery", "BigQuery"), ("dbt", "dbt"), ("postgresql", "Postgres"), ("duckdb", "DuckDB"),
                  ("pandas", "pandas"), ("numpy", "NumPy"), ("jupyter", "Jupyter"), ("looker", "Looker Studio")]),
        ("Backend", [("python", "Python"), ("django", "Django"), ("fastapi", "FastAPI"), ("flask", "Flask"),
                     ("sqlalchemy", "SQLAlchemy"), ("nodedotjs", "Node.js"), ("express", "Express"), ("bun", "Bun"),
                     ("graphql", "GraphQL"), ("swagger", "OpenAPI"), ("prisma", "Prisma"), ("redis", "Redis"),
                     ("mysql", "MySQL"), ("mongodb", "MongoDB"), ("sqlite", "SQLite"), ("supabase", "Supabase"),
                     ("firebase", "Firebase"), (None, "PostgREST"), ("stripe", "Stripe"), ("postman", "Postman")]),
        ("Web & apps", [("typescript", "TypeScript"), ("javascript", "JavaScript"), ("react", "React"),
                        ("nextdotjs", "Next.js"), ("vuedotjs", "Vue"), ("nuxtdotjs", "Nuxt"), ("astro", "Astro"),
                        ("tailwindcss", "Tailwind"), ("shadcnui", "shadcn/ui"), ("vite", "Vite"), ("mdx", "MDX"),
                        ("html5", "HTML"), ("css3", "CSS"), ("swift", "Swift"), (None, "SwiftUI"), ("xcode", "Xcode")]),
        ("Cloud & DevOps", [("googlecloud", "Google Cloud"), ("amazonaws", "AWS"), ("vercel", "Vercel"),
                            ("cloudflare", "Cloudflare"), ("docker", "Docker"), ("githubactions", "GitHub Actions"),
                            ("nginx", "Nginx"), ("sentry", "Sentry")]),
        ("AI", [("claude", "Claude Code"), ("anthropic", "Anthropic API"), ("modelcontextprotocol", "MCP"),
                ("openai", "OpenAI"), ("cursor", "Cursor"), ("huggingface", "Hugging Face"), ("ollama", "Ollama")]),
        ("Web3", [("ethereum", "Ethereum"), ("solana", "Solana"), ("polygon", "Polygon"), (None, "Base"),
                  ("solidity", "Solidity")]),
        ("Home lab & desktop", [("debian", "Debian"), ("ubuntu", "Ubuntu"), ("linux", "Linux"),
                                ("tailscale", "Tailscale"), ("nvidia", "CUDA"), ("i3", "i3"), ("zsh", "zsh"),
                                ("gnubash", "Bash"), ("git", "Git"), ("visualstudiocode", "VS Code"),
                                ("sublimetext", "Sublime Text")]),
    ],
    # what I operate with — product, go-to-market, growth
    "operate": [
        ("Product", [("figma", "Figma"), ("linear", "Linear"), ("notion", "Notion"), ("jira", "Jira"),
                     ("miro", "Miro"), ("loom", "Loom"), ("posthog", "PostHog"), ("mixpanel", "Mixpanel"),
                     (None, "Amplitude"), ("hotjar", "Hotjar"), ("googleanalytics", "Google Analytics"),
                     ("typeform", "Typeform"), (None, "Tally")]),
        ("Go-to-market", [(None, "Clay"), (None, "Apollo"), ("hubspot", "HubSpot"), ("salesforce", "Salesforce"),
                          (None, "Attio"), (None, "Pipedrive"), (None, "Gong"), (None, "Lemlist"),
                          (None, "Instantly"), (None, "Sales Navigator"), ("intercom", "Intercom"),
                          ("zendesk", "Zendesk"), (None, "Customer.io"), ("mailchimp", "Mailchimp"),
                          (None, "Segment"), ("calendly", "Calendly"), ("docusign", "DocuSign"), (None, "Dune")]),
        ("Growth & content", [("webflow", "Webflow"), ("framer", "Framer"), ("ghost", "Ghost"),
                              ("substack", "Substack"), ("googleads", "Google Ads"), ("meta", "Meta Ads"),
                              ("semrush", "Semrush"), (None, "Ahrefs"), ("producthunt", "Product Hunt"),
                              ("x", "X"), (None, "LinkedIn"), ("youtube", "YouTube"), ("canva", "Canva"),
                              (None, "Gamma")]),
        ("Ops & comms", [("zapier", "Zapier"), ("make", "Make"), ("n8n", "n8n"), ("airtable", "Airtable"),
                         ("googlesheets", "Google Sheets"), ("googledocs", "Google Docs"),
                         ("googleslides", "Google Slides"), ("slack", "Slack"), ("discord", "Discord"),
                         ("telegram", "Telegram"), ("whatsapp", "WhatsApp"), ("zoom", "Zoom"),
                         ("googlemeet", "Google Meet")]),
    ],
}
THEMES = {  # bg, chip text, label, chip fill, chip edge, card edge, divider
    "light": ("#fbfbfd", "#1d1d1f", "#86868b", "#f0f0f3", "#0000000f", "#0000001a", "#00000012"),
    "dark":  ("#000000", "#f5f5f7", "#86868b", "#161618", "#ffffff14", "#ffffff1f", "#ffffff14"),
}
# 2× pixels: card width, padding, label column, chip height, gaps
W, PAD_X, PAD_Y, LABEL_W, CHIP_H, GAP, GROUP_GAP = 2560, 128, 112, 430, 76, 14, 70


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
    magick("-background", "none", "-fill", fg, "-font", MEDIUM, "-pointsize", 31, f"label:{name}", text)
    tw, th = size(text)
    lead = 26 + (34 + 12 if slug else 0)
    w = lead + tw + 28
    args = ["-size", f"{w}x{CHIP_H}", "xc:none", "-fill", fill, "-stroke", edge, "-strokewidth", 2,
            "-draw", f"roundrectangle 1,1 {w - 2},{CHIP_H - 2} {CHIP_H // 2},{CHIP_H // 2}"]
    if slug:
        icon = tmp / f"c{n}-i.png"
        magick("-background", "none", "-density", 600, HERE / "icons" / f"{slug}.svg", "-resize", "34x34",
               "-fill", fg, "-colorize", 100, icon)
        args += [icon, "-geometry", f"+26+{(CHIP_H - 34) // 2}", "-composite"]
    magick(*args, text, "-geometry", f"+{lead}+{(CHIP_H - th) // 2}", "-composite", out)
    return out, w


def render(card, groups, theme):
    bg, fg, label_col, fill, chip_edge, card_edge, divider = THEMES[theme]
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        placed, dividers, y, n = [], [], PAD_Y, 0
        for gi, (title, items) in enumerate(groups):
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
        magick(*args, "-strip", HERE / f"toolbox-{card}-{theme}.png")


if __name__ == "__main__":
    for card, groups in CARDS.items():
        for theme in THEMES:
            render(card, groups, theme)
    print("✓ toolbox-{build,operate}-{light,dark}.png")
