import os, json, datetime
import database

JOURNEYS_FOLDER = "journeys/"

MAX_JOURNEY_FILES = 1000

def journey_list_to_str_new(journey):
    """
    Convert a journey to a string.

    Args:
        journey (list): List of journey segments.

    Returns:
        str: Journey string.
    """
    res = []
    for trip in journey:
        method = trip[0]
        line = trip[1] if len(trip) > 1 and trip[1] else ''
        res.append(f"{method}-{line}" if line else method)
    return '_'.join(res)

def journey_list_to_str(journey):
    """
    Convert a journey to a string.

    Args:
        journey (list): List of journey segments.

    Returns:
        str: Journey string.
    """
    MODE, LINE = 0, 1
    res = []
    for trip in journey:
        if trip[MODE] in ("walk", "bike", "car", "dart"):
            res.append(trip[MODE])
        else:
            res.append(trip[MODE] + "-" + trip[LINE])
    return '_'.join(res)

def create_filename_from_journey(journey):
    """
    Create a filename from a journey.

    Args:
        journey (list): List of journey segments.

    Returns:
        str: Filename string.
    """
    journey_str = journey_list_to_str(journey)
    date_str = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
    return journey_str + "#" + date_str

def create_filename_from_journey_new(journey):
    """
    Create a filename from a journey.

    Args:
        journey (list): List of journey segments.

    Returns:
        str: Filename string.
    """
    journey_str = journey_list_to_str_new(journey)
    date_str = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
    return f"{journey_str}#{date_str}"

def store_file(journey_data):
    """
    Store journey data to a file.

    Args:
        journey_data (dict): Journey data.
    """
    filename = create_filename_from_journey(journey_data["journey"])
    with open(f"journeys/{filename}.json", 'w') as file:
        json.dump(journey_data, file)

def store_file_new(journey_data):
    """
    Store journey data to a file.

    Args:
        journey_data (dict): Journey data.
    """
    journey = journey_data["journey"]["methodsJourneys"]
    filename = create_filename_from_journey_new(journey)
    with open(f"{JOURNEYS_FOLDER}/{filename}.json", 'w') as file:
        json.dump(journey_data, file)

def get_journey_files():
    """
    Get all journey files.

    Returns:
        list: List of journey data.
    """
    res = []
    for journey_file in os.listdir(JOURNEYS_FOLDER):
        if journey_file.endswith(".json"):
            with open(JOURNEYS_FOLDER + journey_file) as file:
                journey = json.load(file)
            res.append(journey)
    return res

def delete_all_journey_files():
    """
    Delete all journey files.

    Returns:
        str: Deletion status message.
    """
    for filename in os.listdir(JOURNEYS_FOLDER):
        if filename.endswith(".json"):
            os.remove(JOURNEYS_FOLDER + filename)
    return "Files were successfully deleted"

def store_journey_file(journey_data):
    """
    Store a new journey file.

    Args:
        journey_data (dict): Journey data.

    Returns:
        tuple: Response message and status code.
    """
    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:
        journey = journey_data["journey"]
        journey_str = journey_list_to_str_new(journey)
        date_str = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
        filename = f"{journey_str}#{date_str}.json"
        with open(f"{JOURNEYS_FOLDER}/{filename}", 'w') as file:
            json.dump(journey_data, file)
        return "Data successfully stored on the server", 201
    else:
        return "Too many files on the server", 507

def store_journey(data):
    """
    Store a new journey.

    Args:
        data (dict): Journey data.

    Returns:
        tuple: Response message and status code.
    """
    user_id = data.get('userId')
    name = data.get('name')
    methods_json = data.get('methodsJson')
    if not user_id or not name or not methods_json:
        return {"error": "Invalid input data"}, 400
    con = database.connect_to_db()
    cur = con.cursor()
    cur.execute("INSERT INTO Journeys (userId, name, methodsJson) VALUES (?, ?, ?)", (user_id, name, methods_json))
    con.commit()
    journey_id = cur.lastrowid
    con.close()
    return {"message": "Journey created successfully", "journey": {"journeyId": journey_id, "userId": user_id, "name": name, "methodsJson": methods_json}}, 201

def get_user_journeys(user_id):
    """
    Get all journeys for a specific user.

    Args:
        user_id (int): ID of the user.

    Returns:
        tuple: Response message and status code.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    journeys = cur.execute("SELECT * FROM Journeys WHERE userId=?", (user_id,)).fetchall()
    con.close()
    if journeys:
        journeys_list = [{"journeyId": journey[0], "userId": journey[1], "name": journey[2], "methodsJson": journey[3]} for journey in journeys]
        return {"journeys": journeys_list}, 200
    else:
        return {"error": "No journeys found for the given user ID"}, 404

def get_journey_details(journey_id):
    """
    Get details of a specific journey.

    Args:
        journey_id (int): ID of the journey.

    Returns:
        tuple: Response message and status code.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    journey = cur.execute("SELECT * FROM Journeys WHERE journeyId=?", (journey_id,)).fetchone()
    con.close()
    if journey:
        return {"journey": {"journeyId": journey[0], "userId": journey[1], "name": journey[2], "methods": json.loads(journey[3])}}, 200
    else:
        return {"error": "No journey found with the given ID"}, 404

def remove_journey(journey_id):
    """
    Delete a specific journey by journey ID.

    Args:
        journey_id (int): ID of the journey to delete.

    Returns:
        tuple: Response message and status code.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    result = cur.execute("DELETE FROM Journeys WHERE journeyId=?", (journey_id,))
    con.commit()
    con.close()
    if result.rowcount == 0:
        return {"error": "No journey found with the given ID"}, 404
    else:
        return {"message": "Journey deleted successfully"}, 200