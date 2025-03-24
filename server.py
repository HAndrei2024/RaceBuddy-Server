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
    if "columns" not in request.form:
        return jsonify({"error": "No columns part"}), 400
    if "event_id" not in request.form:
        return jsonify({"error": "No event_id part"}), 400

    file = request.files["file"]
    database_excel_columns_map = json.loads(request.form["columns"])
    event_id = request.form["event_id"]
    excel_required_columns = database_excel_columns_map.values()

    final_response_dict = {"not_found" : []}
    final_response_code = -1

    if not (file.filename.endswith('.xlsx') or not file.filename.endswith('.xls')):
        return jsonify({"error": "Invalid file format. Only .xlsx or .xls files are allowed."}), 400
    
    try:
        xls = pd.ExcelFile(file)

        for sheet_name in xls.sheet_names:
            excel_data = pd.read_excel(file, sheet_name=sheet_name)
            print("#1 Excel read succesfully!")
            if does_excel_sheet_contain_required_columns(excel_data, excel_required_columns):
                for index, row in excel_data.iterrows():
                    update_query_dict = {}
                    athlete_id = -1
                    for key in database_excel_columns_map.keys():
                    # build a dict with the following structure:
                    # key (database columns): value (value from excel - from the required column)
                        if key != "name":
                            update_query_dict[key] = str(row[database_excel_columns_map[key]])
                            
                        else:
                            
                            athlete_name = row[database_excel_columns_map[key]]
                            print(f"{athlete_name=}")
                            athlete_id = get_athlete_id(athlete_name, supabase)
                            
                            result_dict_response = verify_athlete_result(athlete_id, event_id)
 
                            if bool(result_dict_response) == False:
                                final_response_dict["not_found"].append(athlete_name)
                                

                            print(f"{athlete_id=}")
                            if athlete_id == -1:
                                print(f"Athlete {athlete_name} id couldn't be found!")
                    
                    if athlete_id != -1:
                        if bool(final_response_dict["not_found"]) == True:
                            final_response_dict["message"] = "There are results in the excel not registered in the database!"
                            final_response_code = 400
                        else:
                            print("#2 Updating the database...")
                            print(f"{update_query_dict=}")
                            update_database(update_query_dict, athlete_id, event_id, supabase)

        
        final_response_dict["message"] = "Data successfully uploaded to Supabase."
        return jsonify(final_response_dict), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def verify_athlete_result(athlete_id, event_id):
    response = supabase.table("Result").select("*") \
                    .eq("athlete_id", athlete_id) \
                    .eq("event_id", event_id) \
                    .execute()

    return response.data


# assuming name like: first_name + last_name
def get_athlete_id(name, supabase):
    response = supabase.table("Athlete").select("athlete_id") \
                .eq('first_name', name) \
                .execute()

    return response.data[0]["athlete_id"]


def does_excel_sheet_contain_required_columns(excel_data, excel_required_columns):
    excel_columns = excel_data.columns.tolist()
    excel_columns_set = {column for column in excel_columns}
    excel_required_columns_set = {column for column in excel_required_columns}

    if excel_columns_set.issubset(excel_required_columns_set):
        return True

    return False

    
def update_database(query_dict, athlete_id, event_id, supabase):
    print(f"{athlete_id=}")
    response = supabase.table("Result") \
                .update(query_dict) \
                .eq('athlete_id', athlete_id) \
                .eq('event_id', event_id) \
                .execute()
    print(f"Database updated! {response=}")
    return response


if __name__ == "__main__":
    app.run(debug=True)