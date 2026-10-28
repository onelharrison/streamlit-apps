import json
import math
import re
from decimal import Decimal, ROUND_HALF_UP
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]

TITLE_FEE_ESTIMATES = {
    "Alabama": 15.0,
    "Alaska": 15.0,
    "Arizona": 4.0,
    "Arkansas": 10.0,
    "California": 28.0,
    "Colorado": 7.2,
    "Connecticut": 25.0,
    "Delaware": 35.0,
    "Florida": 70.0,
    "Georgia": 18.0,
    "Hawaii": 0.0,
    "Idaho": 14.0,
    "Illinois": 165.0,
    "Indiana": 15.0,
    "Iowa": 35.0,
    "Kansas": 10.0,
    "Kentucky": 9.0,
    "Louisiana": 68.5,
    "Maine": 33.0,
    "Maryland": 200.0,
    "Massachusetts": 75.0,
    "Michigan": 15.0,
    "Minnesota": 51.5,
    "Mississippi": 9.0,
    "Missouri": 8.5,
    "Montana": 12.0,
    "Nebraska": 10.0,
    "Nevada": 28.25,
    "New Hampshire": 35.0,
    "New Jersey": 60.0,
    "New Mexico": 5.0,
    "New York": 50.0,
    "North Carolina": 66.75,
    "North Dakota": 5.0,
    "Ohio": 18.0,
    "Oklahoma": 11.0,
    "Oregon": 106.0,
    "Pennsylvania": 72.0,
    "Rhode Island": 53.5,
    "South Carolina": 15.0,
    "South Dakota": 10.0,
    "Tennessee": 14.0,
    "Texas": 28.0,
    "Utah": 6.0,
    "Vermont": 42.0,
    "Virginia": 15.0,
    "Washington": 15.0,
    "West Virginia": 15.0,
    "Wisconsin": 214.5,
    "Wyoming": 15.0,
}

REGISTRATION_FEE_ESTIMATES = {
    "Alabama": 27.25,
    "Alaska": 100.0,
    "Arizona": 547.1,
    "Arkansas": 28.0,
    "California": 444.0,
    "Colorado": 628.6,
    "Connecticut": 229.0,
    "Delaware": 40.0,
    "Florida": 303.85,
    "Georgia": 20.0,
    "Hawaii": 107.25,
    "Idaho": 70.25,
    "Illinois": 151.0,
    "Indiana": 36.35,
    "Iowa": 0.0,
    "Kansas": 30.0,
    "Kentucky": 21.0,
    "Louisiana": 68.0,
    "Maine": 803.0,
    "Maryland": 120.5,
    "Massachusetts": 60.0,
    "Michigan": 203.0,
    "Minnesota": 514.0,
    "Mississippi": 29.0,
    "Missouri": 69.25,
    "Montana": 246.53,
    "Nebraska": 28.7,
    "Nevada": 458.6,
    "New Hampshire": 632.0,
    "New Jersey": 59.0,
    "New Mexico": 74.5,
    "New York": 91.5,
    "North Carolina": 46.25,
    "North Dakota": 93.0,
    "Ohio": 44.0,
    "Oklahoma": 116.25,
    "Oregon": 162.0,
    "Pennsylvania": 48.0,
    "Rhode Island": 103.5,
    "South Carolina": 40.0,
    "South Dakota": 2.0,
    "Tennessee": 26.5,
    "Texas": 64.0,
    "Utah": 197.5,
    "Vermont": 99.0,
    "Virginia": 30.75,
    "Washington": 249.25,
    "West Virginia": 51.5,
    "Wisconsin": 97.0,
    "Wyoming": 606.0,
}


@st.cache_data(ttl=24 * 60 * 60)
def fetch_json(url):
    request = Request(url, headers={"User-Agent": "CarShoppingCalculator/1.0"})
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 404:
            raise ValueError("A tax rate was not found for the selected state.") from error
        raise RuntimeError(
            f"The rate lookup service returned HTTP {error.code}. Please try again later."
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Could not reach the rate lookup service: {error.reason}"
        ) from error
    except TimeoutError as error:
        raise RuntimeError("The rate lookup service timed out. Please try again.") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError("The rate lookup service returned an invalid response.") from error


