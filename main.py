import tkinter as tk
from tkinter import font as tkfont

BLACK, WHITE, PEACH, YELLOW, LIGHT_GREY = "#1a1a1a", "#ffffff", "#f8cbad", "#ffff00", "#f2f2f2"
FONT_FAMILY = "Segoe UI"

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

class CTCCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ait Salary Receipt")
        self.geometry("680x750")
        self.configure(bg=WHITE)

        self.font_b = tkfont.Font(family=FONT_FAMILY, size=10, weight="bold")
        self.font_n = tkfont.Font(family=FONT_FAMILY, size=10)

        self.ctc_var = tk.StringVar(value="50656")
        self.ins_var = tk.StringVar(value="600")

        top = tk.Frame(self, bg=BLACK, pady=10)
        top.pack(fill="x")
        tk.Label(top, text="Ait Salary Receipt", bg=BLACK, fg=WHITE,
                 font=tkfont.Font(family=FONT_FAMILY, size=14, weight="bold")).pack()

        inp = tk.Frame(self, bg=WHITE, padx=15, pady=10)
        inp.pack(fill="x")
        tk.Label(inp, text="Monthly CTC:", font=self.font_b, bg=WHITE).grid(row=0, column=0, sticky="w")
        tk.Entry(inp, textvariable=self.ctc_var, width=12, font=self.font_n, justify="right").grid(row=0, column=1, padx=5)
        tk.Label(inp, text="Insurance:", font=self.font_b, bg=WHITE).grid(row=0, column=2, sticky="w", padx=(15, 0))
        tk.Entry(inp, textvariable=self.ins_var, width=12, font=self.font_n, justify="right").grid(row=0, column=3, padx=5)
        tk.Button(inp, text="Calculate", command=self.recalculate, bg=BLACK, fg=WHITE,
                  font=self.font_b, cursor="hand2").grid(row=0, column=4, padx=10)

        self.table = tk.Frame(self, bg=WHITE, padx=15, pady=5)
        self.table.pack(fill="both", expand=True)
        for i in range(4):
            self.table.columnconfigure(i, weight=1 if i else 3)

        self.recalculate()

    def _row(self, r, cells, bg=WHITE, fg=BLACK, bold=False):
        font = self.font_b if bold else self.font_n
        for c, text in enumerate(cells):
            tk.Label(self.table, text=text, bg=bg, fg=fg, font=font,
                     anchor="w" if c == 0 else "e", padx=6, pady=3).grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        return r + 1

    def recalculate(self):
        try:
            d = solve_gross(float(self.ctc_var.get().replace(",", "")), float(self.ins_var.get().replace(",", "")))
        except ValueError:
            return

        for w in self.table.winfo_children():
            w.destroy()

        r = self._row(0, ("Particulars", "Rate", "Per Month", "Per Year"), bg=BLACK, fg=WHITE, bold=True)

        earnings = [
            ("Basic Salary", "50%", d["basic"]),
            ("HRA", "50%", d["hra"]),
            ("Medical Allowance", "Fixed", d["medical"]),
        ]
        for i, (l, k, v) in enumerate(earnings):
            r = self._row(r, (l, k, inr(v), inr(v * 12)), bg=LIGHT_GREY if i % 2 else WHITE)

        r = self._row(r, ("Total Gross Salary", "", inr(d["gross"]), inr(d["gross"] * 12)), bg=PEACH, bold=True)

        employers = [
            ("Employer PF Contribution", "12%", d["employer_pf"]),
            ("Employer ESI Contribution", "3.25%", d["employer_esi"]),
            ("Gratuity Contribution", "4.81%", d["gratuity"]),
            ("Bonus", "8.33%", d["bonus"]),
            ("Medical & Accidental Insurance", "Input", d["insurance"]),
        ]
        for i, (l, k, v) in enumerate(employers):
            r = self._row(r, (l, k, inr(v), inr(v * 12)), bg=LIGHT_GREY if i % 2 else WHITE)

        r = self._row(r, ("Cost to Company (CTC)", "", inr(d["ctc"]), inr(d["ctc"] * 12)), bg=PEACH, bold=True)

        r = self._row(r, ("Deductions", "", "", ""), bg=BLACK, fg=WHITE, bold=True)

        deductions = [
            ("PF Contribution by Employee", "12%", d["employee_pf"]),
            ("ESI Contribution by Employee", "0.75%", d["employee_esi"]),
            ("Professional Tax (PT)", "Slab", d["pt"]),
            ("Security Deposit", "2%", d["sec_dep"]),
        ]
        for i, (l, k, v) in enumerate(deductions):
            r = self._row(r, (l, k, inr(v), inr(v * 12)), bg=LIGHT_GREY if i % 2 else WHITE)

        r = self._row(r, ("Total Deductions", "", inr(d["tot_ded"]), inr(d["tot_ded"] * 12)), bg=BLACK, fg=WHITE, bold=True)
        r = self._row(r, ("Net Salary (In Hand)", "", inr(d["net"]), inr(d["net"] * 12)), bg=YELLOW, bold=True)

if __name__ == "__main__":
    CTCCalculatorApp().mainloop()
