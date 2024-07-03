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

#### Journey Data

- **POST** `/api/journey_data`
    - Stores a new journey data.
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

- **GET** `/api/journey_data`
    - Fetches all stored journey data.
    - Requires admin password in request body:
      ```json
      {
          "password": "Zélie est une vilaine fille"
      }
      ```

- **DELETE** `/api/journey_data`
    - Deletes all stored journey data.
    - Requires admin password in request body:
      ```json
      {
          "password": "Zélie est une vilaine fille"
      }
      ```

#### User Management

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

- **GET** `/api/user/<user_id>`
    - Fetches details of a specific user.

- **DELETE** `/api/user/<user_id>`
    - Deletes a specific user and their associated data.

#### Journey Management

- **GET** `/api/journey/user/<user_id>`
    - Fetches all journeys for a specific user.

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

- **GET** `/api/journey/<journey_id>`
    - Fetches details of a specific journey.

- **DELETE** `/api/journey/<journey_id>`
    - Deletes a specific journey.

#### Method Specifications

- **GET** `/api/specification/method/<method_id>`
    - Fetches specifications for a specific method.

- **GET** `/api/method/<method_id>`
    - Fetches details of a specific method.

- **GET** `/api/methods_with_specifications`
    - Fetches all methods with their specifications.

#### Records

- **POST** `/api/record`
    - Stores a new journey record.
    - Example request body:
      ```json
      {
          "journeyId": 1,
          "isValidated": false,
          "isPending": true
      }
      ```