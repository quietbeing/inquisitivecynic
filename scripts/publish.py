#!/usr/bin/env python3
"""
publish.py — Reads Notion pages and generates index.html for inquisitivecynic.com

Notion Page IDs (under the InquisitiveCynic.com hub):
  Home:            34302389-b9e8-810f-8c9e-d44f99d1c6a0
  About:           34302389-b9e8-814a-a54d-e15d08c8df90
  Focus Areas:     34302389-b9e8-81eb-95bf-ff463e250fec
  Field Notes:     34302389-b9e8-81e7-8deb-f049cb115a06
  Connect:         34302389-b9e8-8184-be7a-c971d9c8283c
  Credential Band: 34302389-b9e8-813a-9304-c61d5ec7b3c9

Usage:
  export NOTION_TOKEN="your_notion_integration_token"
  python scripts/publish.py
"""

import os
import re
import json
import requests

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_VERSION = "2022-06-28"

PAGES = {
    "home":       "34302389-b9e8-810f-8c9e-d44f99d1c6a0",
    "about":      "34302389-b9e8-814a-a54d-e15d08c8df90",
    "focus":      "34302389-b9e8-81eb-95bf-ff463e250fec",
    "notes":      "34302389-b9e8-81e7-8deb-f049cb115a06",
    "connect":    "34302389-b9e8-8184-be7a-c971d9c8283c",
    "cred_band":  "34302389-b9e8-813a-9304-c61d5ec7b3c9",
}

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
}


def get_blocks(page_id):
    """Fetch all blocks from a Notion page."""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["results"]


def extract_text(block):
    """Extract plain text from a block's rich_text array."""
    block_type = block["type"]
    rich = block.get(block_type, {}).get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in rich).strip()


