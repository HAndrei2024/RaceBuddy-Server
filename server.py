from flask import Flask, request, jsonify
import joblib
import pandas as pd
import json
from supabase import create_client, Client
from keys import SUPABASE_URL, SUPABASE_API_KEY


app = Flask(__name__)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


@app.route('/prediction', methods=['POST'])
def get_prediction():
    try:
        event_mapping = json.loads(request.form["event"])

        print(f'event loaded: {event_mapping=}')

        #event_mapping = request.json
        start_date = pd.to_datetime(event_mapping["start_date"])
        end_date = pd.to_datetime(event_mapping["end_date"])

        # Build the final model-ready DataFrame
        event_to_predict = pd.DataFrame([{
            "country": event_mapping["country"],
            "category": event_mapping["category"],
            "duration_days": (end_date - start_date).days,
            "start_month": start_date.month,
            "start_weekday": start_date.weekday()  # Monday = 0, Sunday = 6
        }])

        loaded_model = joblib.load('event_participants_model_v2.pkl')

        predicted_participants = loaded_model.predict(event_to_predict)
        #predicted = int(predicted_participants)

        #predicted_rounded =  np.round(predicted_participants)

        # 4. Return response
        return jsonify({
            'predicted_participants': int(predicted_participants[0])
        })

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400


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
    final_response_code = 200

    if not (file.filename.endswith('.xlsx') or not file.filename.endswith('.xls')):
        return jsonify({"error": "Invalid file format. Only .xlsx or .xls files are allowed."}), 400
    
    try:
        xls = pd.ExcelFile(file)

        for sheet_name in xls.sheet_names:
            excel_data = pd.read_excel(file, sheet_name=sheet_name)
           
            if does_excel_sheet_contain_required_columns(excel_data, excel_required_columns):
                for _, row in excel_data.iterrows():

                    update_query_dict = {}
                    athlete_id = -1
                    athlete_not_found_flag = False

                    # build a dict with the following structure:
                    # key (database columns): value (value from excel - from the required column)
                    for key in database_excel_columns_map.keys():
                    
                        if key != "name":
                            update_query_dict[key] = str(row[database_excel_columns_map[key]])
                            
                        else:
                            athlete_name = row[database_excel_columns_map[key]]
                            athlete_id = get_athlete_id(athlete_name, supabase)
                            #TODO: Comment!
                            print(f"Check name: {athlete_name} -> {athlete_id=}")
                            # athlete_id = '9d02c61b-e358-4f5d-87a6-7a150b2d5ae4'
                            
                            result_dict_response = verify_athlete_result(athlete_id, event_id)
 
                            if bool(result_dict_response) == False:
                                final_response_dict["not_found"].append(athlete_name)
                                athlete_not_found_flag = True
                                final_response_code = 400
                    
                    if athlete_not_found_flag == True:
                        if "message" not in final_response_dict.keys():
                            final_response_dict["message"] = "There are results in the excel not registered in the database! The other athlete's results have been updated"
                    else:
                        update_database(update_query_dict, athlete_id, event_id, supabase)

        if final_response_code == 400:
            return jsonify(final_response_dict), final_response_code
        
        final_response_dict["message"] = "Data successfully uploaded to Supabase."
        return  jsonify(final_response_dict), final_response_code
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def verify_athlete_result(athlete_id, event_id):
    response = supabase.table("Result").select("*") \
                    .eq('athlete_uuid', athlete_id) \
                    .eq('event_uuid', event_id) \
                    .execute()

    return response.data


# assuming name like: first_name + last_name
def get_athlete_id(name, supabase):
    response = supabase.table("Athlete").select('athlete_uuid') \
                .eq('first_name', name.split(" ")[0]) \
                .eq('last_name', name.split(" ")[1]) \
                .execute()

    return response.data[0]["athlete_uuid"]


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
                .eq('athlete_uuid', athlete_id) \
                .eq('event_uuid', event_id) \
                .execute()
    print(f"Database updated! {response=}")
    return response


if __name__ == "__main__":
    print("Server is up!")
    app.run(debug=True)
    