@st.cache_data(ttl=24 * 60 * 60)
def lookup_sales_tax(state):
    state_slug = re.sub(r"[^a-z0-9]+", "-", state.lower()).strip("-")
    tax_data = fetch_json(f"https://receiptedit.com/api/sales-tax/{state_slug}")
    if not isinstance(tax_data, dict):
        raise RuntimeError("The tax-rate service returned invalid rate data.")
    if tax_data.get("state", "").casefold() != state.casefold():
        raise RuntimeError("The tax-rate service returned data for an unexpected state.")

    try:
        rate_percent = float(tax_data["avg_combined_sales_tax_pct"])
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("The tax-rate service did not return a combined tax rate.") from error

    if not math.isfinite(rate_percent) or rate_percent < 0:
        raise RuntimeError("The tax-rate service returned an invalid combined tax rate.")

    return {
        "state": state,
        "rate_percent": rate_percent,
        "rates_as_of": tax_data.get("rates_as_of", "date not provided"),
        "state_slug": state_slug,
    }


def calculate_loan_payment(principal, annual_interest_rate_percent, term_months):
    monthly_rate = Decimal(str(annual_interest_rate_percent)) / Decimal("1200")
    if monthly_rate == 0:
        monthly_payment = principal / Decimal(term_months)
    else:
        monthly_payment = principal * monthly_rate / (
            Decimal("1") - (Decimal("1") + monthly_rate) ** -term_months
        )

    total_interest = (monthly_payment * term_months - principal).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    monthly_payment = monthly_payment.quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return monthly_payment, total_interest


st.set_page_config(page_title="Car Shopping Calculator")
st.title("Car Shopping Calculator")
st.caption(
    "Select your state to estimate sales tax, government fees, and calculate an out-the-door "
    "price."
)

state = st.selectbox("State", STATES)
tax_info = None
try:
    tax_info = lookup_sales_tax(state)
except (ValueError, RuntimeError) as error:
    st.error(str(error))

with st.form("car_shopping_form"):
    sale_price = st.number_input(
        "Selling Price ($)", min_value=0.0, value=30000.0, step=500.0, format="%.2f"
    )
    add_ons = st.number_input(
        "Add-ons ($)", min_value=0.0, value=0.0, step=100.0, format="%.2f"
    )
    trade_in_value = st.number_input(
        "Trade-in Value ($)", min_value=0.0, value=0.0, step=100.0, format="%.2f"
    )
    doc_fee = st.number_input(
        "Doc Fee ($)", min_value=0.0, value=175.0, step=25.0, format="%.2f"
    )
    st.number_input(
        "Estimated Sales Tax Rate (%)",
        min_value=0.0,
        value=tax_info["rate_percent"] if tax_info else 0.0,
        format="%.3f",
        disabled=True,
        help=(
            "A state-average combined sales tax estimate. The actual vehicle tax rate "
            "may vary by local jurisdiction and vehicle-specific tax rules."
        ),
    )
    title_fee = st.number_input(
        "Estimated Title Fee ($)",
        min_value=0.0,
        value=TITLE_FEE_ESTIMATES[state],
        step=5.0,
        format="%.2f",
        disabled=True,
        key=f"title_fee_{state}",
        help=(
            "A state-level estimate for a typical passenger vehicle. Oregon's estimate "
            "assumes a 20-39 MPG gasoline vehicle; actual fees vary by vehicle."
            if state == "Oregon"
            else "A state-level estimate for a typical passenger vehicle."
        ),
    )
    registration_fee = st.number_input(
        "Estimated Registration Fee ($)",
        min_value=0.0,
        value=REGISTRATION_FEE_ESTIMATES[state],
        format="%.2f",
        disabled=True,
        key=f"registration_fee_{state}",
        help=(
            "A state-level estimate for a typical new passenger vehicle. Actual "
            "registration, plate, and vehicle-specific fees may vary."
        ),
    )
    submitted = st.form_submit_button("Calculate!", disabled=tax_info is None)

