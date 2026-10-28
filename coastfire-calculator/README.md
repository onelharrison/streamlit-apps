# CoastFIRE Calculator

A Streamlit app that estimates the CoastFIRE number for a user's current age
and whether their current invested assets have reached it. CoastFIRE is the
point at which existing investments can grow to a retirement portfolio goal
without further contributions.

The calculator uses the user's current age, planned retirement age, invested
assets, estimated annual retirement spending, monthly contributions, investment
growth rate, inflation rate, and safe withdrawal rate. If the user has not yet
reached CoastFIRE, it projects how many years it may take with the entered
monthly contributions, up to the planned retirement age. Contributions are
assumed to be made at each month-end and to increase with inflation. A chart
compares projected net worth by age if contributions stop at the CoastFIRE
milestone versus if they continue through retirement, alongside the CoastFIRE
number over time and the FIRE number. The chart uses annual age increments and
includes the current and planned retirement ages on its x-axis.

All results are estimates, not financial advice or guarantees. Actual investment
returns, inflation, spending, and retirement outcomes can differ.

## Run locally

Use Python 3.11, install dependencies, and start Streamlit:

```powershell
py -3.11 -m pip install -r requirements.txt
py -3.11 -m streamlit run app.py
```

Dependencies are listed in `requirements.txt`; `.python-version` selects
Python 3.11.