def parse_sections(blocks):
    """Parse blocks into a dict keyed by heading text -> content text."""
    sections = {}
    current_key = None
    current_lines = []

    for block in blocks:
        btype = block["type"]

        if btype in ("heading_2", "heading_3"):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = extract_text(block)
            current_lines = []
        elif btype == "paragraph":
            text = extract_text(block)
            if text:
                current_lines.append(text)
        elif btype == "divider":
            continue

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def esc(text):
    """HTML-escape text."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_html(data):
    """Build the full index.html from parsed Notion data."""

    home = data["home"]
    about = data["about"]
    focus = data["focus"]
    notes = data["notes"]
    connect = data["connect"]
    cred = data["cred_band"]

    # ── Credential band items
    cred_items_raw = cred.get("Items", "").split("\n")
    cred_items = [i.strip() for i in cred_items_raw if i.strip()]
    cred_html = '\n        <span class="cred-sep" aria-hidden="true">&#9670;</span>\n'.join(
        f'        <span>{esc(item)}</span>' for item in cred_items
    )

    # ── Focus cards
    focus_cards = []
    for num, roman in [("I", "I"), ("II", "II"), ("III", "III")]:
        title = focus.get(f"Focus {num}: Title", "")
        desc = focus.get(f"Focus {num}: Description", "")
        tags_raw = focus.get(f"Focus {num}: Tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        tags_html = "\n".join(f'              <span>{esc(t)}</span>' for t in tags)

        featured = ' focus-card--featured' if num == "I" else ''
        card = f"""          <article class="focus-card{featured}">
            <div class="focus-card-number" aria-hidden="true">{roman}</div>
            <h3>{esc(title)}</h3>
            <p>
              {esc(desc)}
            </p>
            <div class="focus-card-tags">
{tags_html}
            </div>
          </article>"""
        focus_cards.append(card)

    focus_html = "\n\n".join(focus_cards)

    # ── Field Notes cards
    note_cards = []
    note_num = 1
    while f"Note {note_num}: Title" in notes:
        cat = notes.get(f"Note {note_num}: Category", "")
        date = notes.get(f"Note {note_num}: Date", "")
        title = notes.get(f"Note {note_num}: Title", "")
        excerpt = notes.get(f"Note {note_num}: Excerpt", "")
        status = notes.get(f"Note {note_num}: Status", "Forthcoming")

        large = ' note-card--large' if note_num == 1 else ''
        card = f"""          <article class="note-card{large}">
            <div class="note-meta">
              <span class="note-category">{esc(cat)}</span>
              <span class="note-date">{esc(date)}</span>
            </div>
            <h3 class="note-title">{esc(title)}</h3>
            <p class="note-excerpt">
              {esc(excerpt)}
            </p>
            <span class="note-cta-hint">{esc(status)}</span>
          </article>"""
        note_cards.append(card)
        note_num += 1

    notes_html = "\n\n".join(note_cards)

    # ── About paragraphs
    about_p1 = about.get("Paragraph 1", "")
    about_p2 = about.get("Paragraph 2", "")
    about_extra_paragraphs = ""
    p_num = 3
    while f"Paragraph {p_num}" in about:
        about_extra_paragraphs += f'\n          <p>\n            {esc(about[f"Paragraph {p_num}"])}\n          </p>'
        p_num += 1

    # ── Build full HTML
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>The InquisitiveCynic &mdash; Paul Reeves</title>
  <meta name="description" content="AI research, Machine Learning, and the real-world context of parking, transportation, and fleet operations. A personal brand by Paul Reeves." />
  <meta property="og:title" content="The InquisitiveCynic &mdash; Paul Reeves" />
  <meta property="og:description" content="Asking better questions." />
  <meta property="og:url" content="https://inquisitivecynic.com" />
  <meta property="og:type" content="website" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500;1,600&family=EB+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Cormorant+SC:wght@300;400;500&display=swap" rel="stylesheet" />
  <link rel="icon" href="images/favicon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="css/style.css" />
</head>
<body>

  <header class="site-header" id="top">
    <div class="header-inner">
      <a href="#top" class="logo-link" aria-label="The InquisitiveCynic home">
        <div class="logo-wordmark">
          <span class="logo-the">The</span>
          <span class="logo-name">InquisitiveCynic</span>
        </div>
      </a>
      <nav class="site-nav" role="navigation" aria-label="Main navigation">
        <a href="#about">About</a>
        <a href="#focus">Focus</a>
        <a href="#field-notes">Field Notes</a>
        <a href="#connect">Connect</a>
      </nav>
      <button class="theme-toggle" data-theme-toggle aria-label="Switch to dark mode">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </header>

  <main>

    <section class="hero" aria-labelledby="hero-heading">
      <div class="invitation-wrapper">

        <div class="inv-rule" aria-hidden="true">
          <span class="inv-rule-line"></span>
          <svg class="inv-diamond" viewBox="0 0 16 16" fill="currentColor"><polygon points="8,0 16,8 8,16 0,8"/></svg>
          <span class="inv-rule-line"></span>
        </div>

        <h1 id="hero-heading" class="inv-title">
          The InquisitiveCynic
        </h1>

        <p class="inv-subtitle">{esc(home.get("Tagline", "Asking better questions."))}</p>

        <div class="inv-divider" aria-hidden="true">
          <span class="inv-divider-dot"></span>
          <span class="inv-divider-dot"></span>
          <span class="inv-divider-dot"></span>
        </div>

        <p class="inv-body">
          {esc(home.get("Name", "Paul Reeves"))}
        </p>

        <p class="inv-context">
          {esc(home.get("Context Line", ""))}
        </p>

        <div class="inv-rule inv-rule--bottom" aria-hidden="true">
          <span class="inv-rule-line"></span>
          <svg class="inv-diamond" viewBox="0 0 16 16" fill="currentColor"><polygon points="8,0 16,8 8,16 0,8"/></svg>
          <span class="inv-rule-line"></span>
        </div>

        <a href="#about" class="inv-cta">
          Enter
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
        </a>

      </div>
    </section>

    <div class="credential-band" aria-label="Credentials">
      <div class="credential-band-inner">
{cred_html}
      </div>
    </div>

    <section class="section about" id="about" aria-labelledby="about-heading">
      <div class="section-inner section-inner--asymmetric">

        <div class="about-text">
          <p class="section-eyebrow">The Perspective</p>
          <h2 id="about-heading">{esc(about.get("Heading", ""))}</h2>
          <p class="about-lead">
            {esc(about.get("Lead", ""))}
          </p>
          <p>
            {esc(about_p1)}
          </p>
          <p>
            {esc(about_p2)}
          </p>{about_extra_paragraphs}
          <a href="#focus" class="text-link">Explore the focus areas &rarr;</a>
        </div>

        <div class="about-accent" aria-hidden="true">
          <div class="about-card">
            <p class="about-card-quote">
              &ldquo;{esc(about.get("Quote", ""))}&rdquo;
            </p>
            <p class="about-card-attr">&mdash; {esc(about.get("Quote Attribution", ""))}</p>
            <div class="about-card-rule"></div>
            <p class="about-card-tagline">{esc(about.get("Quote Tagline", ""))}</p>
          </div>
        </div>

      </div>
    </section>

    <section class="section focus" id="focus" aria-labelledby="focus-heading">
      <div class="section-inner">
        <p class="section-eyebrow">The Work</p>
        <h2 id="focus-heading">Three Lenses, One Discipline</h2>

        <div class="focus-grid">

{focus_html}

        </div>
      </div>
    </section>

    <section class="section field-notes" id="field-notes" aria-labelledby="field-notes-heading">
      <div class="section-inner">
        <p class="section-eyebrow">The Dispatch</p>
        <h2 id="field-notes-heading">Field Notes</h2>
        <p class="section-subtitle">Observations from the intersection of data, operations, and applied intelligence.</p>

        <div class="notes-grid">

{notes_html}

        </div>
      </div>
    </section>

    <section class="section connect" id="connect" aria-labelledby="connect-heading">
      <div class="section-inner">
        <div class="connect-inner">
          <div class="inv-rule inv-rule--sm" aria-hidden="true">
            <span class="inv-rule-line"></span>
            <svg class="inv-diamond inv-diamond--sm" viewBox="0 0 16 16" fill="currentColor"><polygon points="8,0 16,8 8,16 0,8"/></svg>
            <span class="inv-rule-line"></span>
          </div>

          <p class="section-eyebrow" id="connect-heading">The Introduction</p>
          <h2>{esc(connect.get("Heading", ""))}</h2>
          <p class="connect-body">
            {esc(connect.get("Body", ""))}
          </p>

          <div class="connect-actions">
            <a href="mailto:{esc(connect.get("Email", "paul@inquisitivecynic.com"))}" class="btn-primary">
              {esc(connect.get("Button Text", "Write to Paul"))}
            </a>
          </div>

          <div class="inv-rule inv-rule--sm inv-rule--bottom" aria-hidden="true">
            <span class="inv-rule-line"></span>
            <svg class="inv-diamond inv-diamond--sm" viewBox="0 0 16 16" fill="currentColor"><polygon points="8,0 16,8 8,16 0,8"/></svg>
            <span class="inv-rule-line"></span>
          </div>
        </div>
      </div>
    </section>

  </main>

  <footer class="site-footer" role="contentinfo">
    <div class="footer-inner">
      <div class="footer-pillars">
        <span class="footer-pillar">Applied AI Research</span>
        <span class="footer-pillar-sep" aria-hidden="true">&middot;</span>
        <span class="footer-pillar">Machine Learning</span>
        <span class="footer-pillar-sep" aria-hidden="true">&middot;</span>
        <span class="footer-pillar">Professional Intelligence</span>
      </div>
      <p class="footer-sub">Paul Reeves &middot; <a href="mailto:paul@inquisitivecynic.com">paul@inquisitivecynic.com</a></p>
      <p class="footer-copy">&copy; 2026 Paul Reeves. All rights reserved.</p>
    </div>
  </footer>

  <script src="js/main.js"></script>
</body>
</html>"""
    return html


def main():
    print("Fetching Notion pages...")
    data = {}
    for key, page_id in PAGES.items():
        blocks = get_blocks(page_id)
        data[key] = parse_sections(blocks)
        print(f"  {key}: {len(data[key])} sections")

    print("Generating index.html...")
    html = build_html(data)

    with open("index.html", "w") as f:
        f.write(html)

    print(f"Done — wrote {len(html):,} bytes to index.html")


if __name__ == "__main__":
    main()
