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

def overall_state_label(stress_load: float, function_level: float, hypoxia: bool) -> tuple[str, str, str]:
    if stress_load > 70 and function_level < 35:
        return (
            "High endothelial dysfunction",
            "This profile suggests a disease-like endothelial state with high stress and reduced repair capacity.",
            "bad",
        )
    elif stress_load < 30 and function_level > 70:
        return (
            "More balanced endothelial state",
            "This profile suggests lower stress with better-preserved endothelial metabolism and repair.",
            "good",
        )
    elif stress_load < 45 and function_level < 40 and not hypoxia:
        return (
            "Low-function vulnerable state",
            "This profile suggests weak endothelial reserve without strong active stress. The system may be vulnerable to additional insults.",
            "warn",
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
    "Rescue-like": dict(bmpr2=20, nrf2=20, ces1=80, epigenetic=70, hypoxia=True),
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
# BMPR2 and NRF2 act mainly as upstream support for CES1-related protection.
axis_support = clamp(0.55 * bmpr2 + 0.45 * nrf2)

# CES1 depends on its own expression, upstream support, and repression.
# Repression is intentionally strong.
raw_ces1_capacity = (
    0.65 * ces1
    + 0.20 * bmpr2
    + 0.15 * nrf2
    - 0.95 * epigenetic
)

# Upstream deficiency weakens the ability of CES1 to function.
axis_multiplier = 0.35 + 0.65 * (axis_support / 100.0)

effective_ces1 = clamp(raw_ces1_capacity * axis_multiplier)

# Resilience combines effective CES1 with upstream signaling.
resilience = clamp(0.70 * effective_ces1 + 0.30 * axis_support)

# Vulnerability rises as resilience falls.
vulnerability = clamp(100 - resilience)

# Threshold behavior:
# once effective CES1 gets low, damage accelerates sharply.
ces1_deficit = clamp(100 - effective_ces1) / 100.0
threshold_penalty = ces1_deficit ** 1.8

# Basal dysfunction from poor reserve
basal_stress = clamp(8 + 22 * threshold_penalty + 0.10 * vulnerability)

# Hypoxia acts like a stress trigger whose impact depends on vulnerability.
hypoxia_driver = 0.0
if hypoxia:
    hypoxia_driver = 18 + 28 * threshold_penalty + 0.20 * vulnerability

# Total stress burden
stress_burden = clamp(basal_stress + hypoxia_driver)

# Downstream stress markers
ros = clamp(5 + 20 * threshold_penalty + 0.35 * stress_burden + (10 if hypoxia else 0))
lipid = clamp(8 + 35 * threshold_penalty + 0.20 * vulnerability + 0.20 * hypoxia_driver)
glycolysis = clamp(8 + 28 * threshold_penalty + 0.22 * vulnerability + 0.22 * hypoxia_driver)
apoptosis = clamp(5 + 18 * threshold_penalty + 0.28 * stress_burden)

# Downstream protective functions
fao = clamp(92 - 40 * threshold_penalty - 0.28 * stress_burden - 0.10 * vulnerability)
angiogenesis = clamp(88 - 36 * threshold_penalty - 0.32 * stress_burden - 0.12 * vulnerability)

# Grouped summaries
oxidative_stress = clamp(ros)
lipid_stress = clamp(lipid)
energy_metabolism = clamp((fao + (100 - glycolysis)) / 2)
vessel_repair = clamp((angiogenesis + (100 - apoptosis)) / 2)

stress_load = (oxidative_stress + lipid_stress) / 2
function_level = (energy_metabolism + vessel_repair) / 2

overall_title, overall_text, overall_kind = overall_state_label(stress_load, function_level, hypoxia)

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

    st.write(f"**Resilience:** {resilience:.1f}/100")
    st.caption("Estimated endothelial reserve / protective capacity")

    st.write(f"**Stress burden:** {stress_burden:.1f}/100")
    st.caption("Estimated disease-driving stress load after accounting for hypoxia and vulnerability")

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
This version is designed to reflect the paper's qualitative logic:

- **CES1 loss** increases ROS, lipid stress, apoptosis, and metabolic dysfunction.
- **BMPR2 and NRF2** mainly support the protective CES1 axis.
- **Epigenetic repression** strongly reduces functional CES1.
- **Hypoxia** acts as a true amplifier of damage in a fragile system.
- **CES1 rescue** should visibly improve stress and function outputs.

It remains a **mechanism-inspired conceptual model**, not a fitted experimental model.
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
