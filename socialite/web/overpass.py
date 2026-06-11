"""Locale-scale discovery from OpenStreetMap via Overpass. Why: free, keyless,
and OSM 'website' tags give a first-pass no-website filter before any scraping."""
from __future__ import annotations

import requests

API = "https://overpass-api.de/api/interpreter"


def find_businesses(area_name: str, amenities: list[str], tourism: list[str] | None = None,
                    timeout: int = 60) -> list[dict]:
    """All named businesses of the given types in the area, with their OSM tags."""
    selectors = [f'nwr["amenity"~"^({"|".join(amenities)})$"]["name"](area.a);']
    if tourism:
        selectors.append(f'nwr["tourism"~"^({"|".join(tourism)})$"]["name"](area.a);')
    q = f"""[out:json][timeout:{timeout}];
area["name"="{area_name.split(',')[0].strip()}"]->.a;
({''.join(selectors)});
out tags center;"""
    r = requests.post(API, data={"data": q}, timeout=timeout + 15)
    r.raise_for_status()
    out = []
    for el in r.json().get("elements", []):
        t = el.get("tags", {})
        out.append({
            "name": t.get("name"),
            "category": t.get("amenity") or t.get("tourism") or "business",
            "website_tag": t.get("website") or t.get("contact:website"),
            "phone": t.get("phone") or t.get("contact:phone"),
            "facebook_tag": t.get("contact:facebook"),
            "address": " ".join(filter(None, [t.get("addr:housenumber"), t.get("addr:street"),
                                              t.get("addr:city")])) or None,
            "lat": el.get("lat") or (el.get("center") or {}).get("lat"),
            "lon": el.get("lon") or (el.get("center") or {}).get("lon"),
        })
    return out
