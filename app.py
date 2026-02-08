# save as app.py
# run with: streamlit run app.py

import math
import streamlit as st
from auth import login_gate
from modules.desc_lib import get_suggestions, add_entry
from modules.gates import gates_ui
from modules.custom_items import custom_items_ui
from modules.pdf_export import export_chainlink_order_form_pdf_bytes
from datetime import datetime
import os




login_gate()

os.makedirs("output", exist_ok=True)




def description_input(style, height_ft, finish, category, uid, label, default_typicals, show_save_button=False):
    """
    style: chainlink / ornamental etc
    category: fabric / posts / caps / ties / rails / fittings / etc
    uid: MUST be unique per line item instance (prevents Streamlit key collisions)
    default_typicals: list[str]
    show_save_button: keep False if you're saving on Calculate
    """
    suggestions = get_suggestions(style, height_ft, finish, category)
    combined = default_typicals + [s for s in suggestions if s not in default_typicals]

    mode = st.radio(
        f"{label} description mode",
        ["Typical", "Custom"],
        horizontal=True,
        key=f"{uid}_mode"
    )

    if mode == "Typical":
        choice = st.selectbox(
            f"{label} (typical)",
            combined if combined else default_typicals,
            key=f"{uid}_typ"
        )
        desc = choice
    else:
        desc = st.text_input(
            f"{label} (custom)",
            key=f"{uid}_cust"
        )
        if suggestions:
            st.caption("Past entries (filtered):")
            st.write(suggestions[:10])

    desc = (desc or "").strip()

    # Optional manual save (we won't use it if saving on Calculate)
    if show_save_button:
        if st.button(f"Save {label} description", key=f"{uid}_save"):
            add_entry(style, height_ft, finish, category, desc)
            st.success("Saved.")

    return desc





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
    finish = st.text_input("Finish (e.g., GALV / BLK)", "")


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


# ---------------- Smart Descriptions ----------------
# Determine "style" for the description library (chainlink vs ornamental etc.)
# For now, default to chainlink since your current app is chainlink-focused.
fence_style = "chainlink"

# Use height if valid, else 0 so the key is stable while user is typing
_height_for_desc = to_int(height_str) or 0

# Normalize finish string (optional but helps consistency)
_finish_for_desc = (finish or "").strip().upper() or "UNSPEC"

desc_registry = []


fabric_desc = description_input(
    style=fence_style,
    height_ft=_height_for_desc,
    finish=_finish_for_desc,
    category="fabric",
    uid=f"fabric_{_height_for_desc}_{_finish_for_desc}",
    label="Fabric",
    default_typicals=[
        '2" mesh, 9ga, galvanized chain link fabric',
        '2" mesh, 11.5ga, galvanized chain link fabric',
        '2" mesh, 9ga, black vinyl-coated chain link fabric',
        '2" mesh, 11.5ga, black vinyl-coated chain link fabric',
    ]
)

desc_registry.append(("fabric", fabric_desc))



