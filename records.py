import sqlite3
import database

def get_all_user_records(user_id):    
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
    
    records = cur.execute(query, (user_id,)).fetchall()
    records_list = []
    
    for record in records:
        record_dict = dict(record)
        record_dict['journey'] = {'name': record_dict['journey_name']} if record_dict.get('journey_name') else None
        del record_dict['journey_name']
        records_list.append(record_dict)
    
    cur.close()
    con.close()

    return records_list

def store_record(data):
    """
    Store a new journey record.

    Args:
        data (dict): Record data.

    Returns:
        tuple: Response message and status code.
    """
    journey_id = data.get('journeyId')
    is_validated = data.get('isValidated', False)
    is_pending = data.get('isPending', True)
    json_file_name = data.get('jsonFileName')
    points = data.get('points', 0)
    co2_saved = data.get('co2Saved', 0)
    start_date = data.get('startDate')
    end_date = data.get('endDate')

    con = database.connect_to_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO Records (journeyId, isValidated, isPending, jsonFileName, points, co2Saved, startDate, endDate) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (journey_id, is_validated, is_pending, json_file_name, points, co2_saved, start_date, end_date))
    con.commit()
    record = cur.execute("SELECT * FROM Records WHERE recordId=?", (cur.lastrowid,)).fetchone()
    con.close()

    return {
        "message": "Record created successfully",
        "record": {
            "recordId": record[0],
            "journeyId": record[1],
            "isValidated": record[2],
            "isPending": record[3],
            "jsonFileName": record[4],
            "points": record[5],
            "co2Saved": record[6],
            "nbMethodUsed": record[7],
            "kmTravelled": record[8],
            "startDate": record[9],
            "endDate": record[10]
        }
    }, 201