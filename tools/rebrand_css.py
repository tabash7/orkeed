"""One-time palette transformation for the Orkeed site."""

from pathlib import Path

path = Path(__file__).resolve().parents[1] / "styles.css"
css = path.read_text(encoding="utf-8")
palette = {
    "#142d35": "#291f36",
    "#1b4047": "#3d2b49",
    "#21363d": "#342d3c",
    "#5b7072": "#6c6171",
    "#65b9a9": "#bc8eae",
    "#a5e1d5": "#ead1e0",
    "#f4efe6": "#fbf8f5",
    "#d5e0db": "#e6dfe8",
    "#2f6a70": "#69516f",
    "#1b454c": "#3b2b4a",
    "#2c6669": "#684c68",
    "#285d63": "#614665",
    "#214a50": "#503950",
    "#10272e": "#21192d",
    "#317f76": "#775070",
    "#276e66": "#714669",
    "#398f83": "#a36b95",
    "#74c7b8": "#d9b4ca",
    "#e6efea": "#f3edf2",
    "#f3f4ef": "#f8f4f7",
    "#bbd8d0": "#dfcad9",
    "#f1f7f4": "#fbf7fa",
    "#3b7770": "#805978",
    "#175e57": "#694260",
    "#526d6c": "#6d5b6d",
    "#f5f1e8": "#fbf8f5",
    "#e9d6b0": "#d8c28b",
    "#376b6b": "#69506d",
    "#d2deeb": "#e8dfe9",
    "#d3dfeb": "#e8dfe9",
}
for old, new in palette.items():
    css = css.replace(old, new)
css += """

/* Orkeed's visual system: orchid geometry, soft ivory, and restrained pink. */
.brand img,.footer-brand img{background:#291f36;border-radius:14px}
.hero{background:radial-gradient(circle at 19% 35%,#624d69 0,#3c2d49 42%,#291f36 80%)}
.hero:before{border-color:rgba(217,180,202,.18)}
.hero-pattern{background:radial-gradient(circle at 74% 39%,rgba(217,180,202,.1) 0 20%,transparent 21%),repeating-radial-gradient(circle at 70% 48%,transparent 0 56px,rgba(234,209,224,.042) 57px 58px)}
.hero-visual-frame{background:rgba(255,255,255,.025);border-color:rgba(217,180,202,.48);border-radius:140px 140px 28px 28px;box-shadow:0 28px 75px rgba(15,8,20,.22)}
.hero-visual-frame img{border-radius:120px 120px 18px 18px;background:#291f36}
.button-gold{background:#ead1e0;color:#291f36;border-radius:24px 5px 24px 5px}
.button-gold:hover{background:#fbf8f5}
.nav-contact,.button-outline{border-radius:20px 4px 20px 4px}
.blog-card{border-right-color:#bc8eae;border-radius:16px 4px 16px 4px}
.banner-frame{border-radius:24px 5px 24px 5px}
.article-featured{border-radius:18px 4px 18px 4px}
.blog-landing-hero,.article-hero{background:radial-gradient(circle at 14% 34%,#624d69,#291f36 69%)}
.contact{background:#f3edf2}
"""
path.write_text(css, encoding="utf-8")
print("Applied Orkeed palette")
