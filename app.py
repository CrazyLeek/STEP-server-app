import os
from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from users import *
from journeys import *
from auth import *
import sqlite3
from datetime import datetime, timedelta
import traceback

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'STEP_journey_checker')))

from STEP_journey_checker.journey_checker import analyse_journey



# The maximum number of journey files the server will store
MAX_JOURNEY_FILES = 1000

# The folder where journeys are stored
JOURNEYS_FOLDER = "journeys/"

# The password to fetch the journey stored on the server
ADMIN_PASSWORD = "Zélie est une vilaine fille"

app = Flask(__name__)

# Allow CORS
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.post("/api/journey_data/new")
def receive_journey_data_new():
    """
    API route used to store new journey data.
    Method:
        - POST
    Expected JSON request:
        Journey data in JSON format.
    Possible returns:
        - 201 (Created): Data successfully stored.
        - 507 (Insufficient Storage): Too many files on the server.
    """
    return store_journey_file(request.get_json())

@app.post("/api/journey_data")
def receive_journey_data():
    """
    API route used to store journey data.
    Method:
        - POST
    Expected JSON request:
        Journey data in JSON format.
    Possible returns:
        - 201 (Created): Data successfully stored.
        - 507 (Insufficient Storage): Too many files on the server.
    """
    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:
        store_file(request.get_json())
        return "Data successfully stored on the server", 201
    else:
        return "Too many files on the server", 507

@app.get("/api/journey_data")
def send_journey_data():
    """
    API route used to get all journey data.
    Method:
        - GET
    Expected JSON request:
        {
            "password": "Admin password"
        }
    Possible returns:
        - 200 (OK): Data retrieved successfully.
        - 401 (Unauthorized): Invalid password.
    """
    data = request.get_json()
    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    return jsonify(get_journey_files())

@app.delete("/api/journey_data")
def delete_journey_data():
    """
    API route used to delete all journey data.
    Method:
        - DELETE
    Expected JSON request:
        {
            "password": "Admin password"
        }
    Possible returns:
        - 200 (OK): Files deleted successfully.
        - 401 (Unauthorized): Invalid password.
    """
    data = request.get_json()
    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    return delete_all_journey_files()

@app.post("/api/login")
def receive_login():
    """
    API route used to connect a user.
    Method:
        - POST
    Expected JSON request:
        {
            "username": "User name",
            "password": "Password"
        }
    Possible returns:
        - 200 (OK): Login successful, returns user ID.
        - 401 (Unauthorized): Invalid credentials.
        - 500 (Internal Server Error): Connection attempt error for unknown reason.
    """
    return login_user(request.json)

@app.get('/api/user/<user_id>')
def send_user(user_id):
    """
    API route used to get a user.
    Method:
        - GET
    Possible returns:
        - 200 (OK): User details retrieved successfully.
        - 404 (Not Found): User not found.
        - 500 (Internal Server Error): Error fetching user for unknown reason.
    """
    return get_user_details(user_id)

@app.post("/api/user")
def receive_user():
    """
    API route used to register a new user.
    Method:
        - POST
    Expected form-data request:
        {
            "username": "User name",
            "firstName": "First name",
            "lastName": "Last name",
            "password": "Password",
            "profileImage": "Profile image file (optional)"
        }
    Possible returns:
        - 201 (Created): The user has been created successfully.
        - 400 (Bad Request): The user name already exists in the database.
        - 500 (Internal Server Error): User creation failed for an unknown reason.
    """
    return register_user(request.form, request.files)

@app.get("/api/user_profile_image/<user_id>")
def get_user_profile_image(user_id):
    """
    API route to get the profile image of a user.
    Method:
        - GET
    URL parameters:
        - user_id: ID of the user whose profile image is to be fetched.
    Possible returns:
        - 200 (OK): Profile image retrieved successfully.
        - 404 (Not Found): Profile image not found.
    """
    user_pictures_folder = 'user_pictures'
    filename = os.path.join(user_pictures_folder, f"{user_id}.png")
    
    if os.path.exists(filename):
        return send_file(filename, mimetype='image/png')
    else:
        return {"error": "Profile image not found"}, 404

