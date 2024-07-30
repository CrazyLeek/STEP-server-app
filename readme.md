# Step TCD Rail

## Setup

### Virtual Environment

To work with this project, you need to activate the virtual environment:

```sh
pyenv activate website
```

### Running the Server

To run the Flask server, use the following command (Note: It is recommended to use a production server like Gunicorn for running Flask in production):

```sh
FLASK_RUN_PORT=8003 nohup flask run &
```

After launching the server, you can check if everything is fine with:

```sh
cat nohup.out
```

### Stopping the Server

To stop the server, use:

```sh
sudo fuser -k 8003/tcp
```

## Routes for https://step.tcdrail.com/

### Web Pages

- **GPS Recorder**: `/apps/gps_recorder`

- **STEP App**:  `/apps/step`

### API Endpoints

#### User

- **GET** `/api/user/<user_id>`
    - Fetches details of a specific user.

- **GET** `/api/user_profile_image/<user_id>`
    - Fetches the profile image of a specific user.

- **POST** `/api/user`
    - Registers a new user.
    - Example request body:
      ```json
      {
          "username": "username",
          "firstName": "First name",
          "lastName": "Last name",
          "password": "password"
      }
      ```

- **POST** `/api/login`
    - Authenticates a user.
    - Example request body:
      ```json
      {
          "username": "username",
          "password": "password"
      }
      ```

- **DELETE** `/api/user/<user_id>`
    - Deletes a specific user and their associated data.

#### Journey

- **GET** `/api/journey_data`
    - Fetches all stored journey data.
    - Requires admin password in request body:
      ```json
      {
          "password": "Zélie est une vilaine fille"
      }
      ```

- **GET** `/api/journey/user/<user_id>`
    - Fetches all journeys for a specific user.

- **GET** `/api/journey/<journey_id>`
    - Fetches details of a specific journey.

- **POST** `/api/journey_data/new`
    - Stores new journey data.
    - Example request body:
      ```json
      {
          "journey": [
              ["walk", null],
              ["bus", "83"],
              ["luas", "Red"]
          ],
          "gps": [[-6.2522889, 53.3424784, "2024-06-28T12:21:14.912Z"]],
          "realtime": []
      }
      ```

- **POST** `/api/journey_data`
    - Stores journey data.
    - Example request body:
      ```json
      {
          "journey": [
              ["walk", null],
              ["bus", "83"],
              ["luas", "Red"]
          ],
          "gps": [[-6.2522889, 53.3424784, "2024-06-28T12:21:14.912Z"]],
          "realtime": []
      }
      ```

- **POST** `/api/journey`
    - Stores a new journey.
    - Example request body:
      ```json
      {
          "userId": 1,
          "name": "Journey name",
          "methodsJson": "{\"journey\":[{\"method\":{\"methodId\":4,\"name\":\"Bike\"},\"methodSpecifications\":[]},{\"method\":{\"methodId\":2,\"name\":\"Bus\"},\"methodSpecifications\":[{\"specificationId\":8,\"methodId\":2,\"name\":\"120\"}]}]}"
      }
      ```

- **POST** `/api/upload_journey_file`
    - Uploads a journey file.
    - Example request body (multipart form-data):
      - file: The JSON file containing journey data.
    - Responses:
      - 201 (Created): File successfully uploaded and stored.
      - 400 (Bad Request): No file part or no selected file.
      - 507 (Insufficient Storage): Too many files on the server.

- **DELETE** `/api/journey/<journey_id>`
    - Deletes a specific journey.

- **DELETE** `/api/journey_data`
    - Deletes all stored journey data.
    - Requires admin password in request body:
      ```json
      {
          "password": "Zélie est une vilaine fille"
      }
      ```    

#### Methods & Specifications

- **GET** `/api/specification/method/<method_id>`
    - Fetches specifications for a specific method.

- **GET** `/api/method/<method_id>`
    - Fetches details of a specific method.

- **GET** `/api/methods_with_specifications`
    - Fetches all methods with their specifications.

#### Records

- **GET** `/api/user-records/<int:user_id>`
    - Fetches all records for a specific user.

- **POST** `/api/analyse_journey_file`
    - Analyzes a journey file.
    - Example request body (multipart form-data):
      - file: The JSON file containing journey data.
      - recordId: The ID of the journey record.
      - username: The username of the user.
    - Responses:
      - 200 (OK): File successfully analyzed.
      - 400 (Bad Request): No file part or recordId or username.
      - 500 (Internal Server Error): Error during file analysis.

- **POST** `/api/record`
    - Stores a new journey record.
    - Example request body:
      ```json
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
      ```
      
#### Statistics

- **GET** `/api/carbon_emission_stats`
    - Fetches carbon emission statistics.

- **GET** `/api/kilometers_stats`
    - Fetches kilometers statistics.

- **GET** `/api/usage_stats`
    - Fetches usage statistics.

#### Weekly Roundup

- **GET** `/api/weekly-roundup/<int:user_id>`
    - Fetches the weekly roundup for a specific user.

### App Pages

- **GPS Recorder Page**
  ```
  GET /apps/gps_recorder
  ```
  - Renders the GPS recorder app page.

- **STEP App Page**
  ```
  GET /apps/step
  ```
  - Renders the STEP app page.