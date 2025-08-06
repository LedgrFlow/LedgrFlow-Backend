from ledger_cli import LedgerParser, LedgerAnalyst

default_opts = {
    "taxes": {
        "IVA": {"percentage": 0.16},
        "RET_ISR": {"percentage": 0.10},
    },
}


def normalize_taxes(metadata: dict, opts: dict) -> dict:
    taxes_opt = opts.get("taxes")
    raw_taxes = metadata.get("taxes", taxes_opt)

    if not isinstance(raw_taxes, dict):
        return taxes_opt or {}

    normalized_taxes = {}

    for key, value in raw_taxes.items():
        # Caso válido: ya tiene estructura {'percentage': value}
        if isinstance(value, dict) and "percentage" in value:
            normalized_taxes[key] = value

        # Caso simplificado: valor numérico, lo convertimos
        elif isinstance(value, (int, float)):
            normalized_taxes[key] = {"percentage": value}

        else:
            # Valor no válido, intentamos usar taxes_opt si existe
            return taxes_opt or {}

    return normalized_taxes


def parse_ledger(
    file: str = None, file_accounts: str = None, opts: dict = default_opts
):
    """Parsea un archivo de ledger y devuelve un diccionario con los datos o None si fallan."""

    ledger = None
    transactions = None
    accounts = None
    accounts_advance = None
    metadata = None
    parents = None
    transactions_resolved = None

    try:
        ledger = LedgerParser(
            file=file,
            file_accounts=file_accounts,
            parents_accounts={
                "Assets": "Assets",
                "Liabilities": "Liabilities",
                "Equity": "Equity",
                "Income": "Income",
                "Expenses": "Expenses",
            },
        )
    except Exception as e:
        print(f"[ERROR] ledger instantiation failed: {e}")
        return None, None, None, None, None, None, None

    try:
        transactions = ledger.parse_transactions()
    except Exception as e:
        print(f"[ERROR] parse_transactions failed: {e}")

    try:
        accounts = ledger.parse_accounts()
    except Exception as e:
        print(f"[ERROR] parse_accounts failed: {e}")

    try:
        accounts_advance = ledger.parse_accounts_advance()
    except Exception as e:
        print(f"[ERROR] parse_accounts_advance failed: {e}")

    try:
        metadata = ledger.parse_metadata_yaml()
    except Exception as e:
        print(f"[ERROR] parse_metadata_yaml failed: {e}")

    try:
        parents = ledger.detected_parents_accounts()
    except Exception as e:
        print(f"[ERROR] detected_parents_accounts failed: {e}")

    try:

        taxes = normalize_taxes(metadata, opts)
        if taxes:
            transactions_resolved = ledger.resolve(
                transactions=transactions, tax_definitions=taxes
            )
        else:
            print(f"[LOG] Skipped resolve due to missing taxes.")

        if transactions is not None and opts and "taxes" in opts:
            transactions_resolved = ledger.resolve(
                transactions=transactions, tax_definitions=opts["taxes"]
            )
        else:
            print(f"[LOG] Skipped resolve due to missing transactions or taxes.")
            transactions_resolved = transactions
    except Exception as e:
        print(f"[ERROR] resolve failed: {e}")

    return (
        ledger,
        transactions,
        accounts,
        accounts_advance,
        metadata,
        parents,
        transactions_resolved,
    )


def calculates_ledger(
    file: str = None, file_accounts: str = None, opts: dict = default_opts
):
    """Calcula los balances de un archivo de ledger"""

    balances = None
    balances_by_parents = None
    state_results = None
    balances_by_details = None
    period = None

    try:
        ledger, _, accounts, _, _, _, transactions_resolved = parse_ledger(
            file, file_accounts, opts
        )
    except Exception as e:
        print(f"[ERROR] parse_ledger failed: {e}")
        return None, None, None, None, None

    try:
        if ledger and transactions_resolved and accounts:
            balances = ledger.calculate_balances(
                transactions_json=transactions_resolved, reference=accounts
            )
        else:
            print(f"[LOG] Skipped calculate_balances due to missing data")
    except Exception as e:
        print(f"[ERROR] calculate_balances failed: {e}")

    try:
        if ledger and transactions_resolved:
            balances_by_parents = ledger.calculate_balances_by_parents_accounts(
                transactions_json=transactions_resolved
            )
        else:
            print(
                f"[LOG] Skipped calculate_balances_by_parents_accounts due to missing data"
            )
    except Exception as e:
        print(f"[ERROR] calculate_balances_by_parents_accounts failed: {e}")

    try:
        if ledger and balances:
            state_results = ledger.calculate_status_results(balances)
        else:
            print(f"[LOG] Skipped calculate_status_results due to missing balances")
    except Exception as e:
        print(f"[ERROR] calculate_status_results failed: {e}")

    try:
        if ledger and transactions_resolved:
            balances_by_details = ledger.calculate_balances_by_details_accounts(
                transactions_json=transactions_resolved
            )
        else:
            print(
                f"[LOG] Skipped calculate_balances_by_details_accounts due to missing data"
            )
    except Exception as e:
        print(f"[ERROR] calculate_balances_by_details_accounts failed: {e}")

    try:
        if ledger and transactions_resolved:
            period = ledger.get_date_range(transactions_json=transactions_resolved)
        else:
            print(f"[LOG] Skipped get_date_range due to missing data")
    except Exception as e:
        print(f"[ERROR] get_date_range failed: {e}")

    return balances, balances_by_parents, state_results, balances_by_details, period


