import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="CoastFIRE Calculator")
st.title("CoastFIRE Calculator")
st.write(
    "**CoastFIRE** is the point where your invested savings are sufficient to "
    "grow to your retirement goal by your planned retirement age without any "
    "additional contributions. You can keep contributing to reach CoastFIRE "
    "sooner, then let your investments grow."
)
st.caption(
    "This estimate uses an assumed investment return and inflation rate. "
    "Actual returns, spending, and withdrawal needs will vary."
)

with st.form("coastfire_calculator"):
    current_age = st.number_input(
        "Current age",
        min_value=18,
        max_value=130,
        value=30,
        step=1,
    )
    retirement_age = st.number_input(
        "Planned retirement age",
        min_value=19,
        max_value=100,
        value=65,
        step=1,
    )
    current_assets = st.number_input(
        "Current invested assets ($)",
        min_value=0.0,
        value=100_000.0,
        step=10_000.0,
        format="%.0f",
    )
    annual_spending = st.number_input(
        "Estimated annual spending in retirement ($, today's dollars)",
        min_value=1.0,
        value=60_000.0,
        step=5_000.0,
        format="%.0f",
    )
    monthly_contributions = st.number_input(
        "Monthly investment contributions ($, today's dollars)",
        min_value=0.0,
        value=2_000.0,
        step=100.0,
        format="%.0f",
        help=(
            "Assumed to be invested at the end of each month and to increase "
            "with inflation over time."
        ),
    )
    investment_growth_rate = st.number_input(
        "Estimated annual investment growth rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=7.0,
        step=1.0,
        format="%.0f",
    )
    inflation_rate = st.number_input(
        "Estimated annual inflation rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=3.0,
        step=1.0,
        format="%.0f",
    )
    safe_withdrawal_rate = st.number_input(
        "Safe withdrawal rate (%)",
        min_value=1.0,
        max_value=10.0,
        value=4.0,
        step=1.0,
        format="%.0f",
        help="Used to estimate the portfolio needed at retirement.",
    )
    submitted = st.form_submit_button("Calculate CoastFIRE")

