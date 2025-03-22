import requests
import json

url = 'http://127.0.0.1:5000/upload'
excel_file_path = "data\\test_data.xlsx"

files = {}
data = {}

with open(excel_file_path, 'rb') as f:
    #files = {'file': (excel_file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    files["file"] = f

    columns = {} # key: database column, value: excel column
    columns["rank"] = "Rank"
    columns["time"] = "Time"
    columns["points"] = "Points"
    columns["name"] = "Athlete Name"

    data["columns"] = json.dumps(columns)
    data["event_id"] = 1

    # Send the POST request with the file attached
    response = requests.post(url, files=files, data=data)


if response.status_code == 200:
    print("File uploaded successfully:", response.json())
else:
    print("Failed to upload file. Status code:", response.status_code)
    print("Error:", response.json())