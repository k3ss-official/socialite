"""Web search via ddgs (DuckDuckGo). Why: free, keyless, no quota account to babysit.
Quirks live in notes/SCRAPING.md."""
from __future__ import annotations

import time

from ddgs import DDGS

SOCIAL_DOMAINS = ("facebook.com", "m.facebook.com", "instagram.com", "tiktok.com")

# Listing/review aggregators — presence here is NOT a website of their own.
AGGREGATOR_DOMAINS = (
    "tripadvisor.", "yell.com", "yelp.", "foursquare.com", "google.com", "bing.com",
    "just-eat.", "justeat.", "ubereats.com", "deliveroo.", "menulog.", "opentable.",
    "restaurantguru.com", "wanderlog.com", "happycow.net", "thefork.", "sluurpy.",
    "cylex", "find-open", "opening-times", "hours.com", "nicelocal.", "allmenus.",
    "menupix.", "booking.com", "agoda.com", "expedia.", "hotels.com", "trip.com",
    "makemytrip.", "tourradar.com", "viator.com", "getyourguide.",
    # directory-scraper sites that masquerade as business websites in results
    "findglocal.com", "wheree.com", "placedigger.", "worldorgs.com", "localmint.",
    "hotfrog.", "brownbook.net", "manta.com", "2findlocal.", "tuugo.", "yellow.place",
    "businessyab.com", "chamberofcommerce.com", "fresha.com", "untappd.com",
    "gov.uk", "checkatrade.", "mapquest.com", "yellowpages.", "thomsonlocal.",
)

# White-label ordering platforms: a "site" on one of these is a template page the
# business doesn't own — evidence FOR qualification, verdict 'template'.
ORDER_PLATFORM_DOMAINS = (
    "foodhub.co.uk", "foodhub.com", "orderyoyo.", "touchtakeaway.net", "flipdish.",
    "scoffable.com", "feedmeonline.co.uk", "order.app", "grubhub.", "mealzo.",
    "whatfoodapp.", "kuick.com", "eattheweb.", "smartrestaurants.",
)


def search(query: str, max_results: int = 10, retries: int = 2) -> list[dict]:
    """Returns [{title, href, body}]. Retries once on transient ddg hiccups."""
    for attempt in range(retries + 1):
        try:
            with DDGS() as d:
                rows = list(d.text(query, max_results=max_results))
            return [{"title": r.get("title", ""), "href": r.get("href") or r.get("link", ""),
                     "body": r.get("body", "")} for r in rows if r.get("href") or r.get("link")]
        except Exception:
            if attempt == retries:
                return []
            time.sleep(2 * (attempt + 1))
    return []


def domain_of(url: str) -> str:
    return url.split("//", 1)[-1].split("/", 1)[0].lower().removeprefix("www.")


def classify(url: str) -> str:
    """social | aggregator | order_platform | candidate_website"""
    d = domain_of(url)
    if any(d == s or d.endswith("." + s) for s in SOCIAL_DOMAINS):
        return "social"
    if any(a in d for a in ORDER_PLATFORM_DOMAINS):
        return "order_platform"
    if any(a in d for a in AGGREGATOR_DOMAINS):
        return "aggregator"
    return "candidate_website"
