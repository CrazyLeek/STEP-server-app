import os, json, datetime

from flask import Flask, request, render_template

# The maximum number of journey files the server will store
MAX_JOURNEY_FILES = 1000

# The folder were jouneys are stored
JOURNEYS_FOLDER = "journeys/"

# The password to fetch the journey stored on the server
ADMIN_PASSWORD = "Zélie est une vilaine fille"

app = Flask(__name__)


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


def store_file(journey_data):
    """Store a journey data in the hard drive"""

    filename = create_filename_from_journey(journey_data["journey"])

    with open(f"journeys/{filename}.json", 'w') as file:
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

@app.post("/api/journey_data")
def receive_journey_data():

    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:

        store_file(request.get_json())
        return "Data successfully stored on the server"
    
    else:
         return "Too many files on the server"
    
@app.get("/api/journey_data")
def send_journey_data():

    data = request.get_json()
    res = []

    if "password" in data and data["password"] == ADMIN_PASSWORD:
        res = get_journey_files()


    return res

@app.route("/apps/gps_recorder")
def gps_recorder_page():

    return render_template("gps_record_app.html")


"""
a = rq.get("http://localhost:5000/api/journey_data", json={"password":"Zélie est une vilaine fille"})
aa = json.loads(a.text)

"""