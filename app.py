import streamlit as st
import pandas as pd
import math
from decimal import Decimal, InvalidOperation
import altair as alt

st.set_page_config(page_title="House Savings Calculator", layout="centered")

def parse_currency(s: str) -> Decimal | None:
    if not s:
        return None
    s = s.replace("£", "").replace(",", "").strip()
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

st.title("House Savings Calculator")

with st.form("inputs"):
    house_input = st.text_input("House price (£):", placeholder="e.g. £350,000")
    savings_input = st.text_input("Savings per year (£):", placeholder="e.g. 12,000")
    submitted = st.form_submit_button("Calculate")

if submitted:
    house = parse_currency(house_input)
    savings = parse_currency(savings_input)

    if house is None or house <= 0:
        st.error("Invalid house price — enter a positive number (currency symbols and commas allowed).")
    elif savings is None or savings <= 0:
        st.error("Invalid savings — enter a positive number (currency symbols and commas allowed).")
    else:
        # Validator copied from your console app: require savings per year <= house price
        if savings > house:
            st.error("Validation failed: savings per year must be less than or equal to the house price.")
        else:
            years_needed = float(house / savings)
            st.success(f"You will need {years_needed:.1f} years to afford the house.")

            max_year = max(0, math.ceil(years_needed)) + 1
            rows = []
            for y in range(0, max_year + 1):
                rows.append({"Year": y, "Savings": float(y) * float(savings)})

            df = pd.DataFrame(rows)
            df["Reached"] = df["Savings"] >= float(house)

            # formatted table
            def fmt_currency(val):
                return f"£{int(val):,}"
            st.write("Yearly savings table")
            st.table(df.assign(Savings=df["Savings"].apply(fmt_currency)).drop(columns="Reached"))

            # line chart with target rule
            base = alt.Chart(df).encode(x="Year:O")
            line = base.mark_line(point=True).encode(y=alt.Y("Savings:Q", title="Savings (£)"))
            target = alt.Chart(pd.DataFrame({"y":[float(house)]})).mark_rule(color="red").encode(y="y:Q")
            chart = (line + target).properties(height=300, width=700)
            st.altair_chart(chart, use_container_width=True)