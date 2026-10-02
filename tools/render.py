"""Rendu des visuels Lucide (LinkedIn PNG + Instagram JPEG, 1080x1350, ratio 4:5).

Usage : python3 tools/render.py posts/<dossier>/spec.json
Produit linkedin.png et instagram.jpg dans le même dossier.

spec.json :
{
  "pill": "NOUVEAU",                 # badge encadré (optionnel, "" pour aucun)
  "eyebrow": "OUTIL GRATUIT",        # sur-titre vert en majuscules
  "title": "Votre portefeuille<br>mérite quelle <em>note</em>&nbsp;?",  # <em> = mot en vert
  "title_size": 82,                  # optionnel (64 à 96 selon longueur)
  "middle_html": "...",              # bloc central libre (voir classes CSS ci-dessous)
  "chips": ["<b>30 s</b> chrono", "<b>Gratuit</b>"],   # optionnel
  "cta": "Faire le test &rarr; lucide.finance",
  "alt": "texte alternatif"          # utilisé par le post, pas par le rendu
}

Classes CSS disponibles pour middle_html :
  .card            panneau arrondi (fond #0F2036, bordure #1C3550), flex horizontal
  .card.col        même panneau en colonne
  .gauge + svg     jauge circulaire (voir gauge_svg dans ce fichier pour le motif)
  .rows/.row/.t    liste à puces avec check() ; .t = sous-titre vert majuscules
  .stat            grand chiffre (.stat .n = nombre, .stat .l = libellé)
  .quote           citation en grand, guillemets verts
  .vs              comparaison deux colonnes (.vs .a / .vs .b, .vs .k = label)
  .muted / .green  couleurs de texte
  {CHECK}          remplacé par l'icône check verte
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

C = {
    "bg": "#0A1628", "panel": "#0F2036", "line": "#1C3550", "green": "#1D9E75",
    "green_dark": "#0F6E56", "green_light": "#5DCAA5", "white": "#FFFFFF",
    "muted": "#A9B6C8", "dim": "#5B6B85",
}


def logo(size):
    return (f'<svg viewBox="0 0 100 100" width="{size}" height="{size}">'
            f'<rect x="17" y="17" width="66" height="66" transform="rotate(45 50 50)" fill="none" stroke="{C["green_dark"]}" stroke-width="4"/>'
            f'<rect x="31" y="31" width="38" height="38" transform="rotate(45 50 50)" fill="none" stroke="{C["green"]}" stroke-width="3"/>'
            f'<circle cx="50" cy="50" r="8" fill="{C["green"]}"/></svg>')


CHECK = (f'<svg width="34" height="34" viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="{C["green_dark"]}"/>'
         '<path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

DECO = ('<svg class="deco" viewBox="0 0 400 400" width="560" height="560">'
        '<rect x="58" y="58" width="284" height="284" transform="rotate(45 200 200)" fill="none" stroke="#123a44" stroke-width="2"/>'
        '<rect x="108" y="108" width="184" height="184" transform="rotate(45 200 200)" fill="none" stroke="#123a44" stroke-width="2"/>'
        '<rect x="150" y="150" width="100" height="100" transform="rotate(45 200 200)" fill="none" stroke="#10303a" stroke-width="1.5"/></svg>')


def gauge_svg(label="?", sub="/ 100", pct=0.7):
    """Jauge circulaire ; pct = part remplie (0-1)."""
    off = round(565 * (1 - pct))
    return (f'<div class="gauge"><svg width="210" height="210" viewBox="0 0 210 210">'
            f'<circle cx="105" cy="105" r="90" fill="none" stroke="{C["line"]}" stroke-width="16"/>'
            f'<circle cx="105" cy="105" r="90" fill="none" stroke="{C["green"]}" stroke-width="16" stroke-linecap="round" '
            f'stroke-dasharray="565" stroke-dashoffset="{off}" transform="rotate(-90 105 105)" opacity=".9"/></svg>'
            f'<div class="v"><div class="q">{label}</div><div class="s">{sub}</div></div></div>')


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:{C['bg']};font-family:Inter,sans-serif;color:#fff;position:relative;overflow:hidden}}
.wrap{{position:absolute;inset:90px 90px 80px 90px;display:flex;flex-direction:column}}
.eyebrow{{display:flex;align-items:center;gap:26px;color:{C['green_light']};font-size:27px;font-weight:600;letter-spacing:1.5px}}
.pill{{border:2px solid {C['green']};border-radius:999px;padding:8px 20px;font-size:22px;letter-spacing:2px}}
h1{{font-family:'Inter Display',Inter,sans-serif;font-weight:800;line-height:1.05;letter-spacing:-2px;margin-top:56px}}
h1 em,.green{{font-style:normal;color:{C['green']}}}
.muted{{color:{C['muted']}}}
.rule{{width:90px;height:6px;background:{C['green']};border-radius:3px;margin:40px 0 0}}
.mid{{margin-top:50px}}
.card{{background:{C['panel']};border:2px solid {C['line']};border-radius:28px;padding:40px 44px;display:flex;gap:44px;align-items:center}}
.card.col{{flex-direction:column;align-items:flex-start;gap:22px}}
.gauge{{position:relative;width:210px;height:210px;flex:none}}
.gauge .v{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}}
.gauge .q{{font-family:'Inter Display';font-size:92px;font-weight:800;line-height:1}}
.gauge .s{{font-size:26px;color:{C['muted']};margin-top:4px}}
.rows{{display:flex;flex-direction:column;gap:22px}}
.t{{font-size:22px;letter-spacing:2px;color:{C['green_light']};font-weight:600;margin-bottom:4px}}
.row{{display:flex;align-items:center;gap:18px;font-size:29px;font-weight:500;color:#E6ECF4}}
.stat .n{{font-family:'Inter Display';font-size:120px;font-weight:800;line-height:1;color:{C['green']}}}
.stat .l{{font-size:30px;color:#E6ECF4;margin-top:10px;line-height:1.3}}
.quote{{font-size:44px;font-weight:600;line-height:1.3;color:#E6ECF4}}
.quote:before{{content:'« ';color:{C['green']}}} .quote:after{{content:' »';color:{C['green']}}}
.vs{{display:flex;gap:24px;width:100%}}
.vs>div{{flex:1;background:{C['panel']};border:2px solid {C['line']};border-radius:24px;padding:32px;font-size:28px;line-height:1.35;color:#E6ECF4}}
.vs .b{{border-color:{C['green']}}}
.vs .k{{font-size:22px;letter-spacing:2px;font-weight:600;margin-bottom:14px;color:{C['muted']}}}
.vs .b .k{{color:{C['green_light']}}}
.chips{{display:flex;gap:16px;margin-top:40px;flex-wrap:wrap}}
.chip{{background:#11283f;border:1.5px solid {C['line']};border-radius:999px;padding:12px 24px;font-size:25px;color:{C['muted']};font-weight:500}}
.chip b{{color:#fff;font-weight:600}}
.cta{{margin-top:44px;align-self:flex-start;border:2px solid {C['green']};background:rgba(29,158,117,.12);color:{C['green_light']};border-radius:16px;padding:20px 32px;font-size:31px;font-weight:600}}
.foot{{margin-top:auto}}
.brand{{display:flex;align-items:center;gap:20px}}
.brand .n{{font-size:38px;font-weight:700;letter-spacing:1px}}
.tag{{color:{C['green_light']};font-size:20px;letter-spacing:2px;margin-top:6px}}
.handle{{color:{C['muted']};font-size:22px;font-weight:600;margin-top:14px}}
.disc{{color:{C['dim']};font-size:18px;margin-top:10px}}
.deco{{position:absolute;right:-150px;top:880px;opacity:.9}}
"""


