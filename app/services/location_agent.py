from geopy.geocoders import Nominatim
import re


class LocationAgent:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="resqnet_app")

    def extract_possible_location(self, text: str):
        patterns = [
            r"at (.+)",
            r"near (.+)",
            r"in (.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return text

    def get_coordinates(self, text: str):
        try:
            location_query = self.extract_possible_location(text)
            location = self.geolocator.geocode(location_query)

            if location:
                return {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address
                }

            return None

        except Exception as e:
            print("Location error:", e)
            return None