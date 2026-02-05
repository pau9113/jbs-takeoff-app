# save as app.py
# run with: streamlit run app.py

import math
import streamlit as st
from auth import login_gate
login_gate()



st.set_page_config(page_title="JBS Fence Takeoff", layout="centered")
st.title("JBS Fence Takeoff")

# ---------------- Helpers ----------------
def round_up_to(x, multiple):
    return int(math.ceil(x / multiple) * multiple)

def to_int(s):
    try:
        if s is None or str(s).strip() == "":
            return None
        return int(float(s))
    except:
        return None

def to_float(s):
    try:
        if s is None or str(s).strip() == "":
            return None
        return float(s)
    except:
        return None

def req(name, val, *, allow_zero=False):
    if val is None:
        return f"• {name} is required."
    if allow_zero:
        if val < 0:
            return f"• {name} must be ≥ 0."
    else:
        if val <= 0:
            return f"• {name} must be > 0."
    return None

# ---------------- Base Inputs ----------------
proj_name = st.text_input("Project Name", "")

c1, c2, c3 = st.columns(3)
with c1:
    height_str = st.text_input("Height (ft)", "")
with c2:
    style = st.text_input("Style (e.g., BLK / GALV)", "")
with c3:
    spacing_str = st.text_input("Post Spacing (ft)", "")

length_str = st.text_input("Length (ft)", "")

c4, c5, c6 = st.columns(3)
with c4:
    cor_post_str = st.text_input("Corner Posts", "")
with c5:
    end_post_str = st.text_input("End Posts (For calculations only)", "")
with c6:
    gate_post_str = st.text_input("Gate Posts", "")

# ---------------- Tabs ----------------
tabs = st.tabs([
    "Rails",
    "Tension Wire + Hog Rings",
    "Barbed Wire",
    "Truss Rods",
    "Windscreen",
    "Gates"
])

# --- Rails ---
with tabs[0]:
    st.subheader("Rails")
    has_top = st.selectbox("Top Rail?", ["Yes", "No"], index=0) == "Yes"

    mid_opt = st.selectbox("Mid Rail(s)?", ["No", "Yes"], index=0)
    mid_count_str = ""
    if mid_opt == "Yes":
        mid_count_str = st.text_input("Number of Mid Rails", "1")

    has_bottom = st.selectbox("Bottom Rail?", ["No", "Yes"], index=0) == "Yes"

# --- Tension Wire ---
with tabs[1]:
    st.subheader("Tension Wire + Hog Rings")
    has_tw = st.selectbox("Bottom Tension Wire?", ["No", "Yes"], index=0) == "Yes"

    has_hog = False
    hog_spacing_str = ""
    if has_tw:
        has_hog = st.selectbox("Hog Rings?", ["No", "Yes"], index=0) == "Yes"
        if has_hog:
            hog_spacing_str = st.text_input("Hog Ring Spacing (ft)", "2")

# --- Barbed Wire ---
with tabs[2]:
    st.subheader("Barbed Wire")
    has_bw = st.selectbox("Barbed Wire?", ["No", "Yes"], index=0) == "Yes"

    bw_strands_str = "3"
    if has_bw:
        bw_strands_str = st.text_input("Number of Strands", "3")
        st.caption("Roll size assumed 1320 LF")

# --- Truss Rods ---
with tabs[3]:
    st.subheader("Truss Rods")
    has_truss = st.selectbox("Truss Rods + Tighteners?", ["No", "Yes"], index=0) == "Yes"

# --- Windscreen ---
with tabs[4]:
    st.subheader("Windscreen")
    has_ws = st.selectbox("Windscreen?", ["No", "Yes"], index=0) == "Yes"

    ws_feet_str = ""
    ws_roll_len_str = ""
    if has_ws:
        ws_feet_str = st.text_input("Windscreen Footage (ft)", "")
        ws_roll_len_str = st.text_input("Windscreen Roll Length (ft)", "50")

# --- Gates ---
with tabs[5]:
    st.subheader("Gates")
    gate_tab = st.selectbox("Any gates on this run?", ["No", "Yes"], index=0)

# ---------------- Override Section ----------------
override_lp = False
override_lp_str = ""

with st.expander("Weird Project Override (Line Posts)"):
    override_lp = st.selectbox("Override Line Posts?", ["No", "Yes"], index=0) == "Yes"
    if override_lp:
        override_lp_str = st.text_input("Line Posts Override", "")

