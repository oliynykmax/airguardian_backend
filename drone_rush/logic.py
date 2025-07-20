import requests
from math import sqrt
from .database import SessionLocal
from .models import Violation
import os
import json
from datetime import datetime
import logging

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def fetch_drones():
    try:
        response = requests.get(DRONES_API_URL)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        else:
            logger.warning("API did not return a list as expected.")
            return []

    except requests.RequestException as e:
        logger.error(f"Error during request to fetch drones: {e}")
        return []
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from the response.")
        return []


DRONES_API_URL = "https://drones-api.hive.fi/drones"
USERS_API_URL_TEMPLATE = os.getenv("USERS_API_URL_TEMPLATE")

def is_in_nfz(x, y, radius=1000):
    return sqrt(x**2 + y**2) <= radius

def fetch_and_store_violations():
    if not USERS_API_URL_TEMPLATE:
        logger.error("USERS_API_URL_TEMPLATE is not set.")
        return 0
    if not DRONES_API_URL:
        logger.error("DRONES_API_URL is not set.")
        return 0
    session = SessionLocal()
    violations_added = 0
    try:
        drones = fetch_drones()
        if not drones:
            logger.warning("Failed to fetch drones or no drones returned.")
            return 0
        if isinstance(drones, list):
            for drone in drones:
                x, y, z = drone["x"], drone["y"], drone["z"]
                owner_id = drone["owner_id"]
                drone_id = drone["id"]
                logger.info(f"Drone: owner_id={owner_id}, x={x}, y={y}, z={z}")
                if is_in_nfz(x, y):
                    owner_url = f"{USERS_API_URL_TEMPLATE.rstrip('/')}/{owner_id}"
                    try:
                        owner_resp = requests.get(owner_url, timeout=5)
                        owner_resp.raise_for_status()
                        owner = owner_resp.json()
                    except Exception as e:
                        logger.error(f"Failed to fetch owner info for {owner_id}: {e}")
                        continue

                    # 4. Store violation in DB
                    violation = Violation(
                        timestamp=datetime.now(),
                        drone_id=drone_id,
                        position_x=x,
                        position_y=y,
                        position_z=z,
                        owner_first_name=owner["first_name"],
                        owner_last_name=owner["last_name"],
                        owner_ssn=owner["social_security_number"],
                        owner_phone=owner["phone_number"],
                        owner_email=owner["email"],
                        owner_purchase_date=owner["purchased_at"]
                    )
                    session.add(violation)
                    violations_added += 1
            session.commit()
            logger.info(f"Added {violations_added} violations to the database.")
        else:
            logger.info("No violations detected.")
            return violations_added
    except Exception as e:
        logger.error(f"Error processing drones: {e}")
        logger.error("Rolling back the session due to an error.")
        session.rollback()
        return 0
    finally:
        session.close()