@app.delete('/api/user/<user_id>')
def delete_user(user_id):
    """
    API route for deleting a specific user and all associated data.
    Method:
        - DELETE
    URL parameters:
        - user_id: ID of the user to be deleted
    Possible returns:
        - 200 (OK): User deleted successfully.
        - 500 (Internal Server Error): Error when deleting the user or their data for an unknown reason.
    """
    return remove_user(user_id)

@app.get("/api/journey/user/<user_id>")
def send_journeys(user_id):
    """
    API route used to get all journeys for a specific user.
    Method:
        - GET
    URL parameters:
        - user_id: ID of the user whose journeys are to be fetched.
    Possible returns:
        - 200 (OK): Journeys retrieved successfully.
        - 404 (Not Found): No journeys found for the given user ID.
        - 500 (Internal Server Error): Error retrieving journeys.
    """
    return get_user_journeys(user_id)

@app.post("/api/journey")
def receive_journey():
    """
    API route used to receive and store a new journey.
    Method:
        - POST
    Expected JSON request:
        {
            "userId": 1,
            "name": "Journey name",
            "methodsJson": NEED TO CONFIRM THE STRUCTURE
        }
    Possible returns:
        - 201 (Created): Journey created successfully.
        - 400 (Bad Request): Invalid input data.
        - 500 (Internal Server Error): Error creating journey.
    """
    return store_journey(request.json)

@app.get("/api/specification/method/<method_id>")
def send_specifications_method(method_id):
    """
    API route used to get specifications for a specific method.
    Method:
        - GET
    URL parameters:
        - method_id: ID of the method whose specifications are to be fetched.
    Possible returns:
        - 200 (OK): Specifications retrieved successfully.
        - 404 (Not Found): No specifications found for the given method ID.
        - 500 (Internal Server Error): Error retrieving specifications.
    """
    return get_method_specifications(method_id)

@app.get("/api/method/<method_id>")
def send_method(method_id):
    """
    API route used to get details of a specific method.
    Method:
        - GET
    URL parameters:
        - method_id: ID of the method to be fetched.
    Possible returns:
        - 200 (OK): Method details retrieved successfully.
        - 404 (Not Found): No method found with the given ID.
        - 500 (Internal Server Error): Error retrieving method details.
    """
    return get_method_details(method_id)

@app.get("/api/journey/<journey_id>")
def send_journey(journey_id):
    """
    API route used to get details of a specific journey.
    Method:
        - GET
    URL parameters:
        - journey_id: ID of the journey to be fetched.
    Possible returns:
        - 200 (OK): Journey details retrieved successfully.
        - 404 (Not Found): No journey found with the given ID.
        - 500 (Internal Server Error): Error retrieving journey details.
    """
    return get_journey_details(journey_id)

@app.post("/api/record")
def receive_record():
    """
    API route used to receive and store a new journey record.
    Method:
        - POST
    Expected JSON request:
        {
            "journeyId": 1,
            "isValidated": false,
            "isPending": true,
            "jsonFileName": "example.json",
            "points": 0,
            "co2Saved": 0,
            "startDate": "2024-07-04T12:00:00Z",
            "endDate": "2024-07-04T13:00:00Z"
        }
    Possible returns:
        - 201 (Created): Record created successfully.
        - 500 (Internal Server Error): Error creating record.
    """
    return store_record(request.json)

@app.get("/api/methods_with_specifications")
def send_methods_with_specifications():
    """
    API route used to get all methods with their specifications.
    Method:
        - GET
    Possible returns:
        - 200 (OK): Methods and specifications retrieved successfully.
        - 500 (Internal Server Error): Error retrieving methods and specifications.
    """
    return get_all_methods_with_specifications()

@app.delete('/api/journey/<journey_id>')
def delete_journey(journey_id):
    """
    API route used to delete a specific journey.
    Method:
        - DELETE
    URL parameters:
        - journey_id: ID of the journey to be deleted.
    Possible returns:
        - 200 (OK): Journey deleted successfully.
        - 404 (Not Found): No journey found with the given ID.
        - 500 (Internal Server Error): Error deleting the journey.
    """
    return remove_journey(journey_id)

