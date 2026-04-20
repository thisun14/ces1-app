import streamlit as st

st.set_page_config(page_title="CES1 Simulator", layout="centered")

st.title("CES1–BMPR2 Endothelial Simulator")
st.caption(
    "Interactive conceptual model inspired by PAH endothelial metabolism research"
)

st.markdown("""
### How to read this model
This app displays **normalized relative scores (0–100)** rather than absolute lab units.

- For **stress/pathology markers** like ROS, lipid accumulation, and apoptosis:  
  **0 = healthy / minimal stress** and **100 = severe PAH-like dysfunction**
- For **protective/function markers** like fatty acid oxidation (FAO) and angiogenesis:  
  **0 = severely impaired** and **100 = preserved / healthy function**

These outputs are **qualitative, mechanism-inspired surrogate scores**, not experimentally calibrated measurements.
""")

# Inputs
bmpr2 = st.slider("BMPR2 activity", 0, 100, 40)
nrf2 = st.slider("NRF2 activity", 0, 100, 40)
ces1 = st.slider("CES1 expression", 0, 100, 30)
epigenetic = st.slider("Epigenetic repression", 0, 100, 60)
hypoxia = st.toggle("Hypoxia", True)

# Model logic
effective_ces1 = max(0, min(100, ces1 - 0.6 * epigenetic))

ros = max(0, min(100, 65 - 0.35 * effective_ces1 + (15 if hypoxia else 0)))
lipid = max(0, min(100, 60 - 0.45 * effective_ces1 + epigenetic * 0.2))
fao = max(0, min(100, 25 + 0.45 * effective_ces1))
glycolysis = max(0, min(100, 70 - 0.2 * effective_ces1 + (10 if hypoxia else 0)))
angiogenesis = max(0, min(100, 25 + 0.35 * effective_ces1 - (10 if hypoxia else 0)))
apoptosis = max(0, min(100, 60 - 0.3 * effective_ces1 + (10 if hypoxia else 0)))

def classify_bad_metric(value: float) -> str:
    if value < 30:
        return "Low"
    if value < 70:
        return "Moderate"
    return "High"

def classify_good_metric(value: float) -> str:
    if value < 30:
        return "Impaired"
    if value < 70:
        return "Intermediate"
    return "Preserved"

st.subheader("Predicted endothelial state")

st.markdown("#### Input-derived intermediate")
st.write(
    f"**Effective CES1:** {effective_ces1:.1f}/100  \n"
    "_Interpretation: estimated functional CES1 after accounting for epigenetic repression_"
)

st.markdown("#### Stress / pathology markers")
st.write(f"**ROS:** {ros:.1f}/100 — **{classify_bad_metric(ros)}**")
st.caption("0 = minimal oxidative stress, 100 = severe PAH-like oxidative stress")

st.write(f"**Lipid accumulation:** {lipid:.1f}/100 — **{classify_bad_metric(lipid)}**")
st.caption("0 = minimal lipid stress, 100 = marked lipotoxic accumulation")

st.write(f"**Glycolysis shift:** {glycolysis:.1f}/100 — **{classify_bad_metric(glycolysis)}**")
st.caption("0 = minimal glycolytic shift, 100 = strong Warburg-like metabolic shift")

st.write(f"**Apoptosis:** {apoptosis:.1f}/100 — **{classify_bad_metric(apoptosis)}**")
st.caption("0 = minimal cell death signaling, 100 = severe pro-apoptotic state")

st.markdown("#### Protective / functional markers")
st.write(f"**Fatty acid oxidation (FAO):** {fao:.1f}/100 — **{classify_good_metric(fao)}**")
st.caption("0 = severely impaired mitochondrial FAO, 100 = preserved FAO")

st.write(f"**Angiogenesis:** {angiogenesis:.1f}/100 — **{classify_good_metric(angiogenesis)}**")
st.caption("0 = severely impaired endothelial repair / vessel formation, 100 = preserved angiogenic function")

# Overall interpretation
st.subheader("Overall interpretation")

if ros > 70 and angiogenesis < 30 and fao < 40:
    st.error(
        "This profile is consistent with a strongly dysfunctional PAH-like endothelial state: "
        "high oxidative stress, impaired angiogenesis, and reduced mitochondrial fat metabolism."
    )
elif ros < 35 and angiogenesis > 65 and fao > 60:
    st.success(
        "This profile is closer to a healthier endothelial state: lower oxidative stress, "
        "better-preserved angiogenesis, and stronger fatty acid oxidation."
    )
else:
    st.info(
        "This profile suggests an intermediate endothelial state with mixed metabolic stress "
        "and partial functional preservation."
    )

st.markdown("""
### Pathway logic
**BMPR2 → NRF2 → CES1 → endothelial metabolic balance and repair**

### Important note
This is a **conceptual hypothesis-exploration tool**.  
It is designed to visualize **directional biological effects** inspired by the CES1/BMPR2 PAH mechanism, not to provide quantitative experimental or clinical predictions.
""")
