import requests
from shapely.geometry import shape


def check_clinician(clinicianID):
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
    clinician_geometry = shape(data['features'][0]['geometry'])
    zone_geometry = shape(data['features'][1]['geometry'])

    # clinician is safe if their loc is within the bounding zone
    is_safe = zone_geometry.contains(clinician_geometry)

    if not is_safe:
        print(f"Clinician {clinicianID} is outside the safe zone.")
    else:
        print(f"Clinician {clinicianID} is inside the safe zone.")


if __name__ == "__main__":
    for i in range(1, 8):    
        check_clinician(i)