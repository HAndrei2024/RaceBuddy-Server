from flask import Flask, request, jsonify
import pandas as pd
import json
from supabase import create_client, Client
from keys import SUPABASE_URL, SUPABASE_API_KEY


app = Flask(__name__)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


@app.route('/upload', methods=['POST'])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    # if "columns" not in request.data:
    #     return jsonify({"error": "No columns part"}), 400
    # if "event_id" not in request.data:
    #     return jsonify({"error": "No event_id part"}), 400

    file = request.files["file"]
    database_excel_columns_map = json.loads(request.form["columns"])
    event_id = request.form["event_id"]
    excel_required_columns = database_excel_columns_map.values()
    print("It's working! #1")
    if not (file.filename.endswith('.xlsx') or not file.filename.endswith('.xls')):
        return jsonify({"error": "Invalid file format. Only .xlsx or .xls files are allowed."}), 400
    
    try:
        xls = pd.ExcelFile(file)

        for sheet_name in xls.sheet_names:
            excel_data = pd.read_excel(file, sheet_name=sheet_name)
            print("It's working! #2")
            if does_excel_sheet_contain_required_columns(excel_data, excel_required_columns):
                for index, row in excel_data.iterrows():
                    update_query_dict = {}
                    athlete_id = -1
                    for key in database_excel_columns_map.keys():
                    # build a dict with the following structure:
                    # key (database columns): value (value from excel - from the required column)
                        if key != "name":
                            update_query_dict[key] = row[database_excel_columns_map[key]]
                            print("It's working! #3")
                        else:
                            
                            athlete_name = row[database_excel_columns_map[key]]
                            print(f"{athlete_name=}")
                            athlete_id = get_athlete_id(athlete_name, supabase)
                            print(f"{athlete_id=}")
                            # update_query_dict["athlete_id"] = athlete_id

                            if athlete_id == -1:
                                print(f"Athlete {athlete_name} id couldn't be found!")
                    
                    if athlete_id != -1:
                        response = update_database(update_query_dict, athlete_id, event_id, supabase)

                        if response.status_code == 200:
                            print("Update successful.")
                        else:
                            print(f"Error: {response.status_code} - {response.error_message}")
            
        return jsonify({"message": "Data successfully uploaded to Supabase."}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# assuming name like: first_name + last_name
def get_athlete_id(name, supabase):
    response = supabase.table("Athlete").select("athlete_id") \
                .eq('first_name', 'First') \
                .execute()
    print(response)
    return response.data


def does_excel_sheet_contain_required_columns(excel_data, excel_required_columns):
    excel_columns = excel_data.columns.tolist()
    excel_columns_set = {column for column in excel_columns}
    excel_required_columns_set = {column for column in excel_required_columns}

    if excel_columns_set.issubset(excel_required_columns_set):
        return True

    return False

    
def update_database(query_dict, athlete_id, event_id, supabase):
    response = supabase.table("Result") \
                .update(query_dict) \
                .eq('athlete_id', athlete_id) \
                .eq('event_id', event_id) \
                .execute()
    
    return response


if __name__ == "__main__":
    app.run(debug=True)