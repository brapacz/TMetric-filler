#!/usr/bin/env python3

import requests
import json
from datetime import datetime,timedelta
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY

from config import bearer_auth_key, my_project_id

common_headers = { "Authorization": f"Bearer {bearer_auth_key}"}
api_url = "https://app.tmetric.com/api/v3"
daily_minimum = timedelta(hours=8)

def pretty_print(payload):
    print(json.dumps(payload, indent=4, sort_keys=True))

def get_timeentries(start_date):
    return requests.get(f"{api_url}/accounts/{user_info['activeAccountId']}/timeentries?startDate={start_date}&endDate={datetime.today().date()}", headers=common_headers).json()

def get_my_project_id():
    projects = requests.get(f"{api_url}/accounts/{user_info['activeAccountId']}/timeentries/projects", headers=common_headers).json()
    for project in projects:
        if project['name'] == my_project_id:
            return project['id']
    raise Exception(f"""could not find project id for name "{my_project_id}" """)

response = requests.get(f"{api_url}/user", headers=common_headers)
user_info = response.json()
print(f"Authorized as {user_info['name']}, accountId is {user_info['activeAccountId']}")
# pretty_print(user_info)


last_time_entry = None
start_date = datetime.today().replace(day=1)
while last_time_entry is None:
    start_date -= timedelta(days=31)
    print(f"checking since {start_date}")
    time_entries = get_timeentries(start_date)
    last_time_entry = max([parse(entry['startTime']).date() for entry in time_entries], default=None)

start_date = last_time_entry + timedelta(days=1) # start after last entry
print(f"last time entry was {last_time_entry}, checking since {start_date}")


project_id = get_my_project_id()
print(f"project id is {project_id}")


while True:
    added_anything = False
    time_entries = get_timeentries(start_date)
    for dt in rrule(DAILY, dtstart=start_date, until=datetime.today()):
        # print(f"checking for {dt}")
        today_entries = [entry for entry in time_entries if parse(entry['startTime']).date() == dt.date()]
        # pretty_print(today_entries)
        total = sum( [ parse(entry['endTime'])-parse(entry['startTime']) for entry in today_entries], timedelta())
        print(f"got {len(today_entries)} entry for {dt.date()}, {total} in total")

        if dt.weekday() >= 5:
            print("skipping weekend")
            continue

        if total >= daily_minimum:
            # it's ok :)
            continue

        missing_hours = total - daily_minimum
        print(f"got {-missing_hours} missing in {dt}")

        start_time =  max([parse(entry['endTime']) for entry in today_entries], default=dt.replace(hour=8))
        end_time = start_time + daily_minimum - total

        response = requests.post(
            f"{api_url}/accounts/{user_info['activeAccountId']}/timeentries/",
            headers=common_headers,
            json={
                "startTime": start_time.strftime("%Y/%m/%d, %H:%M:%S"),
                "endTime": end_time.strftime("%Y/%m/%d, %H:%M:%S"),
                "project": {
                    "id": project_id
                }
            }
        )

        if(response.ok):
            for entry in response.json():
                project_name=entry['project']['name']
                total = parse(entry['endTime'])-parse(entry['startTime'])
                print(f"added {total} for {project_name} on {dt.date()}")
            added_anything = True
    if not added_anything:
        print("Nothing to add, exiting")
        break

    print("Running recheck, just in case :)")
