import os
import json
import requests
from datetime import datetime

# Strava API endpoints
TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

# Manhattan bounds
MANHATTAN_BOUNDS = {
    "north": 40.882214,
    "south": 40.680611,
    "east": -73.907000,
    "west": -74.047285
}

def refresh_token():
    """Get fresh access token"""
    response = requests.post(TOKEN_URL, data={
        'client_id': os.environ['STRAVA_CLIENT_ID'],
        'client_secret': os.environ['STRAVA_CLIENT_SECRET'],
        'grant_type': 'refresh_token',
        'refresh_token': os.environ['STRAVA_REFRESH_TOKEN']
    })
    return response.json()['access_token']

def get_activities(access_token):
    """Fetch all running activities"""
    activities = []
    page = 1
    
    while True:
        response = requests.get(ACTIVITIES_URL, 
            headers={'Authorization': f'Bearer {access_token}'},
            params={'per_page': 200, 'page': page, 'type': 'Run'})
        
        data = response.json()
        if not data:
            break
            
        activities.extend(data)
        page += 1
    
    return activities

def decode_polyline(encoded):
    """Decode Google polyline to coordinates"""
    # Implementation of polyline decoder
    # (same as JavaScript version)
    pass

def is_in_manhattan(coordinates):
    """Check if run intersects Manhattan"""
    for lon, lat in coordinates:
        if (MANHATTAN_BOUNDS['south'] <= lat <= MANHATTAN_BOUNDS['north'] and
            MANHATTAN_BOUNDS['west'] <= lon <= MANHATTAN_BOUNDS['east']):
            return True
    return False

def main():
    # Get fresh token
    access_token = refresh_token()
    
    # Fetch activities
    activities = get_activities(access_token)
    
    # Process Manhattan runs
    manhattan_runs = []
    
    for activity in activities:
        if activity.get('map', {}).get('summary_polyline'):
            polyline = activity['map']['summary_polyline']
            coordinates = decode_polyline(polyline)
            
            if is_in_manhattan(coordinates):
                manhattan_runs.append({
                    'id': activity['id'],
                    'name': activity['name'],
                    'date': activity['start_date'],
                    'distance': activity['distance'],
                    'polyline': polyline
                })
    
    # Save to JSON file
    with open('runs_data.json', 'w') as f:
        json.dump({
            'runs': manhattan_runs,
            'last_updated': datetime.now().isoformat()
        }, f)

if __name__ == '__main__':
    main()