@app.post("/api/upload_journey_file")
def upload_journey_file():
    """
    API route used to upload a journey file.
    Method:
        - POST
    Expected multipart form-data request:
        - file: The JSON file containing journey data.
    Possible returns:
        - 201 (Created): File successfully uploaded and stored.
        - 400 (Bad Request): No file part or no selected file.
        - 507 (Insufficient Storage): Too many files on the server.
    """
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:
        filename = os.path.join(JOURNEYS_FOLDER, secure_filename(file.filename))
        file.save(filename)
        return "File successfully uploaded", 201
    else:
        return "Too many files on the server", 507
    
@app.post("/api/analyse_journey_file")
def analyse_journey_file():
    """
    API route used to analyze a journey file.
    Method:
        - POST
    Expected multipart form-data request:
        - file: The JSON file containing journey data.
        - recordId: The ID of the journey record.
        - username: The username of the user.
    Possible returns:
        - 200 (OK): File successfully analyzed.
        - 400 (Bad Request): No file part or no selected file.
        - 500 (Internal Server Error): Error during file analysis.
    """
    if 'file' not in request.files or 'recordId' not in request.form:
        return "No file part or recordId or username", 400

    file = request.files['file']
    record_id = request.form['recordId']

    if file.filename == '':
        return "No selected file", 400


    #Sauvegarde du fichier temporairement
    filename = os.path.join(JOURNEYS_FOLDER, secure_filename(f"{file.filename}"))
    file.save(filename)

    result = False

    #Analyse du fichier par l'algorithme
    try:
        result, distance_by_modes = analyse_journey(filename)
        """
        The section below will be useful the day you want to calculate CO2e differently depending on the specification (particularly for petrol, diesel, hybrid cars, etc.).
        It may be necessary to change the structure returned by distance_by_modes to take account of each specification.
        if you change distance_by_modes, make sure you adapt each location where it was used.
        """
        #
        # file = open(filename, 'r')
        # try:
        #     data = json.load(file)
        # finally:
        #     journey_data = data.get("journey", [])
        #     file.close()

    except Exception as e:
        app.logger.error(f"Error during file analysis: {str(e)}")
        print(traceback.format_exc())
        #Si ça échoue en cours de route on set le record associé à refusé
        try:
            con = database.connect_to_db()
            cur = con.cursor()
            cur.execute("UPDATE Records SET isValidated=?, isPending=?, nbMethodUsed=?, kmTravelled=?  WHERE recordId=?", (False, False, len(distance_by_modes), sum(distance_by_modes.values())/1000, record_id))
            con.commit()
            con.close()
        except Exception as e:
            return f"Error updating record after analysis failure: {str(e)}", 500
        return "Error during file analysis, record updated with analysis failure", 500
    finally:
        #On retire systématiquement le fichier temporairement stocké du serveur
        os.remove(filename)
    try:
        #Sinon si il n'y a pas eu d'erreur on va update le record avec le résultat
        con = database.connect_to_db()
        cur = con.cursor()
        cur.execute("UPDATE Records SET isValidated=?, isPending=?, nbMethodUsed=?, kmTravelled=? WHERE recordId=?", (result, False,len(distance_by_modes), sum(distance_by_modes.values())/1000, record_id))
        con.commit()
        con.close()

        if result == True:
            """
            This section allows you to retrieve a dictionary of CO2e emissions for each transport method and its specifications. It is structured as follows:
                {
                    ‘walk’: {‘default’: 0.231},
                    ‘car‘: {’petrol": 0.634, “diesel”: 0.56, “Unknown”: 0.583},
                    . . . etc
                } 
            """
            con = database.connect_to_db()
            cursor = con.cursor()

            # Step 1: Get all carbon emission factors with method names
            cursor.execute('''
                SELECT cef.carbonEmissionFactorId, cef.methodId, cef.co2eFactor, m.name AS methodName
                FROM CarbonEmissionFactors cef
                JOIN Methods m ON cef.methodId = m.methodId;
            ''')
            factors = cursor.fetchall()

            # Step 2: Count the number of factors per method
            cursor.execute('''
                SELECT methodId, COUNT(*) AS count
                FROM CarbonEmissionFactors
                GROUP BY methodId;
            ''')
            counts = cursor.fetchall()
            method_count = {methodId: count for methodId, count in counts}

            # Step 3: Get specifications for methods with multiple factors
            cursor.execute('''
                SELECT cef.carbonEmissionFactorId, cef.methodId, cef.co2eFactor, ms.name AS specificationName
                FROM CarbonEmissionFactors cef
                JOIN CarbonEmissionFactorSpecifications ceff ON cef.carbonEmissionFactorId = ceff.carbonEmissionFactorId
                JOIN MethodsSpecifications ms ON ceff.specificationId = ms.specificationId
                WHERE ceff.methodId = cef.methodId;
            ''')
            specifications = cursor.fetchall()

            con.close()

            emission_dict = {}

            # Process each factor
            for factorId, methodId, co2eFactor, methodName in factors:
                methodNameLower = methodName.lower()
                if method_count[methodId] == 1:
                    emission_dict[methodNameLower] = {"default": co2eFactor}
                else:
                    if methodNameLower not in emission_dict:
                        emission_dict[methodNameLower] = {}

            # Add specifications to methods with multiple factors
            for factorId, methodId, co2eFactor, specName in specifications:
                method_name = next((name for fid, mid, cf, name in factors if fid == factorId), None)
                if method_name:
                    methodNameLower = method_name.lower()
                    emission_dict[methodNameLower][specName.lower()] = co2eFactor

            c02eSaved = calculate_co2e_emission(distance_by_modes, emission_dict, record_id)

            con = database.connect_to_db()
            cur = con.cursor()
            cur.execute("UPDATE Records SET co2Saved=? WHERE recordId=?", (c02eSaved, record_id))
            con.commit()
            con.close()
                    
    except Exception as e:
        return f"Error updating record: {str(e)}", 500

    return "File successfully analyzed and record updated", 200


