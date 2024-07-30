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
            username, firstName, lastName, password, companyId, companyPositionId, points, score,
            lastMonthScore, lastMonthScoreDate, lastWeekPosition, lastWeekPositionDate, rewardGoalId
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['username'], data['firstName'], data['lastName'], data['password'], data['companyId'], data['companyPositionId'], 
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
        dict: The fetched user details.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    
    user_query = """
    SELECT u.userId, u.username, u.firstName, u.lastName, u.password, 
           u.companyId, c.name as companyName, 
           u.companyPositionId, cp.name as companyPositionName,
           u.points, u.score, u.lastMonthScore, u.lastMonthScoreDate,
           u.lastWeekPosition, u.lastWeekPositionDate, u.rewardGoalId,
           r.name as rewardName, r.cost, r.companyId as rewardCompanyId, rc.name as rewardCompanyName
    FROM Users u
    LEFT JOIN Companies c ON u.companyId = c.companyId
    LEFT JOIN CompanyPositions cp ON u.companyPositionId = cp.companyPositionId
    LEFT JOIN Rewards r ON u.rewardGoalId = r.rewardId
    LEFT JOIN Companies rc ON r.companyId = rc.companyId
    WHERE u.userId = ?
    """
    
    user = cur.execute(user_query, (user_id,)).fetchone()
    con.close()
    
    if user:
        userDic = {
            "userId": user[0],
            "username": user[1],
            "firstName": user[2],
            "lastName": user[3],
            "password": user[4],
            "company": {
                "companyId": user[5],
                "name": user[6]
            },
            "companyPosition": {
                "companyPositionId": user[7],
                "company": {
                    "companyId": user[5],
                    "name": user[6]
                },
                "name": user[8]
            },
            "points": user[9],
            "score": user[10],
            "lastMonthScore": user[11],
            "lastMonthScoreDate": user[12],
            "lastWeekPosition": user[13],
            "lastWeekPositionDate": user[14],
            "rewardGoal": {
                "rewardId": user[15],
                "cost": user[16],
                "company": {
                    "companyId": user[17],
                    "name": user[18]
                },
                "name": user[19]
            }
        }
        return userDic
    return None

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