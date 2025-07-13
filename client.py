import requests
import json

url = 'http://127.0.0.1:5000/prediction'
excel_file_path = "data\\sample_results.xlsx"

files = {}
data = {}

with open(excel_file_path, 'rb') as f:
    #files = {'file': (excel_file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    files["file"] = f

    # columns = {} # key: database column, value: excel column
    # columns["rank"] = "Rank"
    # columns["time"] = "Time"
    # columns["points"] = "Points"
    # columns["name"] = "Athlete Name"

    columns = {}  # key: database column, value: excel column
    #columns["event_uuid"] = "event_id"
    columns["name"] = "name"
    columns["time"] = "time"
    columns["penalties"] = "penalties"
    columns["rank"] = "rank"
    columns["points"] = "points"
    columns["athlete_event_number"] = "athlete_event_number"
    columns["s1"] = "s1"
    columns["s2"] = "s2"
    columns["s3"] = "s3"
    columns["s4"] = "s4"
    columns["status"] = "status"
    columns["confirmed"] = "confirmed"
    columns["category"] = "category"


    data["columns"] = json.dumps(columns)
    data["event_id"] = "13c94ae9-ae3a-4b50-81e4-96d3cf7bc319"

    # Send the POST request with the file attached
    #response = requests.post(url, files=files, data=data)

    input_json = {
    "start_date": "2025-09-12",
    "end_date": "2025-09-15",
    "country": "France",
    "category": "Music"
    }

    response = requests.post(url = url, json=input_json)

    if response.status_code == 200:
        data = response.json()
        predicted_number = data.get("predicted_participants")

        print("✅ Predicted participants:", predicted_number)
    else:
        print("❌ Request failed:", response.status_code)
        print("Response:", response.text)


# if response.status_code == 200:
#     print("File uploaded successfully:", response.json())
# else:
#     print("Failed to upload file. Status code:", response.status_code)
#     print("Error:", response.json())