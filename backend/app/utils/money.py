from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

ROUNDING_TOLERANCE = Decimal("0.01")


def parse_money(value) -> Decimal:
    """Parse any value to Decimal. Never use float."""
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    try:
        # Remove currency symbols and commas
        cleaned = str(value).replace("₹", "").replace(",", "").replace(" ", "").strip()
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid monetary value: {value}")


def round_money(amount: Decimal, places: int = 2) -> Decimal:
    """Round to specified decimal places using banker's rounding."""
    if not isinstance(amount, Decimal):
        amount = parse_money(amount)
    return amount.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


def compare_amounts(a, b, tolerance=None) -> tuple:
    """Compare two monetary amounts. Returns (is_match, is_within_tolerance, difference)."""
    if tolerance is None:
        tolerance = ROUNDING_TOLERANCE
    da = parse_money(a)
    db = parse_money(b)
    diff = da - db
    abs_diff = abs(diff)
    is_exact = abs_diff == Decimal("0")
    is_within_tolerance = abs_diff <= parse_money(tolerance)
    return (is_exact, is_within_tolerance, str(diff))


def format_inr(amount) -> str:
    """Format amount as INR string."""
    d = parse_money(amount)
    return f"₹{round_money(d):,.2f}"