# ---------------- Descriptions (like your Excel sheet) ----------------
with st.expander("Descriptions (Optional) — matches Excel takeoff", expanded=False):
    st.caption("Tip: Pick Typical or Custom, then hit Save on the ones you want remembered for this height/finish.")

    # Posts / caps / ties
    line_post_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="posts",
        uid=f"line_post_{_height_for_desc}_{_finish_for_desc}",
        label="Line Post",
        default_typicals=[
            '2 3/8" OD SCH. 40 x 9\'',
            '2 3/8" OD SCH. 20 x 9\'',
        ]
    )

    line_post_cap_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="caps",
        uid=f"line_post_cap_{_height_for_desc}_{_finish_for_desc}",
        label="Line Post Cap",
        default_typicals=[
            "LOOP CAPS",
            '2 3/8" DOME CAPS',
        ]
    )

    ties_line_post_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="ties",
        uid=f"ties_line_{_height_for_desc}_{_finish_for_desc}",
        label="Ties (Line Post)",
        default_typicals=[
            "9ga BLK LONG",
            "9ga GALV LONG",
        ]
    )

    top_rail_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="rails",
        uid=f"top_rail_{_height_for_desc}_{_finish_for_desc}",
        label="Top Rail",
        default_typicals=[
            '1-5/8" OD SCH. 40 x 21\' sw',
            '1-5/8" OD SCH. 20 x 21\' sw',
        ]
    )

    ties_top_rail_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="ties",
        uid=f"ties_top_{_height_for_desc}_{_finish_for_desc}",
        label="Ties (Top Rail)",
        default_typicals=[
            "9ga BLK SHORT",
            "9ga GALV SHORT",
        ]
    )

    corner_post_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="posts",
        uid=f"corner_post_{_height_for_desc}_{_finish_for_desc}",
        label="Corner Post",
        default_typicals=[
            '2 7/8" OD SCH. 40 x 10\'',
            '2 7/8" OD SCH. 20 x 10\'',
        ]
    )

    gate_post_pipe_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="posts",
        uid=f"gate_post_{_height_for_desc}_{_finish_for_desc}",
        label="Gate Post (Pipe)",
        default_typicals=[
            '4" OD SCH. 40 x 10\'',
            '4" OD SCH. 20 x 10\'',
        ]
    )

    corner_post_cap_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="caps",
        uid=f"corner_cap_{_height_for_desc}_{_finish_for_desc}",
        label="Corner Post Caps",
        default_typicals=[
            '2 7/8" DOME CAPS',
            '2 7/8" EXTERNAL DOME CAPS',
        ]
    )

    gate_post_cap_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="caps",
        uid=f"gate_cap_{_height_for_desc}_{_finish_for_desc}",
        label="Gate Post Caps",
        default_typicals=[
            '4" Dome Caps',
            '4" External Dome Caps',
        ]
    )

    # Fittings / bands / misc hardware
    tension_bar_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="fittings",
        uid=f"tension_bar_{_height_for_desc}_{_finish_for_desc}",
        label="Tension Bars",
        default_typicals=[
            '6\' Tension Bars (1/4" x 3/4")',
            '8\' Tension Bars (1/4" x 3/4")',
        ]
    )

    brace_band_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="fittings",
        uid=f"brace_band_{_height_for_desc}_{_finish_for_desc}",
        label="Brace Bands",
        default_typicals=[
            '2 7/8" Bevel',
            '2 3/8" Bevel',
        ]
    )

    tension_band_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="fittings",
        uid=f"tension_band_{_height_for_desc}_{_finish_for_desc}",
        label="Tension Bands",
        default_typicals=[
            '2 7/8" Bevel',
            '2 3/8" Bevel',
        ]
    )

    rail_end_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="fittings",
        uid=f"rail_end_{_height_for_desc}_{_finish_for_desc}",
        label="Rail Ends",
        default_typicals=[
            '2 7/8" x 1-5/8"',
            '2 3/8" x 1-5/8"',
        ]
    )

    line_rail_clamp_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="fittings",
        uid=f"line_clamp_{_height_for_desc}_{_finish_for_desc}",
        label="Line Rail Clamps",
        default_typicals=[
            '2 3/8" x 1-5/8"',
            '2 7/8" x 1-5/8"',
        ]
    )

    # Optional add-ons (only relevant if toggled)
    tension_wire_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="wire",
        uid=f"tension_wire_{_height_for_desc}_{_finish_for_desc}",
        label="Tension Wire",
        default_typicals=[
            "7ga GALV tension wire",
            "9ga GALV tension wire",
            "Vinyl-coated tension wire to match fabric",
        ]
    )

    truss_rod_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="fittings",
        uid=f"truss_rod_{_height_for_desc}_{_finish_for_desc}",
        label="Truss Rods",
        default_typicals=[
            "Truss Rod - 3/8\" x (length per spec)",
            "Truss Rod - 1/2\" x (length per spec)",
        ]
    )

    windscreen_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="accessories",
        uid=f"windscreen_{_height_for_desc}_{_finish_for_desc}",
        label="Windscreen",
        default_typicals=[
            f'{_height_for_desc}\' Windscreen',
            '6\' Windscreen',
        ]
    )

    gates_desc = description_input(
        style=fence_style,
        height_ft=_height_for_desc,
        finish=_finish_for_desc,
        category="gates",
        uid=f"gates_{_height_for_desc}_{_finish_for_desc}",
        label="Gates (general)",
        default_typicals=[
            "6'H x 28'W Sliding",
            "6'H x 15'W Double Drive",
            "6'H x 10'W Double Drive",
            "6'H x 8'W Double Drive",
        ]
    )

