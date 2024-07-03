from hashlib import sha256
import database

def create_user(data):
    """
    Creates a new user with a username and hashed password.

    Args:
        data (dict): Data for the user to be created.

    Returns:
        user: The newly created user.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO Users (
            username, firstName, lastName, password, companyId, points, score,
            lastMonthScore, lastMonthScoreDate, lastWeekPosition, lastWeekPositionDate, rewardGoalId
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['username'], data['firstName'], data['lastName'], data['password'], data['companyId'], 
        data['points'], data['score'], data['lastMonthScore'], data['lastMonthScoreDate'],
        data['lastWeekPosition'], data['lastWeekPositionDate'], data['rewardGoalId']
    ))
    con.commit()
    inserted_user = cur.execute("SELECT * FROM Users WHERE username=?", (data['username'],)).fetchall()
    con.close()
    return inserted_user

def get_user(user_id):
    """
    Get a specific user by its identifier.

    Args:
        user_id (int): Identifier of the user to fetch.

    Returns:
        user: The fetched user.
    """
    userDic = {}
    con = database.connect_to_db()
    cur = con.cursor()
    user = cur.execute("SELECT * FROM Users WHERE userId=?", (user_id,)).fetchall()
    con.close()
    if user:
        userDic['userId'] = user[0][0]
        userDic['username'] = user[0][1]
    return user

def get_user_by_username(username):
    """
    Get a specific user by username.

    Args:
        username (str): Username of the user to fetch.

    Returns:
        user: The fetched user.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    user = cur.execute("SELECT * FROM Users WHERE username=?", (username,)).fetchall()
    con.close()
    return user

def verify_user(username, password):
    """
    Checks user credentials.

    Args:
        username (str): Username of the user to be verified.
        password (str): Password to verify.

    Returns:
        bool: True if credentials are valid, otherwise False.
    """
    user = get_user_by_username(username)
    if user and user[0][4] == password:
        return True
    return False

def delete_user_by_id(user_id):
    """
    Deletes a specific user.

    Args:
        user_id (int): ID of the user to delete.

    Returns:
        bool: True if the user was successfully deleted, otherwise False.
    """
    try:
        con = database.connect_to_db()
        cur = con.cursor()
        cur.execute("DELETE FROM Users WHERE userId = ?", (user_id,))
        con.commit()
        deleted_user = cur.execute("SELECT * FROM Users WHERE userId=?", (user_id,)).fetchone()
        if deleted_user is None:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error deleting user and associated data: {str(e)}")
        return False