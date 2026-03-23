import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kwadratische Functie Plotter",
    page_icon="📐",
    layout="centered",
)

# ── Custom CSS (light/white theme) ────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: #ffffff; }
  h1, h2, h3 { font-family: 'Space Mono', monospace !important; }

  .title-block {
    background: #f0f4ff;
    border: 1px solid #c7d2fe;
    border-radius: 12px;
    padding: 24px 32px 18px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }
  .title-block::before {
    content: "f(x)";
    position: absolute;
    right: 20px; top: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 72px;
    color: rgba(99,102,241,0.07);
    pointer-events: none;
  }
  .title-block h1 { color: #1e1b4b; margin: 0 0 4px; font-size: 1.5rem; }
  .title-block p  { color: #6366f1; margin: 0; font-size: 0.88rem; }

  .info-card {
    background: #f8faff;
    border: 1px solid #e0e7ff;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.88rem;
  }
  .info-card .label { color: #6366f1; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
  .info-card .value { color: #1e1b4b; font-family: 'Space Mono', monospace; font-size: 0.98rem; margin-top: 3px; }

  .roots-real    { border-left: 3px solid #10b981; }
  .roots-one     { border-left: 3px solid #f59e0b; }
  .roots-complex { border-left: 3px solid #ef4444; }

  .stSlider > div > div > div > div { background: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
  <h1>📐 Kwadratische Functie Plotter</h1>
  <p>Versleep de schuifregelaars om a, b en c aan te passen en de grafiek live te bekijken.</p>
</div>
""", unsafe_allow_html=True)

# ── Sliders ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    a = st.slider("**a** — kwadratisch", min_value=-5.0, max_value=5.0, value=1.0, step=0.1)
with col2:
    b = st.slider("**b** — lineair", min_value=-10.0, max_value=10.0, value=0.0, step=0.1)
with col3:
    c = st.slider("**c** — constant", min_value=-10.0, max_value=10.0, value=0.0, step=0.1)

# ── Equation string builder ───────────────────────────────────────────────────
def build_eq_str(a, b, c):
    def term(coef, var, first=False):
        if coef == 0:
            return ""
        mag = abs(coef)
        mag_str = ("" if mag == 1 and var else
                   (f"{mag:g}" if mag != int(mag) else f"{int(mag)}"))
        if first:
            sign = "−" if coef < 0 else ""
        else:
            sign = " + " if coef > 0 else " − "
        return f"{sign}{mag_str}{var}"

    parts = []
    if a != 0: parts.append(term(a, "x²", first=True))
    if b != 0: parts.append(term(b, "x",  first=(a == 0)))
    if c != 0: parts.append(term(c, "",   first=(a == 0 and b == 0)))
    return "f(x) = " + ("".join(parts) if parts else "0")

eq_label = build_eq_str(a, b, c)

# ── Discriminant & roots ──────────────────────────────────────────────────────
discriminant = b**2 - 4*a*c

if a == 0:
    root_info = ("lineair", None)
else:
    if discriminant > 0:
        r1 = (-b + np.sqrt(discriminant)) / (2*a)
        r2 = (-b - np.sqrt(discriminant)) / (2*a)
        root_info = ("twee_reeel", (r1, r2))
    elif discriminant == 0:
        r1 = -b / (2*a)
        root_info = ("een_reeel", (r1,))
    else:
        real_part = -b / (2*a)
        imag_part = np.sqrt(-discriminant) / (2*a)
        root_info = ("complex", (real_part, imag_part))

kind = root_info[0]

# ── Info cards (Dutch) ────────────────────────────────────────────────────────
ic1, ic2, ic3 = st.columns(3)

with ic1:
    if a != 0:
        vx = -b / (2*a)
        vy = a*vx**2 + b*vx + c
        st.markdown(f"""
        <div class="info-card">
          <div class="label">Buigpunt</div>
          <div class="value">({vx:.2f}, {vy:.2f})</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-card">
          <div class="label">Buigpunt</div>
          <div class="value">— (lineair)</div>
        </div>""", unsafe_allow_html=True)

with ic2:
    if a != 0:
        st.markdown(f"""
        <div class="info-card">
          <div class="label">Discriminant</div>
          <div class="value">Δ = {discriminant:.2f}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-card">
          <div class="label">Discriminant</div>
          <div class="value">—</div>
        </div>""", unsafe_allow_html=True)

with ic3:
    if kind == "twee_reeel":
        css_cls = "roots-real"
        r1, r2 = root_info[1]
        val = f"x₁ = {r1:.2f}, x₂ = {r2:.2f}"
    elif kind == "een_reeel":
        css_cls = "roots-one"
        val = f"x = {root_info[1][0]:.2f}  (dubbel)"
    elif kind == "complex":
        css_cls = "roots-complex"
        re, im = root_info[1]
        val = f"{re:.2f} ± {abs(im):.2f}i"
    else:
        css_cls = ""
        if b != 0:
            val = f"x = {(-c/b):.2f}"
        else:
            val = "geen oplossing" if c != 0 else "alle x"
    st.markdown(f"""
    <div class="info-card {css_cls}">
      <div class="label">Oplossing(en)</div>
      <div class="value">{val}</div>
    </div>""", unsafe_allow_html=True)

# ── Build figure ──────────────────────────────────────────────────────────────
def make_figure(a, b, c, eq_label, kind, root_info):
    x = np.linspace(-10, 10, 800)
    y = a*x**2 + b*x + c

    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for spine in ax.spines.values():
        spine.set_color("#d1d5db")
    ax.tick_params(colors="#374151", labelsize=9)

    ax.grid(True, color="#f3f4f6", linewidth=0.9, linestyle="--")
    ax.axhline(0, color="#9ca3af", linewidth=1.2)
    ax.axvline(0, color="#9ca3af", linewidth=1.2)

    ax.plot(x, y, color="#4f46e5", linewidth=2.5, zorder=4)
    ax.fill_between(x, y, 0, where=(y > 0), alpha=0.07, color="#4f46e5")
    ax.fill_between(x, y, 0, where=(y < 0), alpha=0.07, color="#ef4444")

    # y-axis limits
    y_range = max(abs(y.max()), abs(y.min()), 1)
    ylim = min(y_range * 1.3, 50)
    ax.set_ylim(-ylim, ylim)
    ax.set_xlim(-10, 10)

    # ── Equation inside the plot ──────────────────────────────────────────────
    ax.text(0.03, 0.96, eq_label,
            transform=ax.transAxes,
            fontsize=13, fontfamily="monospace",
            color="#1e1b4b", va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.45", facecolor="white",
                      edgecolor="#c7d2fe", linewidth=1.3, alpha=0.95))

    # Vertex marker
    if a != 0:
        vx = -b / (2*a)
        vy = a*vx**2 + b*vx + c
        ax.plot(vx, vy, "o", color="#f59e0b", markersize=9, zorder=6)
        ax.annotate(f"  ({vx:.1f}, {vy:.1f})",
                    xy=(vx, vy), color="#b45309", fontsize=8,
                    fontfamily="monospace", va="center",
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")])

    # Root markers
    if kind == "twee_reeel":
        for rx in root_info[1]:
            ax.plot(rx, 0, "o", color="#10b981", markersize=9, zorder=6)
            ax.annotate(f"  {rx:.2f}", xy=(rx, 0), color="#065f46",
                        fontsize=8, fontfamily="monospace", va="bottom",
                        path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    elif kind == "een_reeel":
        rx = root_info[1][0]
        ax.plot(rx, 0, "o", color="#f59e0b", markersize=9, zorder=6)
        ax.annotate(f"  {rx:.2f}", xy=(rx, 0), color="#b45309",
                    fontsize=8, fontfamily="monospace", va="bottom",
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")])

    # Legend (Dutch)
    legend_patches = [
        mpatches.Patch(color="#f59e0b", label="Buigpunt"),
        mpatches.Patch(color="#10b981", label="Nulpunten"),
        mpatches.Patch(color="#4f46e5", alpha=0.4, label="f(x) > 0"),
        mpatches.Patch(color="#ef4444", alpha=0.4, label="f(x) < 0"),
    ]
    ax.legend(handles=legend_patches, facecolor="white",
              edgecolor="#e0e7ff", labelcolor="#374151",
              fontsize=8, loc="upper right")

    ax.set_xlabel("x", fontsize=10, color="#374151")
    ax.set_ylabel("f(x)", fontsize=10, color="#374151")
    plt.tight_layout()
    return fig

fig = make_figure(a, b, c, eq_label, kind, root_info)

# ── Show plot ─────────────────────────────────────────────────────────────────
st.pyplot(fig)

# ── Save button ───────────────────────────────────────────────────────────────
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white")
buf.seek(0)
plt.close(fig)

st.download_button(
    label="💾  Grafiek opslaan als PNG",
    data=buf,
    file_name="kwadratische_functie.png",
    mime="image/png",
    use_container_width=True,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<p style="text-align:center; color:#9ca3af; font-size:0.78rem; margin-top:20px; font-family:'Space Mono',monospace;">
  f(x) = ax² + bx + c &nbsp;·&nbsp; Kwadratische Functie Plotter
</p>
""", unsafe_allow_html=True)