# Register descriptions for auto-save on Calculate
desc_registry.extend([
    ("posts", line_post_desc),
    ("caps", line_post_cap_desc),
    ("ties", ties_line_post_desc),
    ("rails", top_rail_desc),
    ("ties", ties_top_rail_desc),

    ("posts", corner_post_desc),
    ("posts", gate_post_pipe_desc),
    ("caps", corner_post_cap_desc),
    ("caps", gate_post_cap_desc),

    ("fittings", tension_bar_desc),
    ("fittings", brace_band_desc),
    ("fittings", tension_band_desc),
    ("fittings", rail_end_desc),
    ("fittings", line_rail_clamp_desc),

    ("wire", tension_wire_desc),
    ("fittings", truss_rod_desc),
    ("accessories", windscreen_desc),
    ("gates", gates_desc),
])




# ---------------- Tabs ----------------

tab_takeoff, tab_custom, tab_export = st.tabs(["Takeoff", "Custom Items", "Export / PDF"])

with tab_takeoff:
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

with tab_custom:
    custom_lines = custom_items_ui()


with tab_export:
    st.subheader("Export / PDF (Excel-style form)")

    items_by_row = st.session_state.get("last_items_by_row")
    meta = st.session_state.get("last_project_meta", {})

    if not items_by_row:
        st.info("Run Calculate in the Takeoff tab first.")
    else:
        colA, colB = st.columns(2)
        with colA:
            meta["project"] = st.text_input("PROJECT", meta.get("project", ""))
            meta["job_name"] = st.text_input("Job Name", meta.get("job_name", ""))
            meta["height_style"] = st.text_input("HEIGHT-STYLE", meta.get("height_style", ""))
        with colB:
            meta["due_date"] = st.text_input("DUE DATE", meta.get("due_date", ""))
            meta["order_date"] = st.text_input("ORDER DATE", meta.get("order_date", ""))
            meta["po"] = st.text_input("PO #", meta.get("po", ""))

        # persist edits
        st.session_state.last_project_meta = meta

        # ---- Generate PDF (stores bytes in session_state) ----
        if st.button("Generate PDF", key="gen_pdf_export_tab"):
            try:
                pdf_bytes = export_chainlink_order_form_pdf_bytes(
                    project=meta,
                    items_by_row=items_by_row
                )
                st.session_state.last_pdf_bytes = pdf_bytes
                st.success("PDF generated.")
            except Exception as e:
                st.error(f"PDF export failed: {e}")

        # ---- Download button (only shows after a successful generate) ----
        pdf_bytes = st.session_state.get("last_pdf_bytes")
        if pdf_bytes:
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"{(meta.get('job_name') or 'JBS_Chainlink_Order_Form').replace(' ', '_')}.pdf",
                mime="application/pdf",
                key="dl_pdf_export_tab"
            )





# ---------------- Override Section ----------------
override_lp = False
override_lp_str = ""

with st.expander("Weird Project Override (Line Posts)"):
    override_lp = st.selectbox("Override Line Posts?", ["No", "Yes"], index=0) == "Yes"
    if override_lp:
        override_lp_str = st.text_input("Line Posts Override", "")