# ---------------- Calculate ----------------
if st.button("Calculate"):
    height = to_int(height_str)
    spacing = to_float(spacing_str)
    length = to_float(length_str)

    cor_post = to_int(cor_post_str)
    end_post = to_int(end_post_str)
    gate_post = to_int(gate_post_str)

    mid_count = to_int(mid_count_str) if mid_opt == "Yes" else 0
    hog_spacing = to_float(hog_spacing_str) if has_hog else None
    bw_strands = to_int(bw_strands_str) if has_bw else 0
    ws_feet = to_float(ws_feet_str) if has_ws else None
    ws_roll_len = to_float(ws_roll_len_str) if has_ws else None
    lp_override = to_int(override_lp_str) if override_lp else None

    total_rails = (1 if has_top else 0) + mid_count + (1 if has_bottom else 0)

    errors = []
    for name, val, allow_zero in [
        ("Height", height, False),
        ("Post Spacing", spacing, False),
        ("Length", length, False),
        ("Terminal Posts", cor_post, True),
        ("End Posts", end_post, True),
        ("Gate Posts", gate_post, True),
        ("Rails Selected", total_rails, False),
    ]:
        err = req(name, val, allow_zero=allow_zero)
        if err:
            errors.append(err)

    if has_hog:
        err = req("Hog Ring Spacing", hog_spacing)
        if err:
            errors.append(err)

    if has_bw:
        err = req("Barbed Wire Strands", bw_strands)
        if err:
            errors.append(err)

    if has_ws:
        err = req("Windscreen Footage", ws_feet)
        if err:
            errors.append(err)
        err = req("Windscreen Roll Length", ws_roll_len)
        if err:
            errors.append(err)

    if override_lp:
        err = req("Line Post Override", lp_override, allow_zero=True)
        if err:
            errors.append(err)

    if end_post is not None and cor_post is not None and end_post > cor_post:
        errors.append("• End posts cannot exceed terminal posts.")

    if gate_post and gate_tab == "No":
        errors.append("• Gate posts entered but Gates tab is set to No.")

    if errors:
        st.error("Fix the following:\n" + "\n".join(errors))
    else:
        # ---------------- Calculations ----------------
        if override_lp:
            line_posts = max(0, lp_override)
        else:
            line_posts = math.ceil((length / spacing) - cor_post - gate_post)
            if line_posts < 0:
                line_posts = 0

        ties_lp = round_up_to(height * line_posts, 50)

        top_rail = math.ceil(length / 21) if has_top else 0
        mid_rail = math.ceil((length * mid_count) / 21) if mid_count else 0
        bottom_rail = math.ceil(length / 21) if has_bottom else 0
        total_rail_sticks = top_rail + mid_rail + bottom_rail

        ties_tr = round_up_to(length / 1.25, 50) if has_top else 0

        true_corners = max(0, cor_post - end_post)

        ten_bar = (true_corners * 2) + (end_post * 1) + (gate_post * 1)

        bb = round_up_to(
            ((true_corners * 4) + (end_post * 2) + (gate_post * 2)) * total_rails,
            50
        )

        tb = round_up_to((height - 1) * ten_bar, 50)
        n_b = math.ceil((bb + tb) / 100)

        rail_ends = ((true_corners * 2) + end_post + gate_post) * total_rails
        line_rc = (mid_count + (1 if has_bottom else 0)) * line_posts

        ten_wire = int(length) if has_tw else 0
        hog_rings = round_up_to(math.ceil(length / hog_spacing), 50) if has_hog else 0

        bw_feet = bw_rolls = 0
        if has_bw:
            bw_feet = int(length * bw_strands)
            bw_rolls = math.ceil(bw_feet / 1320)

        truss_rods = truss_tight = cor_post if has_truss else 0

        ws_rolls = math.ceil(ws_feet / ws_roll_len) if has_ws else 0

        # ---------------- Output ----------------
        st.subheader("Output")

        st.write(f"**Project:** {proj_name or 'N/A'}")
        st.write(f"**Fence:** {height} FT {style}")
        st.write(f"**Fabric:** {int(length)} LF")

        st.write(f"**Corner Posts:** {cor_post}")
        st.write(f"**Gate Posts:** {gate_post}")

        st.write(f"**Line Posts:** {line_posts}")
        st.write(f"**Line Post Caps:** {line_posts}")
        st.write(f"**Line Post Ties:** {ties_lp}")

        st.write(f"**Top Rail (21'):** {total_rail_sticks}")
        if has_top:
            st.write(f"**Top Rail Ties:** {ties_tr}")

        st.write(f"**Tension Bars:** {ten_bar}")
        st.write(f"**Brace Bands:** {bb}")
        st.write(f"**Tension Bands:** {tb}")
        st.write(f'**C/B 5/16" x 1-1/4":** {n_b}')
        st.write(f"**Rail Ends:** {rail_ends}")
        if line_rc:
            st.write(f"**Line Rail Clamps:** {line_rc}")

        if has_tw:
            st.write(f"**Tension Wire:** {ten_wire} LF")
            if has_hog:
                st.write(f"**Hog Rings:** {hog_rings}")

        if has_bw:
            st.write(f"**Barbed Wire:** {bw_feet} LF")
            st.write(f"**Barbed Wire Rolls:** {bw_rolls}")

        if has_truss:
            st.write(f"**Truss Rods:** {truss_rods}")
            st.write(f"**Truss Tighteners:** {truss_tight}")

        if has_ws:
            st.write(f"**Windscreen Footage:** {int(ws_feet)} LF")
            st.write(f"**Windscreen Rolls:** {ws_rolls}")
