import streamlit as st

st.set_page_config(page_title="Ait Salary Receipt", layout="centered")

BLACK, WHITE, PEACH, YELLOW, LIGHT_GREY = "#1a1a1a", "#ffffff", "#f8cbad", "#ffff00", "#f2f2f2"

def inr(val):
    val = round(val)
    s = str(abs(val))
    fmt = s if len(s) <= 3 else ",".join([s[:-3][i-2 if i-2 > 0 else 0:i] for i in range(len(s[:-3]), 0, -2)][::-1]) + "," + s[-3:]
    return ("-" if val < 0 else "") + fmt

def breakdown(gross, insurance):
    basic = 0.5 * gross
    hra = 0.5 * basic
    medical = 1250
    pf_wage = min(basic, 15000)
    emp_pf = 0.12 * pf_wage
    esi_app = gross <= 21000
    employer_esi = 0.0325 * gross if esi_app else 0.0
    employee_esi = 0.0075 * gross if esi_app else 0.0
    gratuity, bonus = 0.0481 * basic, 0.0833 * basic
    ctc = gross + emp_pf + employer_esi + gratuity + bonus + insurance
    pt = 0 if gross <= 15000 else (150 if gross <= 20000 else 200)
    sec_dep = 0.02 * gross
    tot_ded = emp_pf + employee_esi + pt + sec_dep
    return {
        "gross": gross, "basic": basic, "hra": hra, "medical": medical,
        "employer_pf": emp_pf, "employer_esi": employer_esi, "gratuity": gratuity,
        "bonus": bonus, "insurance": insurance, "ctc": ctc, "employee_pf": emp_pf,
        "employee_esi": employee_esi, "pt": pt, "sec_dep": sec_dep,
        "tot_ded": tot_ded, "net": gross - tot_ded
    }

def solve_gross(target_ctc, insurance):
    lo, hi = 0.0, max(target_ctc * 2.0, 100000.0)
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if breakdown(mid, insurance)["ctc"] < target_ctc:
            lo = mid
        else:
            hi = mid
    return breakdown((lo + hi) / 2.0, insurance)

def row_html(cells, bg=WHITE, fg=BLACK, bold=False):
    weight = "700" if bold else "400"
    tds = ""
    for i, text in enumerate(cells):
        align = "left" if i == 0 else "right"
        tds += f'<td style="padding:6px 10px;text-align:{align};background:{bg};color:{fg};font-weight:{weight};border:1px solid #ddd;">{text}</td>'
    return f"<tr>{tds}</tr>"

st.markdown(
    f"<h2 style='text-align:center;background:{BLACK};color:{WHITE};padding:12px;border-radius:6px;'>Ait Salary Receipt</h2>",
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)
with col1:
    ctc_input = st.text_input("Monthly CTC", value="50656")
with col2:
    ins_input = st.text_input("Insurance", value="600")

if st.button("Calculate", use_container_width=True):
    try:
        d = solve_gross(float(ctc_input.replace(",", "")), float(ins_input.replace(",", "")))
    except ValueError:
        st.error("Please enter valid numbers.")
        st.stop()

    html = "<table style='width:100%;border-collapse:collapse;font-family:Segoe UI, sans-serif;font-size:14px;'>"
    html += row_html(("Particulars", "Rate", "Per Month", "Per Year"), bg=BLACK, fg=WHITE, bold=True)

    earnings = [
        ("Basic Salary", "50%", d["basic"]),
        ("HRA", "50%", d["hra"]),
        ("Medical Allowance", "Fixed", d["medical"]),
    ]
    for i, (l, k, v) in enumerate(earnings):
        html += row_html((l, k, inr(v), inr(v * 12)), bg=LIGHT_GREY if i % 2 else WHITE)

    html += row_html(("Total Gross Salary", "", inr(d["gross"]), inr(d["gross"] * 12)), bg=PEACH, bold=True)

    employers = [
        ("Employer PF Contribution", "12%", d["employer_pf"]),
        ("Employer ESI Contribution", "3.25%", d["employer_esi"]),
        ("Gratuity Contribution", "4.81%", d["gratuity"]),
        ("Bonus", "8.33%", d["bonus"]),
        ("Medical & Accidental Insurance", "Input", d["insurance"]),
    ]
    for i, (l, k, v) in enumerate(employers):
        html += row_html((l, k, inr(v), inr(v * 12)), bg=LIGHT_GREY if i % 2 else WHITE)

    html += row_html(("Cost to Company (CTC)", "", inr(d["ctc"]), inr(d["ctc"] * 12)), bg=PEACH, bold=True)
    html += row_html(("Deductions", "", "", ""), bg=BLACK, fg=WHITE, bold=True)

    deductions = [
        ("PF Contribution by Employee", "12%", d["employee_pf"]),
        ("ESI Contribution by Employee", "0.75%", d["employee_esi"]),
        ("Professional Tax (PT)", "Slab", d["pt"]),
        ("Security Deposit", "2%", d["sec_dep"]),
    ]
    for i, (l, k, v) in enumerate(deductions):
        html += row_html((l, k, inr(v), inr(v * 12)), bg=LIGHT_GREY if i % 2 else WHITE)

    html += row_html(("Total Deductions", "", inr(d["tot_ded"]), inr(d["tot_ded"] * 12)), bg=BLACK, fg=WHITE, bold=True)
    html += row_html(("Net Salary (In Hand)", "", inr(d["net"]), inr(d["net"] * 12)), bg=YELLOW, bold=True)

    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)
