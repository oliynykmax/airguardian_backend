import requests
from math import sqrt
from .database import SessionLocal
from .models import Violation
import os
import json
from datetime import datetime

def fetch_drones():
    try:
        response = requests.get(DRONES_API_URL)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        else:
            print("Warning: API did not return a list as expected.")
            return [] # Return an empty list if the format is wrong

    except requests.RequestException as e:
        print("Error during request to fetch drones:", e)
        return [] # Return an empty list on failure
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the response.")
        return []


DRONES_API_URL = "https://drones-api.hive.fi/drones"
USERS_API_URL_TEMPLATE = os.getenv("USERS_API_URL_TEMPLATE")

def is_in_nfz(x, y, radius=1000):
    return sqrt(x**2 + y**2) <= radius

def fetch_and_store_violations():
    session = SessionLocal()
    violations_added = 0
    try:
        # 1. Fetch drone data
        drones = fetch_drones()
        if not drones:
            print("Failed to fetch drones or no drones returned.")
            return 0

        if isinstance(drones, list):
            for drone in drones:
                # The API fields are: owner_id, x, y, z
                x, y, z = drone["x"], drone["y"], drone["z"]
                owner_id = drone["owner_id"]
                drone_id = owner_id  # Use owner_id as drone_id if no other unique identifier

                print(f"Drone: owner_id={owner_id}, x={x}, y={y}, z={z}")

                # 2. Check for NFZ violation
                if is_in_nfz(x, y):
                    # 3. Fetch owner info
                    owner_url = f"{USERS_API_URL_TEMPLATE.rstrip('/')}/{owner_id}"
                    try:
                        owner_resp = requests.get(owner_url, timeout=5)
                        owner_resp.raise_for_status()
                        owner = owner_resp.json()
                    except Exception as e:
                        print(f"Failed to fetch owner info for {owner_id}: {e}")
                        continue

                    # 4. Store violation in DB
                    violation = Violation(
                    	timestamp=datetime.now(),
                        drone_id=drone_id,
                        position_x=x,
                        position_y=y,
                        position_z=z,
                        owner_first_name=owner.get("firstName", ""),
                        owner_last_name=owner.get("lastName", ""),
                        owner_ssn=owner.get("socialSecurityNumber", ""),
                        owner_phone=owner.get("phoneNumber", ""),
                    )
                    session.add(violation)
                    violations_added += 1
            session.commit()
            print(f"Added {violations_added} violations to the database.")
        else:
            print("No violations detected.")
            return violations_added
    except Exception as e:
        print("Error processing drones:", e)
        print("Rolling back the session due to an error.")
        session.rollback()
        return 0
    finally:
        session.close()