def analyze_ledger(
    file: str = None, file_accounts: str = None, opts: dict = default_opts
):
    """Analiza un archivo de ledger"""

    daily = None
    pie_expenses = None
    pie_incomes = None
    assets_summary = None
    liabilities_summary = None
    balance_by_day = None
    accounts_used = None
    detected_alerts = None
    cashflow_by_month = None
    expenses_trends = None
    monthly_growth_rates = None
    monthly_expense_ratio = None
    moving_average = None
    trend_slope = None
    predicted_months = None
    extreme_months = None
    classify_months = None
    income_dependency = None
    cumulative_net_income = None
    months = []

    try:
        _, _, accounts, _, _, parents, transactions_resolved = parse_ledger(
            file, file_accounts, opts
        )
    except Exception as e:
        print(f"[ERROR] parse_ledger failed: {e}")
        return (None,) * 20

    try:
        analyze_ledger = LedgerAnalyst(
            transactions=transactions_resolved,
            accounts=accounts,
            income_parents=(parents["Income"], "Income"),
            expense_parents=[parents["Expenses"], "Expenses"],
            asset_parents={parents["Assets"], "Assets"},
            liability_parents=(parents["Liabilities"], "Liabilities"),
        )
    except Exception as e:
        print(f"[ERROR] LedgerAnalyst instantiation failed: {e}")
        return (None,) * 20

    def safe_call(method, name):
        try:
            return method()
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            return None

    daily = safe_call(
        analyze_ledger.get_daily_incomes_expenses, "get_daily_incomes_expenses"
    )
    pie_expenses = safe_call(analyze_ledger.get_expenses_pie, "get_expenses_pie")
    pie_incomes = safe_call(analyze_ledger.get_incomes_pie, "get_incomes_pie")
    assets_summary = safe_call(analyze_ledger.get_assets_summary, "get_assets_summary")
    liabilities_summary = safe_call(
        analyze_ledger.get_liabilities_summary, "get_liabilities_summary"
    )
    balance_by_day = safe_call(analyze_ledger.get_balance_by_day, "get_balance_by_day")
    accounts_used = safe_call(analyze_ledger.get_accounts_used, "get_accounts_used")
    detected_alerts = safe_call(
        analyze_ledger.detect_unusual_expenses, "detect_unusual_expenses"
    )
    cashflow_by_month = safe_call(
        analyze_ledger.get_cashflow_by_month, "get_cashflow_by_month"
    )
    expenses_trends = safe_call(
        analyze_ledger.get_expense_trends_by_category, "get_expense_trends_by_category"
    )
    monthly_growth_rates = safe_call(
        analyze_ledger.get_monthly_growth_rates, "get_monthly_growth_rates"
    )
    monthly_expense_ratio = safe_call(
        analyze_ledger.get_monthly_expense_ratio, "get_monthly_expense_ratio"
    )
    moving_average = safe_call(analyze_ledger.get_moving_average, "get_moving_average")
    trend_slope = safe_call(analyze_ledger.get_trend_slope, "get_trend_slope")
    predicted_months = safe_call(
        analyze_ledger.predict_future_months, "predict_future_months"
    )
    extreme_months = safe_call(analyze_ledger.get_extreme_months, "get_extreme_months")
    classify_months = safe_call(
        analyze_ledger.classify_months_by_balance, "classify_months_by_balance"
    )
    income_dependency = safe_call(
        analyze_ledger.get_income_dependency_ratio, "get_income_dependency_ratio"
    )
    cumulative_net_income = safe_call(
        analyze_ledger.get_cumulative_net_income, "get_cumulative_net_income"
    )

    try:
        if cashflow_by_month:
            months = [item["month"] for item in cashflow_by_month]
        else:
            print(f"[LOG] Skipped extracting months due to missing cashflow_by_month")
    except Exception as e:
        print(f"[ERROR] Extracting months from cashflow_by_month failed: {e}")

    return (
        daily,
        pie_expenses,
        pie_incomes,
        assets_summary,
        liabilities_summary,
        balance_by_day,
        accounts_used,
        detected_alerts,
        cashflow_by_month,
        expenses_trends,
        monthly_growth_rates,
        monthly_expense_ratio,
        moving_average,
        trend_slope,
        predicted_months,
        extreme_months,
        classify_months,
        income_dependency,
        cumulative_net_income,
        months,
    )


def analyze_ledger_compare(
    file: str = None,
    file_accounts: str = None,
    month1: str = None,
    month2: str = None,
    opts: dict = default_opts,
):
    """Analiza un archivo de ledger"""

    _, _, accounts, _, _, _, transactions_resolved = parse_ledger(
        file, file_accounts, opts
    )

    analyze_ledger = LedgerAnalyst(
        transactions=transactions_resolved,
        accounts=accounts,
        income_parents=("Income", "Income"),
        expense_parents=["Expenses", "Expenses"],
        asset_parents={"Assets", "Assets"},
        liability_parents=("Liabilities", "Liabilities"),
    )

    compare_result = analyze_ledger.compare_months(month1=month1, month2=month2)
    return compare_result


def analyze_ledger_alerts(
    file=None, file_accounts=None, threshold=1.5, opts: dict = default_opts
):
    """Analiza un archivo de ledger"""

    _, _, accounts, _, _, _, transactions_resolved = parse_ledger(
        file, file_accounts, opts
    )

    analyze_ledger = LedgerAnalyst(
        transactions=transactions_resolved,
        accounts=accounts,
        income_parents=("Income", "Income"),
        expense_parents=["Expenses", "Expenses"],
        asset_parents={"Assets", "Assets"},
        liability_parents=("Liabilities", "Liabilities"),
    )

    alerts = analyze_ledger.detect_unusual_expenses(threshold=threshold)
    return alerts
