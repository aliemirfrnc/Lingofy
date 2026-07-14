from backend.core.db import get_conn

def universal_search(query: str):
    """
    Dummy implementation of global search across users, prompts, incidents.
    """
    conn = get_conn()
    results = []
    
    # Search users
    cur = conn.execute("SELECT id, email FROM users WHERE email LIKE ? LIMIT 5", (f"%{query}%",))
    for row in cur.fetchall():
        results.append({"type": "USER", "id": row[0], "title": row[1]})
        
    # Search incidents
    cur = conn.execute("SELECT id, title FROM incidents WHERE title LIKE ? LIMIT 5", (f"%{query}%",))
    for row in cur.fetchall():
        results.append({"type": "INCIDENT", "id": row[0], "title": row[1]})
        
    # Search feature flags
    cur = conn.execute("SELECT id, flag_key FROM feature_flags WHERE flag_key LIKE ? LIMIT 5", (f"%{query}%",))
    for row in cur.fetchall():
        results.append({"type": "FEATURE_FLAG", "id": row[0], "title": row[1]})
        
    return {"results": results}