def calculate_co2e_emission(distance_by_modes, emission_dict, recordId):
    isWalkUsed = False
    isDartUsed = False
    isLuasUsed = False 
    isBikeUsed = False 
    isCarUsed = False 
    isBusUsed = False 
    kmWalk = 0 
    kmDart = 0  
    kmLuas = 0  
    kmBike = 0 
    kmCar = 0 
    kmBus = 0 
    co2eWalk = 0 
    co2eDart = 0 
    co2eLuas = 0 
    co2eBike = 0 
    co2eCar = 0 
    co2eBus = 0 

    for key in distance_by_modes:
        if key == 'walk':
            isWalkUsed = True
            kmWalk += distance_by_modes[key]/1000
            co2eWalk += distance_by_modes[key]/1000 * emission_dict[key]['default']
        elif key == 'bus':
            isBusUsed = True
            kmBus += distance_by_modes[key]/1000
            co2eBus += distance_by_modes[key]/1000 * emission_dict[key]['default']
        elif key == 'luas':
            isLuasUsed = True
            kmLuas += distance_by_modes[key]/1000
            co2eLuas += distance_by_modes[key]/1000 * emission_dict[key]['default']
        elif key == 'dart':
            isDartUsed = True
            kmDart += distance_by_modes[key]/1000
            co2eDart += distance_by_modes[key]/1000 * emission_dict[key]['default']
        elif key == 'bike':
            isBikeUsed = True
            kmBike += distance_by_modes[key]/1000
            co2eBike += distance_by_modes[key]/1000 * emission_dict[key]['default']
        elif key == 'car':
            isCarUsed = True
            kmCar += distance_by_modes[key]/1000
            co2eCar += distance_by_modes[key]/1000 * emission_dict[key]['unknown']
        
    con = database.connect_to_db()
    cur = con.cursor()
    cur.execute('''
    INSERT INTO CarbonEmissionStats (
                recordId, date, isWalkUsed, isDartUsed, isLuasUsed, isBikeUsed, isCarUsed, isBusUsed, kmWalk, kmDart,
                kmLuas, kmBike, kmCar, kmBus, co2eWalk, co2eDart, co2eLuas, co2eBike, co2eCar, co2eBus) VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''',(recordId, datetime.datetime.now(), isWalkUsed, isDartUsed, isLuasUsed, isBikeUsed, isCarUsed, isBusUsed,
        kmWalk, kmDart, kmLuas, kmBike, kmCar, kmBus, co2eWalk, co2eDart, co2eLuas, co2eBike, co2eCar, co2eBus))
    con.commit()
    con.close()

    total_distance = sum(distance_by_modes.values())/1000
    app.logger.error("total_distance")
    app.logger.error(total_distance)
    total_co2e = co2eWalk + co2eDart + co2eLuas + co2eBike + co2eCar + co2eBus
    app.logger.error("total_co2e")
    app.logger.error(total_co2e)
    co2e_by_car = total_distance * emission_dict['car']['unknown']
    app.logger.error("co2e_by_car")
    app.logger.error(co2e_by_car)
    co2eSaved = co2e_by_car - total_co2e
    app.logger.error("co2eSaved")
    app.logger.error(co2eSaved)

    return co2eSaved

