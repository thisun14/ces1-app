import streamlit as st

st.set_page_config(page_title="CES1 Simulator", layout="centered")

st.title("CES1–BMPR2 Endothelial Simulator")
st.caption("Interactive prototype inspired by PAH endothelial metabolism research")

bmpr2 = st.slider("BMPR2 activity", 0, 100, 40)
nrf2 = st.slider("NRF2 activity", 0, 100, 40)
ces1 = st.slider("CES1 expression", 0, 100, 30)
epigenetic = st.slider("Epigenetic repression", 0, 100, 60)
hypoxia = st.toggle("Hypoxia", True)

effective_ces1 = ces1 - 0.6 * epigenetic

ros = max(0, min(100, 65 - 0.35 * effective_ces1 + (15 if hypoxia else 0)))
lipid = max(0, min(100, 60 - 0.45 * effective_ces1 + epigenetic * 0.2))
fao = max(0, min(100, 25 + 0.45 * effective_ces1))
glycolysis = max(0, min(100, 70 - 0.2 * effective_ces1 + (10 if hypoxia else 0)))
angiogenesis = max(0, min(100, 25 + 0.35 * effective_ces1 - (10 if hypoxia else 0)))
apoptosis = max(0, min(100, 60 - 0.3 * effective_ces1 + (10 if hypoxia else 0)))

st.subheader("Predicted endothelial state")

st.write(f"ROS: {ros:.1f}")
st.write(f"Lipid accumulation: {lipid:.1f}")
st.write(f"Fatty acid oxidation: {fao:.1f}")
st.write(f"Glycolysis: {glycolysis:.1f}")
st.write(f"Angiogenesis: {angiogenesis:.1f}")
st.write(f"Apoptosis: {apoptosis:.1f}")

if ros > 60 and angiogenesis < 40:
    st.warning("High oxidative stress with impaired angiogenesis (PAH-like state)")
elif fao > 50:
    st.success("More balanced endothelial metabolic state")
else:
    st.info("Intermediate endothelial state")

st.markdown("""
**Pathway:**  
BMPR2 → NRF2 → CES1 → metabolism + angiogenesis

*Conceptual model inspired by recent CES1 PAH research*
""")