def build_html(spec):
    pill = f'<span class="pill">{spec["pill"]}</span>' if spec.get("pill") else ""
    chips = "".join(f'<span class="chip">{c}</span>' for c in spec.get("chips", []))
    chips_html = f'<div class="chips">{chips}</div>' if chips else ""
    cta = f'<div class="cta">{spec["cta"]}</div>' if spec.get("cta") else ""
    middle = spec.get("middle_html", "").replace("{CHECK}", CHECK)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
{DECO}
<div class="wrap">
  <div class="eyebrow">{logo(78)}{pill}<span>{spec.get('eyebrow', '')}</span></div>
  <h1 style="font-size:{spec.get('title_size', 82)}px">{spec['title']}</h1>
  <div class="rule"></div>
  <div class="mid">{middle}</div>
  {chips_html}
  {cta}
  <div class="foot">
    <div class="brand">{logo(58)}<span class="n">LUCIDE</span></div>
    <div class="tag">ANALYSE · DÉCISION · CLARTÉ</div>
    <div class="handle">@lucide.finance · lucide.finance</div>
    <div class="disc">Contenu informatif · ne constitue pas un conseil en investissement.</div>
  </div>
</div></body></html>"""


def render(spec_path):
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = spec_path.parent
    html = build_html(spec)
    (out / "visual.html").write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.set_content(html)
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(out / "linkedin.png"))
        pg.screenshot(path=str(out / "instagram.jpg"), type="jpeg", quality=92)
        b.close()
    print(out / "linkedin.png", out / "instagram.jpg")


if __name__ == "__main__":
    render(sys.argv[1])
