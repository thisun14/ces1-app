import streamlit as st

st.set_page_config(page_title="CES1 Simulator", layout="centered")

# --------------------------------------------------
# Helpers
# --------------------------------------------------
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
        return "Reduced"
    if value < 70:
        return "Intermediate"
    return "Preserved"

def overall_state_label(avg_stress: float, avg_function: float) -> tuple[str, str, str]:
    if avg_stress > 70 and avg_function < 35:
        return (
            "High endothelial dysfunction",
            "This profile suggests a more disease-like endothelial state with high stress and reduced repair capacity.",
            "bad",
        )
    elif avg_stress < 35 and avg_function > 65:
        return (
            "More balanced endothelial state",
            "This profile suggests lower stress with better-preserved endothelial metabolism and repair.",
            "good",
        )
    else:
        return (
            "Intermediate endothelial state",
            "This profile suggests mixed metabolic stress with partial preservation of endothelial function.",
            "info",
        )

def color_box(title: str, text: str, kind: str = "info"):
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
            padding: 18px 20px;
            border-radius: 14px;
            margin: 10px 0 18px 0;
            line-height: 1.45;">
            <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 6px;">{title}</div>
            <div style="font-size: 1.02rem;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("CES1–BMPR2 Endothelial Simulator")
st.caption("Interactive mechanism explorer inspired by PAH endothelial metabolism research")

st.markdown(
    """
**Scale:** 0–100 relative score  
- **Stress markers:** higher = worse  
- **Function markers:** higher = better
"""
)

# --------------------------------------------------
# Presets
# --------------------------------------------------
preset = st.selectbox(
    "Quick start",
    ["Custom", "Healthy-like", "Intermediate", "PAH-like", "Rescue-like"],
    index=2,
)

preset_values = {
    "Healthy-like": dict(bmpr2=85, nrf2=80, ces1=85, epigenetic=10, hypoxia=False),
    "Intermediate": dict(bmpr2=55, nrf2=50, ces1=55, epigenetic=30, hypoxia=False),
    "PAH-like": dict(bmpr2=20, nrf2=20, ces1=20, epigenetic=70, hypoxia=True),
    "Rescue-like": dict(bmpr2=55, nrf2=70, ces1=75, epigenetic=20, hypoxia=False),
}

if preset == "Custom":
    default_vals = dict(bmpr2=55, nrf2=50, ces1=55, epigenetic=30, hypoxia=False)
else:
    default_vals = preset_values[preset]

# --------------------------------------------------
# Controls
# --------------------------------------------------
st.subheader("Controls")

bmpr2 = st.slider("BMPR2 activity", 0, 100, default_vals["bmpr2"])
nrf2 = st.slider("NRF2 activity", 0, 100, default_vals["nrf2"])
ces1 = st.slider("CES1 expression", 0, 100, default_vals["ces1"])
epigenetic = st.slider("Epigenetic repression", 0, 100, default_vals["epigenetic"])
hypoxia = st.toggle("Hypoxia", value=default_vals["hypoxia"])

# --------------------------------------------------
# Mechanism-inspired model
# --------------------------------------------------
# Paper-consistent design principles:
# 1) BMPR2 supports NRF2 and CES1
# 2) NRF2 supports antioxidant/metabolic balance and CES1
# 3) Epigenetic repression lowers functional CES1
# 4) CES1 loss is a major failure point
# 5) Hypoxia amplifies dysfunction, especially when CES1 is low

# "Axis support" approximates upstream protective signaling
axis_support = clamp(0.55 * bmpr2 + 0.45 * nrf2)

# Effective CES1 reflects its own slider plus upstream support minus repression
effective_ces1 = clamp(
    0.55 * ces1 +
    0.20 * bmpr2 +
    0.15 * nrf2 -
    0.65 * epigenetic
)