def get_start_end_of_week(date):
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start, end

@app.route('/api/weekly-roundup/<int:user_id>', methods=['GET'])
def get_weekly_roundup(user_id):
    con = database.connect_to_db()
    cur = con.cursor()
    
    today = datetime.today()
    start_of_week, end_of_week = get_start_end_of_week(today)
    start_of_week_str = start_of_week.strftime('%Y-%m-%d')
    end_of_week_str = end_of_week.strftime('%Y-%m-%d')
    
    query = '''
        SELECT r.*
        FROM Records r
        LEFT JOIN Journeys j ON r.journeyId = j.journeyId
        WHERE j.userId = ?
          AND r.startDate BETWEEN ? AND ?
    '''
    
    records = cur.execute(query, (user_id, start_of_week_str, end_of_week_str)).fetchall()
    
    routes_completed = len(records)
    co2_reduced = sum(record['co2Saved'] for record in records)
    
    cur.close()
    con.close()
    
    data = {
        'routesCompleted': routes_completed,
        'co2Reduced': co2_reduced,
        'pointsEarned': 0,  # À compléter si nécessaire
        'moneySaved': 0,    # À compléter si nécessaire
        'leaderboardPosition': 0,  # À compléter si nécessaire
        'placesGained': 0,   # À compléter si nécessaire
    }
    
    return jsonify(data)

@app.route('/api/user-records/<int:user_id>', methods=['GET'])
def get_user_records(user_id):
    con = database.connect_to_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    query = '''
        SELECT r.*, j.name as journey_name
        FROM Records r
        LEFT JOIN Journeys j ON r.journeyId = j.journeyId
        WHERE j.userId = ?
        ORDER BY r.startDate DESC
    '''
    
    #try:
    records = cur.execute(query, (user_id,)).fetchall()
    records_list = []
    
    for record in records:
        record_dict = dict(record)
        record_dict['journey'] = {'name': record_dict['journey_name']} if record_dict.get('journey_name') else None
        del record_dict['journey_name']
        records_list.append(record_dict)
    
    cur.close()
    con.close()

    return jsonify(records_list)

    #except sqlite3.Error as e:
    #    return jsonify({'error': str(e)}), 500
    
    #finally:

@app.route('/api/carbon_emission_stats', methods=['GET'])
def get_carbon_emission_stats():
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        cur.execute('''
            SELECT 
                strftime('%m', c.date) as month,
                SUM(c.co2eWalk) as co2eWalk,
                SUM(c.co2eDart) as co2eDart,
                SUM(c.co2eLuas) as co2eLuas,
                SUM(c.co2eBike) as co2eBike,
                SUM(c.co2eCar) as co2eCar,
                SUM(c.co2eBus) as co2eBus,
                COUNT(DISTINCT c.recordId) as recordCount
            FROM 
                CarbonEmissionStats c
            JOIN 
                Records r ON c.recordId = r.recordId
            WHERE 
                r.isValidated = 1 AND r.isPending = 0
            GROUP BY 
                month
        ''')
        rows = cur.fetchall()
        con.close()

        stats = {
            "Walk": [0]*12,
            "Dart": [0]*12,
            "Luas": [0]*12,
            "Bike": [0]*12,
            "Car": [0]*12,
            "Bus": [0]*12,
            "TotalRecords": 0,
        }

        total_records = 0
        for row in rows:
            month_index = int(row[0]) - 1
            stats["Walk"][month_index] = row[1]
            stats["Dart"][month_index] = row[2]
            stats["Luas"][month_index] = row[3]
            stats["Bike"][month_index] = row[4]
            stats["Car"][month_index] = row[5]
            stats["Bus"][month_index] = row[6]
            total_records += row[7]

        stats["TotalRecords"] = total_records

        return jsonify(stats), 200
    except Exception as e:
        return str(e), 500
    
