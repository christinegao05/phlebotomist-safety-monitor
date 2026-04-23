Phlebotomist Safety Monitor:
A Python service that monitors clinician locations via the Sprinter Health API.

Implementation Details:
- Uses Shapely with .intersects() to ensure clinicians on the boundary line of a safe zone are identified as safe.
- Includes a try/except block to handle API failure and alerts.
- Tracks alert history using a set to prevent spam email with alerts triggered only on a status changes.

Quick Start:
- Configure Environment: Create a .env file with SENDER_EMAIL and SENDER_PASSKEY.
- Install dependencies: pip install requests shapely python-dotenv
