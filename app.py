import os, json, datetime

from users import *
from journeys import *
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

# The maximum number of journey files the server will store
MAX_JOURNEY_FILES = 1000

# The folder were jouneys are stored
JOURNEYS_FOLDER = "journeys/"

# The password to fetch the journey stored on the server
ADMIN_PASSWORD = "Zélie est une vilaine fille"

app = Flask(__name__)

# Allow CORS
CORS(app)

def journey_list_to_str_new(journey):
    res = []
    for trip in journey:
        method = trip[0]
        line = trip[1] if len(trip) > 1 and trip[1] else ''
        res.append(f"{method}-{line}" if line else method)
    return '_'.join(res)

def journey_list_to_str(journey:list):
    """Convert a journey to a string"""

    MODE, LINE = 0, 1
    res = []

    for trip in journey:
        if trip[MODE] in ("walk", "bike", "car", "dart"):
            res.append(trip[MODE])
        else:
            res.append(trip[MODE] + "-" + trip[LINE])

    return '_'.join(res)

def create_filename_from_journey(journey:list):
    """
    Return a filename describing the journey 
    """

    journey_str = journey_list_to_str(journey)
    date_str = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

    return journey_str + "#" + date_str

def create_filename_from_journey_new(journey):
    """
    Return a filename describing the journey 
    """
    journey_str = journey_list_to_str_new(journey)
    date_str = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
    return f"{journey_str}#{date_str}"

def store_file(journey_data):
    """Store a journey data in the hard drive"""

    filename = create_filename_from_journey(journey_data["journey"])

    with open(f"journeys/{filename}.json", 'w') as file:
        json.dump(journey_data, file)

def store_file_new(journey_data):
    """Store a journey data in the hard drive"""
    journey = journey_data["journey"]["methodsJourneys"]
    filename = create_filename_from_journey_new(journey)
    with open(f"{JOURNEYS_FOLDER}/{filename}.json", 'w') as file:
        json.dump(journey_data, file)

def get_journey_files():
    """Return the dictionnary of all journeys recorded on the server"""

    res = []

    for journey_file in os.listdir(JOURNEYS_FOLDER):

        if journey_file[-5:] == ".json":

            with open(JOURNEYS_FOLDER + journey_file) as file:
                journey = json.load(file)

            res.append(journey)

    return res

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.post("/api/journey_data/new")
def receive_journey_data_new():
    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:
        journey_data = request.get_json()
        journey = journey_data["journey"]
        journey_str = journey_list_to_str_new(journey)
        date_str = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
        filename = f"{journey_str}#{date_str}.json"

        with open(f"{JOURNEYS_FOLDER}/{filename}", 'w') as file:
            json.dump(journey_data, file)
        return "Data successfully stored on the server", 201
    else:
        return "Too many files on the server", 507
    
@app.post("/api/journey_data")
def receive_journey_data():

    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:

        store_file(request.get_json())
        return "Data successfully stored on the server", 201
    
    else:
         return "Too many files on the server", 507
    
@app.get("/api/journey_data")
def send_journey_data():

    data = request.get_json()
    res = []

    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    

    res = get_journey_files()

    return res

@app.delete("/api/journey_data")
def delete_journey_data():
    """Delete all the journeys stored in the folder"""

    data = request.get_json()

    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    

    for filename in os.listdir(JOURNEYS_FOLDER):

        if filename[-5:] == ".json":
            os.remove(JOURNEYS_FOLDER + filename)

    return "Files were successfully deleted"


