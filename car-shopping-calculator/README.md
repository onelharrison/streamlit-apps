# Car Shopping Calculator

A Streamlit app that estimates vehicle sales tax and out-the-door price from the
selected state and entered vehicle costs, including an optional trade-in credit.
After calculating the out-the-door price, choose cash or use the separate
financing calculator to estimate a monthly payment, total loan interest, and
total loan cost from the down payment, term, and interest rate. Financing
estimates update as the loan inputs change. State tax, fee, and loan figures
are estimates; local rules, lender terms, and vehicle details can change the
actual amount.

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Select **Create app**, then choose the repository and branch.
4. Set the main file path to `app.py` and deploy.

Dependencies are listed in `requirements.txt`, and `.python-version` selects
Python 3.11. No app secrets are required.
