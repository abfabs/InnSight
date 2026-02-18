# backend/services/travel_planner.py
from __future__ import annotations

from datetime import date
from dateutil.relativedelta import relativedelta

from services.city_tags import CITY_TAGS, cities_with_all_tags


COASTAL_AREAS = {
    "sicily": {
        "Catania",
        "Siracusa",
        "Taormina",
        "Palermo",
        "Cefalù",
        "Trapani",
        "Marsala",
        "San Vito Lo Capo",
        "Noto",
        "Avola",
    },
    "crete": {
        "Chania",
        "Rethymno",
        "Heraklion",
        "Agios Nikolaos",
        "Elounda",
    },
}


def next_month_yyyy_mm(today: date | None = None) -> str:
    today = today or date.today()
    nm = today + relativedelta(months=1)
    return nm.strftime("%Y-%m")


def month_minus_one_year(ym: str) -> str:
    y, m = ym.split("-")
    return f"{int(y) - 1:04d}-{int(m):02d}"


def month_index(ym: str) -> int:
    y, m = ym.split("-")
    return int(y) * 12 + int(m)


def get_city_month_occupancy(db, city: str, month: str) -> float | None:
    doc = db.occupancy_by_month.find_one({"city": city, "level": "city"})
    if not doc:
        return None

    for row in doc.get("monthly_occupancy", []):
        if row.get("month") == month:
            try:
                return float(row.get("occupancy_rate"))
            except (TypeError, ValueError):
                return None
    return None


def get_city_sentiment(db, city: str) -> dict | None:
    doc = db.sentiment_summary.find_one({"city": city, "level": "city"})
    if not doc:
        return None

    return {
        "total_reviews": int(doc.get("total_reviews", 0) or 0),
        "positive": float(doc.get("positive", 0) or 0),
        "neutral": float(doc.get("neutral", 0) or 0),
        "negative": float(doc.get("negative", 0) or 0),
    }


def get_neighborhood_sentiment(db, city: str, neighborhood: str) -> dict | None:
    doc = db.sentiment_summary.find_one(
        {"city": city, "level": "neighborhood", "neighborhood": neighborhood}
    )
    if not doc:
        return None

    return {
        "total_reviews": int(doc.get("total_reviews", 0) or 0),
        "positive": float(doc.get("positive", 0) or 0),
        "neutral": float(doc.get("neutral", 0) or 0),
        "negative": float(doc.get("negative", 0) or 0),
    }


def select_candidate_cities(preferences: set[str], exclude: set[str] | None = None) -> list[str]:
    """
    preferences example: {"beach", "warm"}
    exclude example: {"no_beach"} (future-friendly)
    - If preferences empty -> allow all cities in CITY_TAGS.
    - If preferences has tags -> city must contain all tags.
    - If exclude has tags -> city must NOT contain those tags (if you model them in CITY_TAGS)
      For now: we only treat "no_beach" as "do not require beach" (handled later).
    """
    exclude = exclude or set()

    if not preferences:
        cities = list(CITY_TAGS.keys())
    else:
        cities = cities_with_all_tags(preferences)

    # If in the future you tag cities with "beach", you can exclude them like this:
    # if "no_beach" in exclude:
    #     cities = [c for c in cities if "beach" not in CITY_TAGS.get(c, set())]

    return cities


def plan_trip(db, preferences: set[str], month: str | None = None, exclude_preferences: set[str] | None = None) -> list[dict]:
    """
    Returns city-level candidates sorted by lowest occupancy first (quieter).
    """
    month = month or next_month_yyyy_mm(date.today())
    candidate_cities = select_candidate_cities(preferences, exclude=exclude_preferences)

    rows: list[dict] = []
    for city in candidate_cities:
        occ = get_city_month_occupancy(db, city, month)
        sent = get_city_sentiment(db, city)

        if occ is None or sent is None:
            continue

        rows.append(
            {
                "city": city,
                "month": month,
                "occupancy_rate": occ,
                "sentiment": sent,
            }
        )

    rows.sort(key=lambda r: r["occupancy_rate"])
    return rows


def recommend_neighborhoods(
    db,
    city: str,
    month: str,
    limit: int = 3,
    min_reviews: int = 50,
    preferences: set[str] | None = None,
) -> list[dict]:
    """
    Recommends neighborhoods/areas to stay in (FACTS ONLY).
    Strategy:
    1) Consider ALL neighborhood-level data for the city
    2) Keep only places with meaningful activity (reviews + non-zero occupancy)
    3) If user asked for beach/coast AND we have a coastal allowlist, restrict to it
    4) From those, pick lower occupancy (quieter / more available)
    """
    preferences = preferences or set()
    want_coastal = "beach" in preferences
    avoid_coastal = "no_beach" in preferences

    coastal_allowlist = COASTAL_AREAS.get(city) if want_coastal else None

    cursor = db.occupancy_by_month.find(
        {"city": city, "level": "neighborhood"},
        {"neighborhood": 1, "monthly_occupancy": 1},
    )

    candidates: list[dict] = []

    for d in cursor:
        name = d.get("neighborhood")
        if not name:
            continue

        # If user wants coastal and we have a curated list, restrict to it
        if coastal_allowlist and name not in coastal_allowlist:
            continue

        # If user explicitly avoids beach/coast and we have coastal list, exclude it
        if avoid_coastal and city in COASTAL_AREAS and name in COASTAL_AREAS[city]:
            continue

        occ = None
        for row in d.get("monthly_occupancy", []):
            if row.get("month") == month:
                try:
                    occ = float(row.get("occupancy_rate"))
                except (TypeError, ValueError):
                    occ = None
                break

        if occ is None or occ <= 0:
            continue

        sentiment = get_neighborhood_sentiment(db, city, name)
        if not sentiment:
            continue

        if sentiment["total_reviews"] < min_reviews:
            continue

        candidates.append(
            {
                "neighborhood": name,
                "occupancy_rate": occ,
                "sentiment": sentiment,
            }
        )

    candidates.sort(key=lambda x: x["occupancy_rate"])
    return candidates[: max(1, int(limit))]


def available_months_for_city(db, city: str) -> list[str]:
    """
    Best-effort: return months present in occupancy_by_month city-level doc.
    """
    doc = db.occupancy_by_month.find_one({"city": city, "level": "city"}, {"monthly_occupancy": 1})
    if not doc:
        return []
    months = []
    for row in doc.get("monthly_occupancy", []):
        m = row.get("month")
        if m:
            months.append(m)
    return sorted(set(months))


def closest_available_month(db, city: str, target_month: str) -> str | None:
    months = available_months_for_city(db, city)
    if not months:
        return None
    tgt = month_index(target_month)
    best = None
    best_dist = None
    for m in months:
        try:
            dist = abs(month_index(m) - tgt)
        except Exception:
            continue
        if best is None or dist < best_dist:
            best = m
            best_dist = dist
    return best
