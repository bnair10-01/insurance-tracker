from datetime import date

EXPIRING_SOON_DAYS = 30


def compute_status(coverage_start: date | None, coverage_end: date | None, today: date | None = None) -> str:
    today = today or date.today()

    if coverage_start is None:
        return "unknown"
    if coverage_start > today:
        return "upcoming"
    if coverage_end is None:
        return "active"
    if coverage_end < today:
        return "expired"
    if (coverage_end - today).days <= EXPIRING_SOON_DAYS:
        return "expiring_soon"
    return "active"
