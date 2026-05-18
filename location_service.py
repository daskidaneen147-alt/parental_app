# ============================================================
#  backend/location_service.py
#
#  Smart Location System:
#    Android  -->  Real GPS (plyer library)
#    PC       -->  IP geolocation (3 APIs)
#    Default  -->  Bahawalpur (jab sab fail ho)
#
#  Automatically detect karta hai PC hai ya Android!
# ============================================================

import requests
import threading
import platform
from datetime import datetime
from backend.database import execute_query, fetch_all

# ── Default: Bahawalpur ─────────────────────────────────────
current_location = {
    "latitude":  29.3944,
    "longitude": 71.6911,
    "city":      "Bahawalpur",
    "region":    "Punjab",
    "country":   "Pakistan",
    "address":   "Bahawalpur, Punjab, Pakistan",
    "time":      datetime.now().strftime("%I:%M %p"),
    "loaded":    True,
    "source":    "default",   # "gps" | "ip" | "default"
}


# ── Check: Android hai ya PC? ───────────────────────────────
def is_android() -> bool:
    """
    Android pe ANDROID_ARGUMENT environment variable hoti hai.
    PC pe nahi hoti.
    """
    try:
        import os
        return "ANDROID_ARGUMENT" in os.environ or \
               "ANDROID_ROOT" in os.environ
    except Exception:
        return False


# ── GPS: Android ke liye ───────────────────────────────────
def start_gps_android(callback=None):
    """
    Android pe real GPS start karo.
    Plyer library se GPS coordinates milte hain.
    """
    try:
        from plyer import gps

        def on_location(**kwargs):
            lat = kwargs.get("lat", 29.3944)
            lon = kwargs.get("lon", 71.6911)

            # Reverse geocoding se city name lo
            city, region = get_city_from_coords(lat, lon)

            current_location.update({
                "latitude":  lat,
                "longitude": lon,
                "city":      city,
                "region":    region,
                "address":   f"{city}, {region}, Pakistan",
                "time":      datetime.now().strftime("%I:%M %p"),
                "loaded":    True,
                "source":    "gps",
            })
            print(f"[GPS] Real GPS: {lat}, {lon} -- {city}")

            if callback:
                callback(True)

        def on_status(stype, status):
            print(f"[GPS] Status: {stype} = {status}")

        gps.configure(
            on_location = on_location,
            on_status   = on_status,
        )
        gps.start(
            minTime     = 1000,   # 1 second
            minDistance = 0,      # har update pe
        )
        print("[GPS] Android GPS started!")
        return True

    except Exception as e:
        print(f"[GPS] Android GPS failed: {e}")
        return False


# ── IP Location: PC ke liye ────────────────────────────────
def get_location_by_ip() -> bool:
    """
    PC ke liye 3 alag APIs try karo.
    Jo pehle kaam kare woh use hogi.
    """

    # API 1 -- ip-api.com (most reliable)
    try:
        r    = requests.get(
            "http://ip-api.com/json/",
            timeout = 6
        )
        data = r.json()
        if data.get("status") == "success":
            current_location.update({
                "latitude":  float(data.get("lat", 29.3944)),
                "longitude": float(data.get("lon", 71.6911)),
                "city":      data.get("city",       "Bahawalpur"),
                "region":    data.get("regionName", "Punjab"),
                "country":   data.get("country",    "Pakistan"),
                "address":   (
                    f"{data.get('city','Bahawalpur')}, "
                    f"{data.get('regionName','Punjab')}"
                ),
                "time":      datetime.now().strftime("%I:%M %p"),
                "loaded":    True,
                "source":    "ip",
            })
            print(f"[Location] API1: {current_location['address']}")
            return True
    except Exception as e:
        print(f"[Location] API1 failed: {e}")

    # API 2 -- ipwho.is
    try:
        r    = requests.get(
            "https://ipwho.is/",
            timeout = 6,
            headers = {"User-Agent": "Mozilla/5.0"},
        )
        data = r.json()
        if data.get("success"):
            current_location.update({
                "latitude":  float(data.get("latitude",  29.3944)),
                "longitude": float(data.get("longitude", 71.6911)),
                "city":      data.get("city",    "Bahawalpur"),
                "region":    data.get("region",  "Punjab"),
                "country":   data.get("country", "Pakistan"),
                "address":   (
                    f"{data.get('city','Bahawalpur')}, "
                    f"{data.get('region','Punjab')}"
                ),
                "time":      datetime.now().strftime("%I:%M %p"),
                "loaded":    True,
                "source":    "ip",
            })
            print(f"[Location] API2: {current_location['address']}")
            return True
    except Exception as e:
        print(f"[Location] API2 failed: {e}")

    # API 3 -- freeipapi.com
    try:
        r    = requests.get(
            "https://freeipapi.com/api/json",
            timeout = 6
        )
        data = r.json()
        if data.get("latitude"):
            current_location.update({
                "latitude":  float(data.get("latitude",  29.3944)),
                "longitude": float(data.get("longitude", 71.6911)),
                "city":      data.get("cityName",    "Bahawalpur"),
                "region":    data.get("regionName",  "Punjab"),
                "country":   data.get("countryName", "Pakistan"),
                "address":   (
                    f"{data.get('cityName','Bahawalpur')}, "
                    f"{data.get('regionName','Punjab')}"
                ),
                "time":      datetime.now().strftime("%I:%M %p"),
                "loaded":    True,
                "source":    "ip",
            })
            print(f"[Location] API3: {current_location['address']}")
            return True
    except Exception as e:
        print(f"[Location] API3 failed: {e}")

    # Sab fail -- Bahawalpur default
    current_location["time"]   = datetime.now().strftime("%I:%M %p")
    current_location["source"] = "default"
    print("[Location] All failed -- Bahawalpur default")
    return False


