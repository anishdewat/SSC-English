"""Builds the static site into ./_site.

Layout expected in the repo:
    <Subject_Name>/<NN>.html     e.g. Spellings/02.html
Every top-level folder containing .html files becomes a subject.
"""
import html, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "_site"

CSS = """
:root{--bg:#f6f7fb;--card:#fff;--text:#1c2030;--mut:#6b7185;--acc:#4f46e5;--bd:#e3e5ee}
@media(prefers-color-scheme:dark){:root{--bg:#12141c;--card:#1b1e29;--text:#e8eaf2;--mut:#9aa0b6;--acc:#8b8cf8;--bd:#2b2f3f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,sans-serif}
main{max-width:720px;margin:0 auto;padding:40px 16px}
h1{font-size:1.7rem;margin:0 0 4px}p.sub{color:var(--mut);margin:0 0 28px}
a.back{color:var(--mut);text-decoration:none;font-size:.9rem;display:inline-block;margin-bottom:16px}
.list{display:grid;gap:10px}
.item{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 18px;background:var(--card);
border:1px solid var(--bd);border-radius:12px;color:var(--text);text-decoration:none}
.item:hover{border-color:var(--acc)}.item b{font-weight:600}.item span{color:var(--mut);font-size:.85rem;white-space:nowrap}
"""

BAR = ('<a href="./" style="position:fixed;top:10px;left:10px;z-index:99999;background:#1c2030;color:#fff;'
       'padding:6px 12px;border-radius:999px;font:13px system-ui,sans-serif;text-decoration:none;opacity:.85">'
       '&larr; All lectures</a>')


def page(title, body):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{CSS}</style></head>'
            f'<body><main>{body}</main></body></html>')


def nice(name):
    return name.replace("_", " ").replace("-", " ")


def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def title_of(path, fallback):
    m = re.search(r"<title[^>]*>(.*?)</title>", path.read_text("utf-8", "ignore")[:200000], re.S | re.I)
    return html.unescape(m.group(1).strip()) if m and m.group(1).strip() else fallback


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / ".nojekyll").write_text("")

    subjects = []
    for d in sorted(ROOT.iterdir(), key=lambda p: natural(p.name)):
        if not d.is_dir() or d.name.startswith((".", "_")):
            continue
        files = sorted((f for f in d.glob("*.html") if f.name.lower() != "index.html"), key=lambda p: natural(p.stem))
        if not files:
            continue
        sub_out = OUT / d.name
        sub_out.mkdir()
        rows = []
        for f in files:
            src = f.read_text("utf-8", "ignore")
            src = re.sub(r"</body>", BAR + "</body>", src, count=1, flags=re.I) if re.search(r"</body>", src, re.I) else src + BAR
            (sub_out / f.name).write_text(src, "utf-8")
            t = title_of(f, f.stem)
            rows.append(f'<a class="item" href="{html.escape(f.name)}"><b>{html.escape(t)}</b><span>Lecture {html.escape(f.stem)}</span></a>')
        body = (f'<a class="back" href="../">&larr; All subjects</a><h1>{html.escape(nice(d.name))}</h1>'
                f'<p class="sub">{len(files)} lecture{"s" if len(files) != 1 else ""}</p><div class="list">{"".join(rows)}</div>')
        (sub_out / "index.html").write_text(page(nice(d.name), body), "utf-8")
        subjects.append((d.name, len(files)))

    rows = [f'<a class="item" href="{html.escape(n)}/"><b>{html.escape(nice(n))}</b><span>{c} lecture{"s" if c != 1 else ""}</span></a>'
            for n, c in subjects]
    body = ('<h1>SSC English Notes</h1><p class="sub">Pick a topic</p><div class="list">'
            + ("".join(rows) or "<p>No notes yet.</p>") + "</div>")
    (OUT / "index.html").write_text(page("SSC English Notes", body), "utf-8")
    print(f"Built {len(subjects)} subjects")


main()
