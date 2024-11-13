from app.core.connection import get_db_connection


def sample_query_function():
    """
    This function is sample function for testing purposes
    """
    try:

        # Establish a database connection
        conn = get_db_connection()
        cur = conn.cursor()

        base_query = """
                write query here for insertion, deletion, update, delete
        """

        cur.execute(base_query, vars)
        results = cur.fetchall()

        cur.close()
        conn.close()

        return results
    except:
        return {}