# Loss-of-CES1 penalty: little effect when CES1 is adequate,
# but steeper collapse once it gets low
ces1_loss = clamp(100 - effective_ces1)
loss_penalty = (ces1_loss / 100) ** 1.6

# Additional upstream failure burden when BMPR2/NRF2 axis is low
axis_loss = clamp(100 - axis_support)
axis_penalty = (axis_loss / 100) ** 1.2

# Hypoxia acts mainly as an amplifier, especially when system is already fragile
hypoxia_factor = 1.0 + (0.22 if hypoxia else 0.0)

# Stress markers
ros = clamp((12 + 58 * loss_penalty + 18 * axis_penalty) * hypoxia_factor)
lipid = clamp((10 + 62 * loss_penalty + 10 * axis_penalty) * (1.12 if hypoxia else 1.0))
glycolysis = clamp((12 + 55 * loss_penalty + 15 * axis_penalty) * (1.10 if hypoxia else 1.0))
apoptosis = clamp((10 + 54 * loss_penalty + 18 * axis_penalty) * hypoxia_factor)

# Protective/function markers
fao = clamp((92 - 65 * loss_penalty - 15 * axis_penalty) / hypoxia_factor)
angiogenesis = clamp((90 - 60 * loss_penalty - 18 * axis_penalty) / hypoxia_factor)

# Grouped summaries for simpler user interpretation
oxidative_stress = clamp(ros)
lipid_stress = clamp(lipid)
energy_metabolism = clamp((fao + (100 - glycolysis)) / 2)
vessel_repair = clamp((angiogenesis + (100 - apoptosis)) / 2)

avg_stress = (oxidative_stress + lipid_stress) / 2
avg_function = (energy_metabolism + vessel_repair) / 2

overall_title, overall_text, overall_kind = overall_state_label(avg_stress, avg_function)

# --------------------------------------------------
# Main summary
# --------------------------------------------------
st.subheader("Overall result")
color_box(overall_title, overall_text, kind=overall_kind)

st.subheader("Key effects")

col1, col2 = st.columns(2)

with col1:
    st.metric("Oxidative stress", classify_bad_metric(oxidative_stress))
    st.caption(f"Score: {oxidative_stress:.1f}/100")

    st.metric("Energy metabolism", classify_good_metric(energy_metabolism))
    st.caption(f"Score: {energy_metabolism:.1f}/100")

with col2:
    st.metric("Lipid stress", classify_bad_metric(lipid_stress))
    st.caption(f"Score: {lipid_stress:.1f}/100")

    st.metric("Vessel repair", classify_good_metric(vessel_repair))
    st.caption(f"Score: {vessel_repair:.1f}/100")

# --------------------------------------------------
# Optional detail
# --------------------------------------------------
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

    st.write(f"**Axis support (BMPR2/NRF2):** {axis_support:.1f}/100")
    st.caption("Approximate upstream protective signaling support")

    st.write(f"**Effective CES1:** {effective_ces1:.1f}/100")
    st.caption("Estimated functional CES1 after upstream support and epigenetic repression are considered")

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

with st.expander("How this version matches the paper better"):
    st.markdown(
        """
This version is designed so that it behaves **qualitatively** like the paper:

- **CES1 loss** drives oxidative stress, lipid accumulation, apoptosis, reduced FAO, and impaired angiogenesis.
- **BMPR2 and NRF2** support the CES1 axis rather than acting as equal standalone drivers.
- **Epigenetic repression** suppresses effective CES1.
- **Hypoxia** worsens an already fragile system rather than acting as the main driver by itself.

It is still a **mechanism-inspired conceptual model**, not a quantitatively fitted experimental model.
"""
    )

with st.expander("Pathway logic and note"):
    st.markdown(
        """
**Pathway logic:**  
BMPR2 → NRF2 → CES1 → endothelial metabolic balance and repair

**Important note:**  
This tool is intended to visualize **directional biological effects** inspired by the paper, not to provide quantitative experimental or clinical predictions.
"""
    )