# ── Reverse Geocoding: GPS coords se city name ─────────────
def get_city_from_coords(lat: float, lon: float):
    """
    GPS coordinates se city name lo.
    OpenStreetMap Nominatim API use hoti hai (free).
    """
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params  = {
                "lat":            lat,
                "lon":            lon,
                "format":         "json",
                "accept-language":"en",
            },
            headers = {"User-Agent": "GuardianEye-App/1.0"},
            timeout = 5,
        )
        data    = r.json()
        address = data.get("address", {})
        city    = (
            address.get("city")   or
            address.get("town")   or
            address.get("village") or
            "Bahawalpur"
        )
        region  = address.get("state", "Punjab")
        return city, region

    except Exception as e:
        print(f"[Geocoding] Failed: {e}")
        return "Bahawalpur", "Punjab"


# ── Main function: auto detect device ──────────────────────
def fetch_location_async(callback=None):
    """
    Automatically detect karo:
      Android --> GPS
      PC      --> IP
    """
    def _fetch():
        if is_android():
            # Android: Real GPS
            print("[Location] Android detected -- using GPS")
            success = start_gps_android(callback=callback)
            if not success:
                # GPS fail -- IP try karo
                success = get_location_by_ip()
                if callback:
                    callback(success)
        else:
            # PC: IP geolocation
            print("[Location] PC detected -- using IP")
            success = get_location_by_ip()
            if callback:
                callback(success)

    threading.Thread(target=_fetch, daemon=True).start()


# ── Database functions ──────────────────────────────────────
def save_location_to_db(child_id: int):
    """Location history save karo timestamp ke saath."""
    try:
        execute_query(
            """INSERT INTO locations
               (child_id, latitude, longitude, address, logged_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                child_id,
                current_location["latitude"],
                current_location["longitude"],
                current_location["address"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        print(f"[Location] Saved: {current_location['address']}")
    except Exception as e:
        print(f"[Location] Save error: {e}")


def get_location_history(child_id: int) -> list:
    """Last 20 locations database se lo."""
    try:
        return fetch_all(
            """SELECT address, latitude, longitude, logged_at
               FROM locations WHERE child_id=?
               ORDER BY logged_at DESC LIMIT 20""",
            (child_id,)
        )
    except Exception:
        return []


def get_current() -> dict:
    """Current location return karo."""
    return current_location


def get_source_label() -> str:
    """
    Location kahan se aayi -- UI mein dikhane ke liye.
    """
    source = current_location.get("source", "default")
    if source == "gps":
        return "GPS"
    elif source == "ip":
        return "Network"
    else:
        return "Default"


def format_time(dt_string: str) -> str:
    """'2024-01-15 08:30:00' ko '08:30 AM' mein convert karo."""
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%I:%M %p")
    except Exception:
        return dt_string