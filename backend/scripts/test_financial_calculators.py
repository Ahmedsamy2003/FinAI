from backend.app.core.financial_calculators import (
    calculate_investment_growth,
)


def main():

    result = calculate_investment_growth(
        initial_investment=1000,
        monthly_contribution=200,
        annual_return=7,
        years=10,
    )

    print("=" * 60)
    print("FINAI INVESTMENT GROWTH CALCULATOR")
    print("=" * 60)

    print(
        f"Total contributed: "
        f"${result['total_contributed']:,.2f}"
    )

    print(
        f"Investment growth: "
        f"${result['investment_growth']:,.2f}"
    )

    print(
        f"Final balance: "
        f"${result['final_balance']:,.2f}"
    )


if __name__ == "__main__":
    main()