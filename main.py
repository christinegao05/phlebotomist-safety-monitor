import requests
from shapely.geometry import shape
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import time

# we'll add to set upon alerting, and remove when they've re-enter safe zone
alerted_safety = set()
alerted_api = set()

# gets my hidden email + pw 
load_dotenv()

def check_clinician(clinicianID):

    url = f"https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus/{clinicianID}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # throws exception if status not right
        
        data = response.json()
        # import json
        # print(json.dumps(data))

        # idx 0 = clinician loc
        # idx 1 = safe range
        
        clinician_loc = None
        safe_zones = []

        for feature in data.get('features', []):
            geo_type = feature['geometry']['type']
            if geo_type == "Point":
                clinician_loc = shape(feature['geometry'])
            elif geo_type in ["Polygon", "MultiPolygon"]:
                safe_zones.append(shape(feature['geometry']))
        
        if not clinician_loc or not safe_zones:
            print("Missing clinician or safe zone data")
            return

        # clinician is safe if their loc is within the bounding zone
        is_safe = any(zone.intersects(clinician_loc) for zone in safe_zones)

        if not is_safe:
            print(f"Clinician {clinicianID} is outside the safe zone.")
            # alert if we haven't already
            if clinicianID not in alerted_safety:
                alert(clinicianID, "is outside of safe zone")
                alerted_safety.add(clinicianID)
        else:
            print(f"Clinician {clinicianID} is inside the safe zone.")
            # if  previously outside safe zone, remove from alerted set
            if clinicianID in alerted_safety:
                alerted_safety.remove(clinicianID)

        # if we reach here, API worked
        if clinicianID in alerted_api:
            alerted_api.remove(clinicianID)
    
    except Exception as e:
        print(f"Clinician {clinicianID} API error")
        if clinicianID not in alerted_api:    
            alert(clinicianID, "endpoint did not return")
            alerted_api.add(clinicianID)


def alert(clinicianID, reason):
    # send email
    sender = os.getenv("SENDER_EMAIL") 
    passkey = os.getenv("SENDER_PASSKEY")
    # receiver = "wyubyf+6z2k5ndkdunh8@sharklasers.com"
    receiver = "coding-challenges+alerts@sprinterhealth.com"

    alert_msg = EmailMessage()
    alert_msg.set_content(f"Clinician {clinicianID} {reason}.")
    alert_msg['Subject'] = f"ALERT: Clinician in danger!"
    alert_msg['From'] = sender
    alert_msg['To'] = receiver

    # port 465 is for SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, passkey)
        server.send_message(alert_msg)

    print(f"Sent email alert for clinician {clinicianID}.")


if __name__ == "__main__":
    # run this for 1 hr with 1 minute intervals
    for minute in range (60):
        print(f"\n--- Check {minute + 1} of {60} ({time.strftime('%H:%M:%S')}) ---")
    
        for i in range(1, 8):    
            check_clinician(i)

        if minute < 59:
            time.sleep(60)