@app.get('/api/user/<user_id>')
def send_user(user_id):
    """
    API route used to get a user.
    Method:
    - GET
    Possible returns:
    - 200 (OK): Login successful, returns user.
    - 404 (Not Found): Indicates that the requested user was not found.
    - 500 (Internal Server Error): Error fetching user for unknown reason.
    """
    try:
        user = get_user(user_id)
        if user:
            return jsonify({"user": user}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching user: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@app.post("/api/user")
def receive_user():
    """
    API route used to register a new user.
    Method:
    - POST
    Expected JSON request:
        {
            "username": "User name",
            "password": "Password"
        }
    Possible returns:
    - 201 (Created): The user has been created successfully.
    - 400 (Bad Request): The user name already exists in the database.
    - 500 (Internal Server Error): User creation failed for an unknown reason.
    """
    try:
        data = request.json
        username = data.get('username')
        existing_user = get_user_by_username(username)
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400
        user = create_user(data)
        if user:
            return jsonify({"message": "User created successfully", "userId": str(user[0][0])}), 201
        else:
            return jsonify({"error": "Failed to create user"}), 500
    except Exception as e:
        app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

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
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user = get_user_by_username(username)
        if user and verify_user(username, password):
            user_id = str(user[0][0])
            return jsonify({'userId': user_id}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    
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
    try:
        if delete_user_by_id(user_id):
            return jsonify({"message": "User and associated data deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete user and associated data"}), 500
    except Exception as e:
        app.logger.error(f"Error deleting user and associated data: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    
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
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        journeys = cur.execute("SELECT * FROM Journeys WHERE userId=?", (user_id,)).fetchall()
        con.close()

        if journeys:
            # Convert each journey's methodsJson field from string to a list of methods
            journeys_list = [{
                "journeyId": journey[0],
                "userId": journey[1],
                "name": journey[2],
                "methodsJson": journey[3]
            } for journey in journeys]

            return jsonify({"journeys": journeys_list}), 200
        else:
            return jsonify({"error": "No journeys found for the given user ID"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching journeys for user: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

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
    try:
        data = request.json
        user_id = data.get('userId')
        name = data.get('name')
        methods_json = data.get('methodsJson')

        if not user_id or not name or not methods_json:
            return jsonify({"error": "Invalid input data"}), 400

        con = database.connect_to_db()
        cur = con.cursor()
        cur.execute("INSERT INTO Journeys (userId, name, methodsJson) VALUES (?, ?, ?)",
                    (user_id, name, methods_json))
        con.commit()
        journey_id = cur.lastrowid
        con.close()

        return jsonify({"message": "Journey created successfully", "journey": {"journeyId": journey_id, "userId": user_id, "name": name, "methodsJson": methods_json}}), 201
    except Exception as e:
        app.logger.error(f"Error creating journey: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500


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
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        specifications = cur.execute("SELECT * FROM MethodsSpecifications WHERE methodId=?", (method_id,)).fetchall()
        con.close()

        if specifications:
            return jsonify({"specifications": [{"specificationId": spec[0], "methodId": spec[1], "name": spec[2]} for spec in specifications]}), 200
        else:
            return jsonify({"error": "No specifications found for the given method ID"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching specifications for method: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

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
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        method = cur.execute("SELECT * FROM Methods WHERE methodId=?", (method_id,)).fetchone()
        con.close()

        if method:
            return jsonify({"method": {"methodId": method[0], "name": method[1]}}), 200
        else:
            return jsonify({"error": "No method found with the given ID"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching method details: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

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
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        journey = cur.execute("SELECT * FROM Journeys WHERE journeyId=?", (journey_id,)).fetchone()
        con.close()

        if journey:
            return jsonify({"journey": {"journeyId": journey[0], "userId": journey[1], "name": journey[2], "methods": json.loads(journey[3])}}), 200
        else:
            return jsonify({"error": "No journey found with the given ID"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching journey details: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

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
            "isPending": true
        }
    Possible returns:
    - 201 (Created): Record created successfully.
    - 500 (Internal Server Error): Error creating record.
    """
    try:
        data = request.json
        journey_id = data.get('journeyId')
        is_validated = data.get('isValidated', False)
        is_pending = data.get('isPending', True)

        con = database.connect_to_db()
        cur = con.cursor()
        cur.execute("INSERT INTO Records (journeyId, isValidated, isPending) VALUES (?, ?, ?)",
                    (journey_id, is_validated, is_pending))
        con.commit()
        record = cur.execute("SELECT * FROM Records WHERE recordId=?", (cur.lastrowid,)).fetchone()
        con.close()

        return jsonify({"message": "Record created successfully", "record": {"recordId": record[0], "journeyId": record[1], "isValidated": record[2], "isPending": record[3]}}), 201
    except Exception as e:
        app.logger.error(f"Error creating record: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    
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
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        methods = cur.execute("SELECT * FROM Methods").fetchall()
        
        methods_with_specifications = []
        for method in methods:
            method_id = method[0]
            specifications = cur.execute("SELECT * FROM MethodsSpecifications WHERE methodId=?", (method_id,)).fetchall()
            method_dict = {
                "methodId": method[0],
                "name": method[1],
                "specifications": [{"specificationId": spec[0], "methodId": spec[1], "name": spec[2]} for spec in specifications]
            }
            methods_with_specifications.append(method_dict)
        
        con.close()

        return jsonify({"methods": methods_with_specifications}), 200
    except Exception as e:
        app.logger.error(f"Error fetching methods and specifications: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500


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
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        result = cur.execute("DELETE FROM Journeys WHERE journeyId=?", (journey_id,))
        con.commit()
        con.close()

        if result.rowcount == 0:
            return jsonify({"error": "No journey found with the given ID"}), 404
        else:
            return jsonify({"message": "Journey deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting journey: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500


@app.route("/apps/gps_recorder")
def gps_recorder_page():

    return render_template("gps_record_app.html")

"""
a = rq.get("http://localhost:5000/api/journey_data", json={"password":"Zélie est une vilaine fille"})
aa = json.loads(a.text)

"""