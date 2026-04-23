import requests
from shapely.geometry import shape
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import time

# we'll add to set upon alerting, and remove when they've re-enter safe zone
alerted = set()

# gets my hidden email + pw 
load_dotenv()

def check_clinician(clinicianID):

    url = f"https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus/{clinicianID}"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Could not find clinician {clinicianID}")
            return
        
        data = response.json()
        # import json
        # print(json.dumps(data))

        # idx 0 = clinician loc
        # idx 1 = safe range
        clinician_loc = shape(data['features'][0]['geometry'])
        safe_zone = shape(data['features'][1]['geometry'])

        # clinician is safe if their loc is within the bounding zone
        is_safe = safe_zone.intersects(clinician_loc)

        if not is_safe:
            print(f"Clinician {clinicianID} is outside the safe zone.")
            # alert if we haven't already
            if clinicianID not in alerted:
                alert(clinicianID, True)
        else:
            print(f"Clinician {clinicianID} is inside the safe zone.")
            # if  previously outside safe zone, remove from alerted set
            if clinicianID in alerted:
                alerted.remove(clinicianID)
    except Exception as e:
        alert(clinicianID, False)


def alert(clinicianID, outside_type):
    # send email
    sender = os.getenv("SENDER_EMAIL") 
    passkey = os.getenv("SENDER_PASSKEY")
    receiver = "coding-challenges+alerts@sprinterhealth.com"
    if outside_type:
        reason = "is outside of safe zone"
    else:
        reason = "endpoint did not return"
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

    # add to alerted set
    if outside_type:
        alerted.add(clinicianID)


if __name__ == "__main__":
    # run this for 1 hr with 1 minute intervals
    for minute in range (60):
        print(f"\n--- Check {minute + 1} of {60} ({time.strftime('%H:%M:%S')}) ---")
    
        for i in range(1, 8):    
            check_clinician(i)

        if minute < 59:
            time.sleep(60)