# ---------------- Calculate ----------------
# ---------------- Calculate ----------------
if st.button("Calculate", key="calc_btn"):
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
        # ---------------- Auto-save descriptions on Calculate ----------------
        if _height_for_desc > 0 and _finish_for_desc != "UNSPEC":
            for category, desc in desc_registry:
                add_entry(
                    style=fence_style,
                    height_ft=_height_for_desc,
                    finish=_finish_for_desc,
                    category=category,
                    description=desc
                )

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

        truss_rods = truss_tight = cor_post if has_truss else 0
        ws_rolls = math.ceil(ws_feet / ws_roll_len) if has_ws and ws_feet and ws_roll_len else 0

        items_by_row = {
            "FABRIC": {"qty": int(length), "desc": fabric_desc},

            "LINE POST": {"qty": line_posts, "desc": line_post_desc},
            "LINE POST CAP": {"qty": line_posts, "desc": line_post_cap_desc},
            "TIES LINE POST": {"qty": ties_lp, "desc": ties_line_post_desc},

            "TOP RAIL": {"qty": total_rail_sticks, "desc": top_rail_desc},
            "TIES TOP RAIL": {"qty": ties_tr if has_top else "", "desc": ties_top_rail_desc if has_top else ""},

            "CORNER POST": {"qty": cor_post, "desc": corner_post_desc},
            "CORNER POST CAPS": {"qty": cor_post, "desc": corner_post_cap_desc},

            "GATE POST": {"qty": gate_post, "desc": gate_post_pipe_desc},
            "GATE POST CAPS": {"qty": gate_post, "desc": gate_post_cap_desc},

            "TENSION BARS": {"qty": ten_bar, "desc": tension_bar_desc},
            "BRACE BANDS": {"qty": bb, "desc": brace_band_desc},
            "TENSION BANDS": {"qty": tb, "desc": tension_band_desc},

            'C/B - 5/16" X 1-1/4"': {"qty": n_b, "desc": 'C/B 5/16" x 1-1/4"'},
            "RAIL ENDS": {"qty": rail_ends, "desc": rail_end_desc},
            "LINE RAIL CLAMPS": {"qty": line_rc if line_rc else "", "desc": line_rail_clamp_desc if line_rc else ""},

            "TENSION WIRE": {"qty": ten_wire if has_tw else "", "desc": tension_wire_desc if has_tw else ""},

            "TRUSS ROD - 3/8 X": {"qty": truss_rods if has_truss else "", "desc": truss_rod_desc if has_truss else ""},
            "TRUSS TIGHTENERS": {"qty": truss_tight if has_truss else "", "desc": "Truss Tighteners" if has_truss else ""},

            "WINDSCREEN": {"qty": int(ws_feet) if has_ws and ws_feet is not None else "", "desc": windscreen_desc if has_ws else ""},
        }

        st.session_state.last_items_by_row = items_by_row

        # Save meta for export tab
        height_val = to_int(height_str) or ""
        finish_val = finish or ""
        st.session_state.last_project_meta = {
            "project": "",
            "due_date": "",
            "order_date": "",
            "po": "",
            "job_name": proj_name or "",
            "height_style": f"{height_val}  {finish_val}".strip(),
        }

        st.success("Calculated. Go to Export / PDF tab to generate the PDF.")


# ---------------- Output (safe on reruns) ----------------
with tab_takeoff:
    st.divider()
    st.subheader("Output")

    items_by_row = st.session_state.get("last_items_by_row")

    if not items_by_row:
        st.info("Enter inputs and click Calculate.")
    else:
        # Show the Excel/PDF rows
        for item_name, data in items_by_row.items():
            qty = data.get("qty", "")
            desc = data.get("desc", "")
            if qty != "" and qty is not None:
                st.write(f"**{item_name}:** {qty} — {desc or 'N/A'}")





# ---------------- Build quote items ----------------
#quote_items = []

# Fabric
#quote_items.append({
 #   "item": "FABRIC",
 #   "description": fabric_desc,
  #  "unit": "LF",
   # "qty": int(length)
#})

# Posts / caps / ties / rails (only if quantities > 0)
#def add_line(code, desc, unit, qty):
 #   qty_int = int(qty or 0)
  #  if qty_int > 0:
   #     quote_items.append({"item": code, "description": desc, "unit": unit, "qty": qty_int})

#add_line("LINE POST", line_post_desc, "EA", line_posts)
#add_line("LP CAP", line_post_cap_desc, "EA", line_posts)
#add_line("LP TIES", ties_line_post_desc, "EA", ties_lp)

#add_line("TOP RAIL", top_rail_desc, "EA", total_rail_sticks)
#if has_top:
 #   add_line("TR TIES", ties_top_rail_desc, "EA", ties_tr)

#add_line("CORNER POST", corner_post_desc, "EA", cor_post)
#add_line("CORNER CAP", corner_post_cap_desc, "EA", cor_post)

#add_line("GATE POST", gate_post_pipe_desc, "EA", gate_post)
#add_line("GATE CAP", gate_post_cap_desc, "EA", gate_post)