if submitted and tax_info is not None:
    rate = Decimal(str(tax_info["rate_percent"]))
    tax_basis = Decimal(str(sale_price)) + Decimal(str(add_ons))
    sales_tax = (tax_basis * rate / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total = (
        tax_basis
        + Decimal(str(doc_fee))
        + Decimal(str(title_fee))
        + Decimal(str(registration_fee))
        + sales_tax
        - Decimal(str(trade_in_value))
    )
    st.session_state["otd_calculation"] = {
        "state": tax_info["state"],
        "rate": rate,
        "sales_tax": sales_tax,
        "trade_in_value": Decimal(str(trade_in_value)),
        "total": total,
        "rates_as_of": tax_info["rates_as_of"],
        "state_slug": tax_info["state_slug"],
    }

if "otd_calculation" in st.session_state:
    calculation = st.session_state["otd_calculation"]
    st.subheader("Estimated out-the-door price")
    st.metric("Estimated total", f"${calculation['total']:,.2f}")

    st.write(f"**State:** {calculation['state']}")
    st.write(f"**Estimated combined sales tax rate:** {calculation['rate']:.3f}%")
    st.write(f"**Estimated sales tax:** ${calculation['sales_tax']:,.2f}")
    st.write(f"**Trade-in credit:** -${calculation['trade_in_value']:,.2f}")
    st.caption(
        f"Rate data as of {calculation['rates_as_of']}. Source: "
        f"[ReceiptEdit 2026 sales tax data]"
        f"(https://receiptedit.com/api/sales-tax/{calculation['state_slug']}). "
        f"Title fee estimates are for a typical passenger vehicle, based on the "
        f"[US Vehicle Tax Calculator state-fee dataset]"
        f"(https://github.com/abderrahim13224/car-sales-tax-by-state), last "
        f"checked October 7, 2026. Registration estimates use the dataset's "
        f"typical title-and-registration total less its title-fee estimate; Oregon "
        f"uses the state DMV fee page and assumes a 20-39 MPG gasoline passenger "
        f"vehicle. Actual fees vary by vehicle and circumstances. "
        f"The sales tax rate is a state average, not an address-specific rate. "
        f"This estimate taxes the selling price and add-ons; fees are added without tax."
    )

    st.subheader("Financing calculator")
    financing_type = st.radio(
        "Financing type", ["Cash", "Finance"], horizontal=True
    )
    if financing_type == "Cash":
        st.metric("Estimated payment due", f"${calculation['total']:,.2f}")
    else:
        down_payment = st.number_input(
            "Down Payment ($)", min_value=0.0, value=0.0, step=500.0, format="%.2f"
        )
        loan_term = st.number_input(
            "Loan Term (months)", min_value=1, value=60, step=12
        )
        interest_rate = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.0,
            value=6.0,
            step=0.25,
            format="%.2f",
        )
        down_payment_amount = Decimal(str(down_payment))
        if down_payment_amount > calculation["total"]:
            st.error("Down payment cannot exceed the estimated out-the-door price.")
        else:
            amount_financed = calculation["total"] - down_payment_amount
            monthly_payment, total_interest = calculate_loan_payment(
                amount_financed, interest_rate, loan_term
            )
            total_loan_cost = amount_financed + total_interest
            (
                payment_due_col,
                monthly_payment_col,
                interest_col,
                loan_cost_col,
            ) = st.columns(4)
            payment_due_col.metric("Est. payment due", f"${down_payment:,.2f}")
            monthly_payment_col.metric("Est. monthly payment", f"${monthly_payment:,.2f}")
            interest_col.metric("Est. total interest", f"${total_interest:,.2f}")
            loan_cost_col.metric(
                "Est. total loan cost", f"${total_loan_cost:,.2f}"
            )
            st.write(f"**Amount financed:** ${amount_financed:,.2f}")

st.caption(
    "For an exact quote, confirm the tax rate, taxable fees, and registration charges "
    "with your dealer or state tax authority."
)
st.caption(
    "Additonally, when buying a used car, a pre-purchase inspection is highly recommended. "
    "Costs vary and are not included in this estimate."
)
