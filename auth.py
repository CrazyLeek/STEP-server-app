from users import *
import os
from werkzeug.utils import secure_filename

def login_user(data):
    """
    Handle user login.

    Args:
        data (dict): Data for login containing 'username' and 'password'.

    Returns:
        tuple: Response message and status code.
    """
    username = data.get('username')
    password = data.get('password')
    user = get_user_by_username(username)
    if user and verify_user(username, password):
        user_id = str(user[0][0])
        return {'userId': user_id}, 200
    else:
        return {"error": "Invalid credentials"}, 401

def get_user_details(user_id):
    """
    Fetch user details by user ID.

    Args:
        user_id (int): ID of the user.

    Returns:
        tuple: Response message and status code.
    """
    user = get_user(user_id)
    if user:
        return {"user": user}, 200
    else:
        return {"error": "User not found"}, 404

def register_user(data, files):
    """
    Register a new user.

    Args:
        data (dict): Data for the new user.
        files (FileStorage): Files for the new user.

    Returns:
        tuple: Response message and status code.
    """
    username = data.get('username')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    password = data.get('password')
    company_id = 1
    company_position_id = 1
    points = 0
    score = 0
    last_month_score = 0
    last_month_score_date = None
    last_week_position = 0
    last_week_position_date = None
    reward_goal_id = None

    existing_user = get_user_by_username(username)
    if existing_user:
        return {"error": "Username already exists"}, 400

    user = create_user({
        'username': username,
        'firstName': first_name,
        'lastName': last_name,
        'password': password,
        'companyId': company_id,
        'companyPositionId' : company_position_id,
        'points': points,
        'score': score,
        'lastMonthScore': last_month_score,
        'lastMonthScoreDate': last_month_score_date,
        'lastWeekPosition': last_week_position,
        'lastWeekPositionDate': last_week_position_date,
        'rewardGoalId': reward_goal_id
    })

    if user:
        user_id = user[0][0]
        if 'profileImage' in files:
            save_profile_image(files['profileImage'], user_id)
        return {"message": "User created successfully", "userId": str(user_id)}, 201
    else:
        return {"error": "Failed to create user"}, 500
    
def save_profile_image(profile_image, user_id):
    """
    Save the profile image for a user.

    Args:
        profile_image (FileStorage): The profile image file.
        user_id (int): The ID of the user.
    """
    user_pictures_folder = 'user_pictures'
    if not os.path.exists(user_pictures_folder):
        os.makedirs(user_pictures_folder)
    
    filename = secure_filename(f"{user_id}.png")
    profile_image.save(os.path.join(user_pictures_folder, filename))

def remove_user(user_id):
    """
    Delete a specific user by user ID.

    Args:
        user_id (int): ID of the user to delete.

    Returns:
        tuple: Response message and status code.
    """
    if delete_user_by_id(user_id):
        return {"message": "User and associated data deleted successfully"}, 200
    else:
        return {"error": "Failed to delete user and associated data"}, 500
