import streamlit as st

st.set_page_config(page_title="CES1 Simulator", layout="centered")

# -----------------------------
# Helpers
# -----------------------------
def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))

def classify_bad_metric(value: float) -> str:
    if value < 30:
        return "Low"
    if value < 70:
        return "Moderate"
    return "High"

def classify_good_metric(value: float) -> str:
    if value < 30:
        return "Low"
    if value < 70:
        return "Moderate"
    return "High"

def simple_function_label(value: float) -> str:
    if value < 30:
        return "Reduced"
    if value < 70:
        return "Moderate"
    return "Strong"

def overall_state_label(avg_stress: float, avg_function: float) -> tuple[str, str]:
    if avg_stress > 70 and avg_function < 35:
        return (
            "High endothelial dysfunction",
            "This profile suggests a more disease-like endothelial state with high stress and reduced repair capacity."
        )
    elif avg_stress < 35 and avg_function > 65:
        return (
            "More balanced endothelial state",
            "This profile suggests a healthier endothelial balance with lower stress and better-preserved function."
        )
    else:
        return (
            "Intermediate endothelial state",
            "This profile suggests mixed metabolic stress with partial preservation of endothelial function."
        )

def color_box(text: str, kind: str = "info"):
    colors = {
        "good": "#e8f5e9",
        "warn": "#fff8e1",
        "bad": "#ffebee",
        "info": "#e3f2fd",
    }
    st.markdown(
        f"""
        <div style="
            background-color: {colors.get(kind, "#e3f2fd")};
            padding: 16px 18px;
            border-radius: 12px;
            margin: 10px 0 18px 0;
            font-size: 1.05rem;
            line-height: 1.45;">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Title
# -----------------------------
st.title("CES1–BMPR2 Endothelial Simulator")
st.caption("Interactive conceptual model inspired by PAH endothelial metabolism research")

st.markdown(
    """
**Scale:** 0–100 relative score  
- **Stress markers:** higher = worse  
- **Function markers:** higher = better
"""
)

# -----------------------------
# Presets
# -----------------------------
preset = st.selectbox(
    "Quick start",
    ["Custom", "Healthy-like", "Intermediate", "PAH-like", "Rescue-like"],
    index=2
)

preset_values = {
    "Healthy-like": dict(bmpr2=80, nrf2=75, ces1=80, epigenetic=15, hypoxia=False),
    "Intermediate": dict(bmpr2=55, nrf2=40, ces1=45, epigenetic=30, hypoxia=False),
    "PAH-like": dict(bmpr2=30, nrf2=20, ces1=20, epigenetic=65, hypoxia=True),
    "Rescue-like": dict(bmpr2=55, nrf2=60, ces1=70, epigenetic=20, hypoxia=False),
}

if preset == "Custom":
    default_vals = dict(bmpr2=55, nrf2=40, ces1=45, epigenetic=30, hypoxia=False)
else:
    default_vals = preset_values[preset]

# -----------------------------
# Controls
# -----------------------------
st.subheader("Controls")

bmpr2 = st.slider("BMPR2 activity", 0, 100, default_vals["bmpr2"])
nrf2 = st.slider("NRF2 activity", 0, 100, default_vals["nrf2"])
ces1 = st.slider("CES1 expression", 0, 100, default_vals["ces1"])
epigenetic = st.slider("Epigenetic repression", 0, 100, default_vals["epigenetic"])
hypoxia = st.toggle("Hypoxia", value=default_vals["hypoxia"])

# -----------------------------
# Model
# -----------------------------
effective_ces1 = clamp(ces1 - 0.6 * epigenetic)

ros = clamp(65 - 0.35 * effective_ces1 + (15 if hypoxia else 0))
lipid = clamp(60 - 0.45 * effective_ces1 + epigenetic * 0.2)
fao = clamp(25 + 0.45 * effective_ces1)
glycolysis = clamp(70 - 0.2 * effective_ces1 + (10 if hypoxia else 0))
angiogenesis = clamp(25 + 0.35 * effective_ces1 - (10 if hypoxia else 0))
apoptosis = clamp(60 - 0.3 * effective_ces1 + (10 if hypoxia else 0))

# Grouped summaries
oxidative_stress = clamp(ros)
lipid_stress = clamp(lipid)
energy_function = clamp((fao + (100 - glycolysis)) / 2)
vessel_repair = clamp((angiogenesis + (100 - apoptosis)) / 2)

avg_stress = (oxidative_stress + lipid_stress) / 2
avg_function = (energy_function + vessel_repair) / 2

overall_title, overall_text = overall_state_label(avg_stress, avg_function)

# -----------------------------
# Main summary
# -----------------------------
st.subheader("Overall result")

if "High" in overall_title:
    color_box(f"<strong>{overall_title}</strong><br>{overall_text}", kind="bad")
elif "balanced" in overall_title:
    color_box(f"<strong>{overall_title}</strong><br>{overall_text}", kind="good")
else:
    color_box(f"<strong>{overall_title}</strong><br>{overall_text}", kind="info")

st.subheader("Key effects")

col1, col2 = st.columns(2)

with col1:
    st.metric("Oxidative stress", classify_bad_metric(oxidative_stress))
    st.caption(f"Score: {oxidative_stress:.1f}/100")

    st.metric("Energy metabolism", simple_function_label(energy_function))
    st.caption(f"Score: {energy_function:.1f}/100")

with col2:
    st.metric("Lipid stress", classify_bad_metric(lipid_stress))
    st.caption(f"Score: {lipid_stress:.1f}/100")

    st.metric("Vessel repair", simple_function_label(vessel_repair))
    st.caption(f"Score: {vessel_repair:.1f}/100")

# -----------------------------
# Optional detail
# -----------------------------
with st.expander("Show detailed markers"):
    st.markdown("### Detailed markers")

    st.write(f"**ROS:** {ros:.1f}/100 — {classify_bad_metric(ros)}")
    st.caption("Higher = more oxidative stress")

    st.write(f"**Lipid accumulation:** {lipid:.1f}/100 — {classify_bad_metric(lipid)}")
    st.caption("Higher = more lipotoxic stress")

    st.write(f"**Glycolysis shift:** {glycolysis:.1f}/100 — {classify_bad_metric(glycolysis)}")
    st.caption("Higher = greater stress-related metabolic shift")

    st.write(f"**Apoptosis:** {apoptosis:.1f}/100 — {classify_bad_metric(apoptosis)}")
    st.caption("Higher = stronger cell death tendency")

    st.write(f"**Fatty acid oxidation (FAO):** {fao:.1f}/100 — {classify_good_metric(fao)}")
    st.caption("Higher = better mitochondrial energy use")

    st.write(f"**Angiogenesis:** {angiogenesis:.1f}/100 — {classify_good_metric(angiogenesis)}")
    st.caption("Higher = better endothelial repair / vessel formation")

    st.write(f"**Effective CES1:** {effective_ces1:.1f}/100")
    st.caption("Estimated functional CES1 after accounting for epigenetic repression")

with st.expander("What do 0 and 100 mean?"):
    st.markdown(
        """
- For **stress markers** like ROS or lipid accumulation:  
  **0 = minimal stress**, **100 = severe dysfunction**

- For **function markers** like FAO or vessel repair:  
  **0 = severely impaired**, **100 = preserved / healthy**

These are **relative conceptual scores**, not absolute lab units.
"""
    )

with st.expander("Pathway logic and note"):
    st.markdown(
        """
**Pathway logic:**  
BMPR2 → NRF2 → CES1 → endothelial metabolic balance and repair

**Important note:**  
This is a **conceptual hypothesis-exploration tool**.  
It is meant to visualize **directional biological effects**, not provide quantitative experimental or clinical predictions.
"""
    )
