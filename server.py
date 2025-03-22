from flask import Flask, request, jsonify
import pandas as pd
from supabase import create_client, Client


app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    if "columns" not in request.files:
        return jsonify({"error": "No columns part"}), 400

    file = request.files["file"]
    database_excel_columns_map = request.files["columns"]
    excel_required_columns = database_excel_columns_map.values()

    if not (file.filename.endswith('.xlsx') or not file.filename.endswith('.xls')):
        return jsonify({"error": "Invalid file format. Only .xlsx or .xls files are allowed."}), 400
    
    try:
        xls = pd.ExcelFile(file)

        for sheet_name in xls.sheet_names:
            excel_data = pd.read_excel(file, sheet_name=sheet_name)

            if does_excel_sheet_contain_required_columns(excel_data, excel_required_columns):
                for row in excel_data.iterrows():
                   update_query_dict = {}
                   for key in database_excel_columns_map.keys():
                    # build a dict with the following structure:
                    # key (database columns): value (value from excel - from the required column)
                    update_query_dict[key] = excel_data[database_excel_columns_map[key]]
                    update_database()
                    # get the athlete_id based on the name
                    # update the database
                    
            

        return jsonify({"message": "Data successfully uploaded to Supabase."}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def does_excel_sheet_contain_required_columns(excel_data, excel_required_columns):
    excel_columns = excel_data.columns()
    excel_columns_set = {column for column in excel_columns}
    excel_required_columns_set = {column for column in excel_required_columns}

    if excel_columns_set.issubset(excel_required_columns_set):
        return True

    return False

    
def update_database():
    pass


if __name__ == "__main__":
    app.run(debug=True)