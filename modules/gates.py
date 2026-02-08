import streamlit as st
from dataclasses import dataclass, asdict

@dataclass
class GateLine:
    gate_type: str
    description: str
    qty: int

GATE_TYPES = [
    "Single Swing Gate",
    "Double Drive Gate",
    "Slide Gate",
    "Cantilever Gate",
    "Roll Gate",
    "Other"
]

def gates_ui():
    st.subheader("Gates")

    if "gates" not in st.session_state:
        st.session_state.gates = []

    colA, colB = st.columns([1,1])
    with colA:
        num_types = st.number_input("How many different gate types?", min_value=0, step=1, value=len(st.session_state.gates))
    with colB:
        if st.button("Reset gates"):
            st.session_state.gates = []
            st.rerun()

    # resize list
    while len(st.session_state.gates) < num_types:
        st.session_state.gates.append(asdict(GateLine(GATE_TYPES[0], "", 1)))
    while len(st.session_state.gates) > num_types:
        st.session_state.gates.pop()

    for i in range(num_types):
        st.markdown(f"**Gate Type #{i+1}**")
        c1, c2, c3 = st.columns([1,2,1])
        with c1:
            st.session_state.gates[i]["gate_type"] = st.selectbox(
                "Type",
                GATE_TYPES,
                index=GATE_TYPES.index(st.session_state.gates[i]["gate_type"]) if st.session_state.gates[i]["gate_type"] in GATE_TYPES else 0,
                key=f"gate_type_{i}"
            )
        with c2:
            st.session_state.gates[i]["description"] = st.text_input(
                "Description (ex: 20' dbl drive, SS40, barbwire, etc.)",
                value=st.session_state.gates[i]["description"],
                key=f"gate_desc_{i}"
            )
        with c3:
            st.session_state.gates[i]["qty"] = st.number_input(
                "Qty",
                min_value=1,
                step=1,
                value=int(st.session_state.gates[i]["qty"] or 1),
                key=f"gate_qty_{i}"
            )

    # convert to line items
    gate_lines = []
    for g in st.session_state.gates:
        qty = int(g.get("qty", 0) or 0)
        if qty <= 0:
            continue
        label = g.get("gate_type", "Gate")
        desc = g.get("description", "").strip()
        if desc:
            full_desc = f"{label} — {desc}"
        else:
            full_desc = label
        gate_lines.append({"item": "GATE", "description": full_desc, "unit": "EA", "qty": qty})

    return gate_lines