if submitted:
    if retirement_age <= current_age:
        st.error("Planned retirement age must be greater than current age.")
    else:
        nominal_growth = investment_growth_rate / 100
        inflation = inflation_rate / 100
        real_growth = (1 + nominal_growth) / (1 + inflation) - 1
        years_to_retirement = int(retirement_age - current_age)
        months_to_retirement = years_to_retirement * 12
        real_monthly_growth = (1 + real_growth) ** (1 / 12) - 1
        retirement_target = annual_spending / (safe_withdrawal_rate / 100)
        coastfire_number = retirement_target / (
            (1 + real_growth) ** years_to_retirement
        )

        projected_ages = [int(current_age)]
        net_worth_after_coastfire = [float(current_assets)]
        net_worth_with_contributions = [float(current_assets)]
        coastfire_numbers = [coastfire_number]
        coastfire_assets = float(current_assets)
        continued_assets = float(current_assets)
        coastfire_reached = current_assets >= coastfire_number
        months_until_coastfire = 0 if coastfire_reached else None

        for month in range(1, months_to_retirement + 1):
            coastfire_assets *= 1 + real_monthly_growth
            continued_assets *= 1 + real_monthly_growth
            continued_assets += monthly_contributions
            if not coastfire_reached:
                coastfire_assets += monthly_contributions

            remaining_years = (months_to_retirement - month) / 12
            coastfire_number_at_age = retirement_target / (
                (1 + real_growth) ** remaining_years
            )
            if not coastfire_reached and coastfire_assets >= coastfire_number_at_age:
                coastfire_reached = True
                months_until_coastfire = month

            if month % 12 == 0:
                projected_ages.append(int(current_age) + month // 12)
                net_worth_after_coastfire.append(coastfire_assets)
                net_worth_with_contributions.append(continued_assets)
                coastfire_numbers.append(coastfire_number_at_age)

        st.subheader("Your CoastFIRE estimate")
        st.metric(
            f"CoastFIRE number at age {int(current_age)}",
            f"${coastfire_number:,.0f}",
        )
        st.write(
            f"Estimated portfolio needed at age {int(retirement_age)}: "
            f"${retirement_target:,.0f} in today's dollars."
        )
        st.write(f"Estimated real growth rate: {real_growth * 100:.2f}% per year.")

        chart_data = pd.DataFrame(
            {
                "Age": projected_ages,
                "Net worth after CoastFIRE": net_worth_after_coastfire,
                "Net worth with continued contributions": net_worth_with_contributions,
                "CoastFIRE number": coastfire_numbers,
                "FIRE number": [retirement_target] * len(projected_ages),
            }
        )
        st.subheader("Projected net worth by age")
        chart_long = chart_data.melt(
            id_vars="Age", var_name="Projection", value_name="Net worth"
        )
        age_ticks = list(range(int(current_age), int(retirement_age) + 1))
        age_hover = alt.selection_point(
            fields=["Age"],
            nearest=True,
            on="pointerover",
            clear="pointerout",
            empty=False,
        )
        projection_lines = (
            alt.Chart(chart_long)
            .mark_line()
            .encode(
                x=alt.X(
                    "Age:Q",
                    axis=alt.Axis(values=age_ticks, format="d", title="Age"),
                    scale=alt.Scale(
                        domain=[int(current_age), int(retirement_age)]
                    ),
                ),
                y=alt.Y(
                    "Net worth:Q",
                    axis=alt.Axis(format="$,.0f"),
                    title="Net worth ($, today's dollars)",
                ),
                color=alt.Color("Projection:N", title=""),
            )
        )
        hover_targets = (
            alt.Chart(chart_data)
            .mark_point(opacity=0, size=100)
            .encode(
                x="Age:Q",
                y=alt.value(0),
                tooltip=[
                    alt.Tooltip("Age:Q", format=".0f"),
                    alt.Tooltip("Net worth after CoastFIRE:Q", format="$,.0f"),
                    alt.Tooltip(
                        "Net worth with continued contributions:Q",
                        format="$,.0f",
                    ),
                    alt.Tooltip("CoastFIRE number:Q", format="$,.0f"),
                    alt.Tooltip("FIRE number:Q", format="$,.0f"),
                ],
            )
            .add_params(age_hover)
        )
        st.altair_chart(
            alt.layer(projection_lines, hover_targets), width="stretch"
        )
        st.caption(
            "Compare projected net worth if monthly contributions stop at the "
            "CoastFIRE milestone with net worth if contributions continue through "
            "retirement. The CoastFIRE number shows the portfolio needed at each "
            "age to reach the FIRE number by retirement. Values are in today's dollars."
        )

        if current_assets >= coastfire_number:
            st.success(
                "You have already achieved CoastFIRE based on these assumptions. "
                "Your current invested assets are at or above your CoastFIRE number."
            )
        else:
            if months_until_coastfire is not None:
                years_until_coastfire, remaining_months = divmod(
                    months_until_coastfire, 12
                )
                coastfire_age = current_age + months_until_coastfire / 12
                duration = []
                if years_until_coastfire:
                    duration.append(
                        f"{years_until_coastfire} "
                        f"{'year' if years_until_coastfire == 1 else 'years'}"
                    )
                if remaining_months:
                    duration.append(
                        f"{remaining_months} "
                        f"{'month' if remaining_months == 1 else 'months'}"
                    )
                st.info(
                    f"You have not achieved CoastFIRE yet. Based on your "
                    f"contributions and assumptions, you are projected to reach "
                    f"CoastFIRE in about {' and '.join(duration)}, "
                    f"at approximately age {coastfire_age:.1f}."
                )
            else:
                st.warning(
                    "You are not projected to reach CoastFIRE by your planned "
                    "retirement age with these assumptions. Consider increasing "
                    "your contributions, adjusting your retirement plan, or "
                    "reviewing your estimates."
                )

        st.caption(
            "The CoastFIRE number is calculated in today's dollars using the "
            "inflation-adjusted growth rate and the portfolio target implied by "
            "your spending and safe withdrawal rate. Contributions are assumed "
            "to be made at each month-end in today's dollars."
        )
