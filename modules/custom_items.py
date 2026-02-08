import streamlit as st

def custom_items_ui():
    st.subheader("Custom / Non-typical Items")

    if "custom_items" not in st.session_state:
        st.session_state.custom_items = []

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Add custom item"):
            st.session_state.custom_items.append({"description": "", "unit": "EA", "qty": 1})
    with col2:
        if st.button("Reset custom items"):
            st.session_state.custom_items = []
            st.rerun()

    for i, row in enumerate(st.session_state.custom_items):
        st.markdown(f"**Custom Item #{i+1}**")
        c1, c2, c3, c4 = st.columns([3,1,1,1])
        with c1:
            row["description"] = st.text_input("Description", value=row["description"], key=f"cust_desc_{i}")
        with c2:
            row["unit"] = st.selectbox("Unit", ["EA", "LF", "SF", "LS"], index=["EA","LF","SF","LS"].index(row["unit"]), key=f"cust_unit_{i}")
        with c3:
            row["qty"] = st.number_input("Qty", min_value=0, step=1, value=int(row["qty"] or 0), key=f"cust_qty_{i}")
        with c4:
            if st.button("Delete", key=f"cust_del_{i}"):
                st.session_state.custom_items.pop(i)
                st.rerun()

    # convert to line items
    lines = []
    for r in st.session_state.custom_items:
        desc = (r.get("description") or "").strip()
        qty = int(r.get("qty") or 0)
        if desc and qty > 0:
            lines.append({"item": "CUSTOM", "description": desc, "unit": r.get("unit","EA"), "qty": qty})
    return lines