@app.route('/api/kilometers_stats', methods=['GET'])
def get_kilometers_stats():
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        cur.execute('''
            SELECT 
                strftime('%m', c.date) as month,
                SUM(c.kmWalk) as kmWalk,
                SUM(c.kmDart) as kmDart,
                SUM(c.kmLuas) as kmLuas,
                SUM(c.kmBike) as kmBike,
                SUM(c.kmCar) as kmCar,
                SUM(c.kmBus) as kmBus,
                COUNT(DISTINCT c.recordId) as recordCount
            FROM 
                CarbonEmissionStats c
            JOIN 
                Records r ON c.recordId = r.recordId
            WHERE 
                r.isValidated = 1 AND r.isPending = 0
            GROUP BY 
                month
        ''')
        rows = cur.fetchall()
        con.close()

        stats = {
            "Walk": [0]*12,
            "Dart": [0]*12,
            "Luas": [0]*12,
            "Bike": [0]*12,
            "Car": [0]*12,
            "Bus": [0]*12,
            "TotalRecords": 0,
        }

        total_records = 0
        for row in rows:
            month_index = int(row[0]) - 1
            stats["Walk"][month_index] = row[1]
            stats["Dart"][month_index] = row[2]
            stats["Luas"][month_index] = row[3]
            stats["Bike"][month_index] = row[4]
            stats["Car"][month_index] = row[5]
            stats["Bus"][month_index] = row[6]
            total_records += row[7]

        stats["TotalRecords"] = total_records

        return jsonify(stats), 200
    except Exception as e:
        return str(e), 500
    
@app.route('/api/usage_stats', methods=['GET'])
def get_usage_stats():
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        cur.execute('''
            SELECT 
                strftime('%m', c.date) as month,
                SUM(CASE WHEN c.isWalkUsed THEN 1 ELSE 0 END) as walkUsage,
                SUM(CASE WHEN c.isDartUsed THEN 1 ELSE 0 END) as dartUsage,
                SUM(CASE WHEN c.isLuasUsed THEN 1 ELSE 0 END) as luasUsage,
                SUM(CASE WHEN c.isBikeUsed THEN 1 ELSE 0 END) as bikeUsage,
                SUM(CASE WHEN c.isCarUsed THEN 1 ELSE 0 END) as carUsage,
                SUM(CASE WHEN c.isBusUsed THEN 1 ELSE 0 END) as busUsage,
                COUNT(DISTINCT c.recordId) as recordCount
            FROM 
                CarbonEmissionStats c
            JOIN 
                Records r ON c.recordId = r.recordId
            WHERE 
                r.isValidated = 1 AND r.isPending = 0
            GROUP BY 
                month
        ''')
        rows = cur.fetchall()
        con.close()

        stats = {
            "Walk": [0]*12,
            "Dart": [0]*12,
            "Luas": [0]*12,
            "Bike": [0]*12,
            "Car": [0]*12,
            "Bus": [0]*12,
            "TotalRecords": 0,
        }

        total_records = 0
        for row in rows:
            month_index = int(row[0]) - 1
            stats["Walk"][month_index] = row[1]
            stats["Dart"][month_index] = row[2]
            stats["Luas"][month_index] = row[3]
            stats["Bike"][month_index] = row[4]
            stats["Car"][month_index] = row[5]
            stats["Bus"][month_index] = row[6]
            total_records += row[7]

        stats["TotalRecords"] = total_records

        return jsonify(stats), 200
    except Exception as e:
        return str(e), 500
    
@app.route("/apps/gps_recorder")
def gps_recorder_page():
    return render_template("gps_record_app.html")

@app.route("/apps/step")
def step_app_page():
    return render_template("step_app.html")

if __name__ == '__main__':
    app.run(debug=True)