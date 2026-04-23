import requests
from shapely.geometry import shape
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# we'll add to set upon alerting, and remove when they've re-enter safe zone
alerted = set()

def check_clinician(clinicianID):
    # gets my hidden email + pw 
    load_dotenv()

    url = f"https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus/{clinicianID}"

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
    is_safe = safe_zone.contains(clinician_loc)

    if not is_safe:
        print(f"Clinician {clinicianID} is outside the safe zone.")
        # alert if we haven't already
        if clinicianID not in alerted:
            alert(clinicianID)
    else:
        print(f"Clinician {clinicianID} is inside the safe zone.")
        # if  previously outside safe zone, remove from alerted set
        if clinicianID in alerted:
            alerted.remove(clinicianID)


def alert(clinicianID):
    # send email
    sender = os.getenv("SENDER_EMAIL") 
    passkey = os.getenv("SENDER_PASSKEY")
    receiver = "wwnp7b+7701g3p4vb15pnqurgo1xc33bd0@guerrillamail.info"

    alert_msg = EmailMessage()
    alert_msg.set_content(f"Clinician {clinicianID} is outside of safe zone.")
    alert_msg['Subject'] = f"ALERT: Clinician in danger!"
    alert_msg['From'] = sender
    alert_msg['To'] = receiver

    # port 465 is for SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, passkey)
        server.send_message(alert_msg)

    print(f"Sent email alert for clinician {clinicianID}.")

    # add to alerted set
    alerted.add(clinicianID)


if __name__ == "__main__":
    for i in range(1, 8):    
        check_clinician(i)