#add_line("TENSION BAR", tension_bar_desc, "EA", ten_bar)
#add_line("BRACE BAND", brace_band_desc, "EA", bb)
#add_line("TENSION BAND", tension_band_desc, "EA", tb)
#add_line('C/B 5/16 x 1-1/4', 'C/B 5/16" x 1-1/4"', "EA", n_b)
#add_line("RAIL END", rail_end_desc, "EA", rail_ends)

#if line_rc:
 #   add_line("LINE CLAMP", line_rail_clamp_desc, "EA", line_rc)

#if has_tw:
 #   add_line("TENSION WIRE", tension_wire_desc, "LF", ten_wire)
#if has_hog:
 #   add_line("HOG RINGS", "Hog Rings", "EA", hog_rings)

#if has_bw:
 #   add_line("BARB WIRE", "Barbed Wire", "LF", bw_feet)
  #  add_line("BARB ROLLS", "Barbed Wire Rolls", "RL", bw_rolls)

#if has_truss:
 #   add_line("TRUSS ROD", truss_rod_desc, "EA", truss_rods)
  #  add_line("TRUSS TIGHT", "Truss Tighteners", "EA", truss_tight)

#if has_ws:
 #   add_line("WINDSCREEN", windscreen_desc, "LF", int(ws_feet))
  #  add_line("WS ROLLS", "Windscreen Rolls", "RL", ws_rolls)

#if gate_tab == "Yes":
    # placeholder until we wire gates_ui()
 #   add_line("GATES", gates_desc, "EA", 1)

# ---------------- Output ----------------
#st.subheader("Output")

#st.write(f"**Fabric:** {int(length)} LF — {fabric_desc or 'N/A'}")

#st.write(f"**Corner Posts:** {cor_post} — {corner_post_desc or 'N/A'}")
#st.write(f"**Corner Post Caps:** {cor_post} — {corner_post_cap_desc or 'N/A'}")

#st.write(f"**Gate Posts:** {gate_post} — {gate_post_pipe_desc or 'N/A'}")
#st.write(f"**Gate Post Caps:** {gate_post} — {gate_post_cap_desc or 'N/A'}")

#st.write(f"**Line Posts:** {line_posts} — {line_post_desc or 'N/A'}")
#st.write(f"**Line Post Caps:** {line_posts} — {line_post_cap_desc or 'N/A'}")
#st.write(f"**Line Post Ties:** {ties_lp} — {ties_line_post_desc or 'N/A'}")

#st.write(f"**Top Rail (21'):** {total_rail_sticks} — {top_rail_desc or 'N/A'}")
#if has_top:
 #   st.write(f"**Top Rail Ties:** {ties_tr} — {ties_top_rail_desc or 'N/A'}")

#st.write(f"**Tension Bars:** {ten_bar} — {tension_bar_desc or 'N/A'}")
#st.write(f"**Brace Bands:** {bb} — {brace_band_desc or 'N/A'}")
#st.write(f"**Tension Bands:** {tb} — {tension_band_desc or 'N/A'}")
#st.write(f'**C/B 5/16" x 1-1/4":** {n_b}')
#st.write(f"**Rail Ends:** {rail_ends} — {rail_end_desc or 'N/A'}")
#if line_rc:
 #   st.write(f"**Line Rail Clamps:** {line_rc} — {line_rail_clamp_desc or 'N/A'}")

#if has_tw:
 #   st.write(f"**Tension Wire:** {ten_wire} LF — {tension_wire_desc or 'N/A'}")
  #  if has_hog:
   #     st.write(f"**Hog Rings:** {hog_rings}")

#if has_bw:
 #   st.write(f"**Barbed Wire:** {bw_feet} LF")
  #  st.write(f"**Barbed Wire Rolls:** {bw_rolls}")

#if has_truss:
 #   st.write(f"**Truss Rods:** {truss_rods} — {truss_rod_desc or 'N/A'}")
  #  st.write(f"**Truss Tighteners:** {truss_tight}")

#if has_ws:
 #   st.write(f"**Windscreen Footage:** {int(ws_feet)} LF — {windscreen_desc or 'N/A'}")
  #  st.write(f"**Windscreen Rolls:** {ws_rolls}")

#if gate_tab == "Yes":
 #   st.write(f"**Gates:** (see gate posts) — {gates_desc or 'N/A'}")

     
