import database

def get_method_specifications(method_id):
    """
    Get specifications for a specific method.

    Args:
        method_id (int): ID of the method.

    Returns:
        tuple: Response message and status code.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    specifications = cur.execute("SELECT * FROM MethodsSpecifications WHERE methodId=?", (method_id,)).fetchall()
    con.close()
    if specifications:
        return {"specifications": [{"specificationId": spec[0], "methodId": spec[1], "name": spec[2]} for spec in specifications]}, 200
    else:
        return {"error": "No specifications found for the given method ID"}, 404
    
def get_method_details(method_id):
    """
    Get details of a specific method.

    Args:
        method_id (int): ID of the method.

    Returns:
        tuple: Response message and status code.
    """
    con = database.connect_to_db()
    cur = con.cursor()
    method = cur.execute("SELECT * FROM Methods WHERE methodId=?", (method_id,)).fetchone()
    con.close()
    if method:
        return {"method": {"methodId": method[0], "name": method[1]}}, 200
    else:
        return {"error": "No method found with the given ID"}, 404

def get_all_methods_with_specifications():
    """
    Get all methods with their specifications.

    Returns:
        tuple: Response message and status code.
    """
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
    return {"methods": methods_with_specifications}, 200