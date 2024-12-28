


import streamlit as st

def calculate_inr_from_usd(
    amount_usd: float,
    paypal_fee_percent: float,
    paypal_fixed_fee_usd: float,
    tax_percent: float,
    usd_to_inr_rate: float
) -> float:
    """
    Given an amount in USD, calculates the final INR amount
    after PayPal fees, fixed fee, tax, and currency conversion.
    """
    # 1. Deduct PayPal percentage fee
    net_after_paypal_percent = amount_usd * (1 - paypal_fee_percent / 100)
    # 2. Deduct PayPal fixed fee
    net_after_paypal_fees = net_after_paypal_percent - paypal_fixed_fee_usd
    # 3. Deduct tax (e.g., TDS) - apply on remaining USD
    net_after_tax_usd = net_after_paypal_fees * (1 - tax_percent / 100)
    # 4. Convert remaining USD to INR
    final_inr = net_after_tax_usd * usd_to_inr_rate
    return final_inr

def calculate_usd_for_target_inr(
    target_inr: float,
    paypal_fee_percent: float,
    paypal_fixed_fee_usd: float,
    tax_percent: float,
    usd_to_inr_rate: float
) -> float:
    """
    Given a target INR amount to receive, determines 
    how many USD should be invoiced such that after 
    fees, tax, and currency conversion, we end up with target_inr.
    
    Solves:
      ( (Y * (1 - p) ) - f ) * (1 - t) * R = target_inr
    Where
       Y = amount_invoiced_in_usd
       p = paypal_fee_percent / 100
       f = paypal_fixed_fee_usd
       t = tax_percent / 100
       R = usd_to_inr_rate
    """
    p = paypal_fee_percent / 100
    t = tax_percent / 100
    R = usd_to_inr_rate
    f = paypal_fixed_fee_usd

    # Solve step-by-step:
    # ( (Y*(1 - p)) - f ) * (1 - t) * R = target_inr
    # => ( (Y*(1 - p)) - f ) * (1 - t) = target_inr / R
    # => (Y*(1 - p)) - f = (target_inr / R) / (1 - t)
    # => Y*(1 - p) = (target_inr / (R*(1 - t))) + f
    # => Y = [ (target_inr / (R*(1 - t))) + f ] / (1 - p)

    denominator = R * (1 - t)
    if denominator == 0 or (1 - p) == 0:
        st.error("Invalid parameters. Please check your rates/fees.")
        return 0.0

    required_usd = (
        (target_inr / denominator) + f
    ) / (1 - p)

    return required_usd


def main():
    st.title("PayPal Fee & Currency Conversion Calculator")
    st.write(
        """
        This tool helps you figure out how much INR you'll receive for a given USD amount
        in your **PayPal Business (India)** account, and also how much USD to request to 
        finally get a specific INR after fees, taxes, and conversion.
        """
    )

    # Sidebar inputs for fees, rates, etc.
    st.sidebar.header("Configure Fees & Rates")
    paypal_fee_percent = st.sidebar.number_input(
        "PayPal Fee Percentage (%)",
        min_value=0.0,
        value=4.4,
        step=0.1,
        help="Typical range ~4.4% for international transactions. Adjust as per your contract."
    )
    paypal_fixed_fee_usd = st.sidebar.number_input(
        "PayPal Fixed Fee (USD)",
        min_value=0.0,
        value=0.30,
        step=0.01,
        help="Typical fixed fee for PayPal. Adjust as needed."
    )
    tax_percent = st.sidebar.number_input(
        "Tax/TDS (%)",
        min_value=0.0,
        value=0.0,
        step=0.1,
        help="Tax on the PayPal net amount, if applicable. E.g., TDS 1-5% etc."
    )
    usd_to_inr_rate = st.sidebar.number_input(
        "USD to INR Exchange Rate",
        min_value=1.0,
        value=82.0,
        step=0.1,
        help="Current or assumed USD → INR rate."
    )

    st.subheader("1. USD → INR Calculation")
    st.write("**How much INR will I receive if someone sends me X USD?**")
    with st.form("usd_to_inr"):
        usd_amount = st.number_input(
            "Enter amount in USD",
            min_value=0.0,
            value=100.0,
            step=1.0
        )
        submitted_1 = st.form_submit_button("Calculate INR")
        if submitted_1:
            inr_received = calculate_inr_from_usd(
                amount_usd=usd_amount,
                paypal_fee_percent=paypal_fee_percent,
                paypal_fixed_fee_usd=paypal_fixed_fee_usd,
                tax_percent=tax_percent,
                usd_to_inr_rate=usd_to_inr_rate
            )
            st.success(f"You will receive approximately ₹{inr_received:,.2f}")

    st.markdown("---")

    st.subheader("2. Target INR → Required USD Calculation")
    st.write("**I want to receive X INR in my bank. How much USD should I invoice so that after all fees I get that INR?**")
    with st.form("inr_to_usd"):
        inr_target = st.number_input(
            "Enter target amount in INR",
            min_value=0.0,
            value=10000.0,
            step=100.0
        )
        submitted_2 = st.form_submit_button("Calculate USD")
        if submitted_2:
            usd_required = calculate_usd_for_target_inr(
                target_inr=inr_target,
                paypal_fee_percent=paypal_fee_percent,
                paypal_fixed_fee_usd=paypal_fixed_fee_usd,
                tax_percent=tax_percent,
                usd_to_inr_rate=usd_to_inr_rate
            )
            st.success(f"To receive ₹{inr_target:,.2f}, you should request about ${usd_required:,.2f}.")

if __name__ == "__main__":
    main()
