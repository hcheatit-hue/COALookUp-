import os
import pyodbc
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

def get_connection():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    driver = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    encrypt = os.getenv("DB_ENCRYPT", "yes")
    trust_cert = os.getenv("DB_TRUST_CERT", "yes")

    conn_str_parts = [
        f"DRIVER={driver}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"Encrypt={encrypt}",
        f"TrustServerCertificate={trust_cert}",
    ]

    if user and password:
        conn_str_parts.append(f"UID={user}")
        conn_str_parts.append(f"PWD={password}")
    else:
        conn_str_parts.append("Trusted_Connection=yes")

    conn_str = ";".join(conn_str_parts)
    return pyodbc.connect(conn_str)


def run_query(sql, params=None):
    """Run a query and return list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Permission description helper (used inline in SQL, kept here for reference)
# ---------------------------------------------------------------------------
PERMISSION_LABELS = {
    "Y": "Full Access",
    "R": "Read Only",
    "N": "No Access",
}


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

SQL_USER_GROUPS = """
SELECT au.NAME AS UserName, g.ID AS GroupID, g.DESCRIPTION AS GroupDesc, gu.IS_LEADER
FROM APPLICATION_USER au
JOIN GROUP_USER gu ON au.NAME = gu.USER_ID
JOIN GROUPS g ON gu.GROUP_ID = g.ID
WHERE au.NAME = ?
ORDER BY g.ID;
"""

SQL_USER_PROFILES = """
SELECT up.USER_ID, up.PROFILE_ID, p.DESCRIPTION
FROM USER_PROFILE up
JOIN PROFILES p ON up.PROFILE_ID = p.ID
WHERE up.USER_ID = ?
ORDER BY up.PROFILE_ID;
"""

# All programs in the system, with this user's EFFECTIVE permission.
# (User override > Group > Profile > Default = Yes)
# Matches the SQL you provided (restricts to programs that appear in USER_PGM_AUTHORITY for user/group/profile).
SQL_USER_ALL_PROGRAMS = """
WITH AllPrograms AS (
    SELECT PROGRAM_ID FROM USER_PGM_AUTHORITY WHERE USER_ID = ?
    UNION
    SELECT upa.PROGRAM_ID FROM USER_PGM_AUTHORITY upa
    JOIN GROUP_USER gu ON upa.USER_ID = gu.GROUP_ID WHERE gu.USER_ID = ?
    UNION
    SELECT upa.PROGRAM_ID FROM USER_PGM_AUTHORITY upa
    JOIN USER_PROFILE up ON upa.USER_ID = up.PROFILE_ID WHERE up.USER_ID = ?
)
SELECT
    ap.PROGRAM_ID,
    pn.MENU_TEXT AS MenuString,
    COALESCE(user_perm.PERMISSION, group_perm.PERMISSION, profile_perm.PERMISSION, 'Y') AS Permission
FROM AllPrograms ap
LEFT JOIN (
    SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME
) pn ON pn.PROGRAM_ID = ap.PROGRAM_ID
LEFT JOIN USER_PGM_AUTHORITY user_perm
    ON user_perm.USER_ID = ? AND user_perm.PROGRAM_ID = ap.PROGRAM_ID
LEFT JOIN GROUP_USER gu
    ON gu.USER_ID = ?
LEFT JOIN USER_PGM_AUTHORITY group_perm
    ON group_perm.USER_ID = gu.GROUP_ID AND group_perm.PROGRAM_ID = ap.PROGRAM_ID
LEFT JOIN USER_PROFILE up
    ON up.USER_ID = ?
LEFT JOIN USER_PGM_AUTHORITY profile_perm
    ON profile_perm.USER_ID = up.PROFILE_ID AND profile_perm.PROGRAM_ID = ap.PROGRAM_ID
ORDER BY MenuString;
"""


# Search by Program ID or Menu string -> show every user + every profile + effective permission
SQL_SEARCH_PROGRAM_USERS = """
SELECT
    'USER' AS RecordType,
    au.NAME AS ID,
    pn.MENU_TEXT AS MenuString,
    pn.PROGRAM_ID,
    COALESCE(user_perm.PERMISSION, group_perm.PERMISSION, profile_perm.PERMISSION, 'Y') AS Permission
FROM APPLICATION_USER au
CROSS JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME WHERE PROGRAM_ID = ?) pn
LEFT JOIN USER_PGM_AUTHORITY user_perm ON user_perm.USER_ID = au.NAME AND user_perm.PROGRAM_ID = pn.PROGRAM_ID
LEFT JOIN GROUP_USER gu ON gu.USER_ID = au.NAME
LEFT JOIN USER_PGM_AUTHORITY group_perm ON group_perm.USER_ID = gu.GROUP_ID AND group_perm.PROGRAM_ID = pn.PROGRAM_ID
LEFT JOIN USER_PROFILE up ON up.USER_ID = au.NAME
LEFT JOIN USER_PGM_AUTHORITY profile_perm ON profile_perm.USER_ID = up.PROFILE_ID AND profile_perm.PROGRAM_ID = pn.PROGRAM_ID

UNION ALL

SELECT
    'PROFILE' AS RecordType,
    p.ID AS ID,
    pn.MENU_TEXT AS MenuString,
    pn.PROGRAM_ID,
    COALESCE(profile_perm.PERMISSION, 'Y') AS Permission
FROM PROFILES p
CROSS JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME WHERE PROGRAM_ID = ?) pn
LEFT JOIN USER_PGM_AUTHORITY profile_perm ON profile_perm.USER_ID = p.ID AND profile_perm.PROGRAM_ID = pn.PROGRAM_ID

ORDER BY RecordType, ID;
"""

SQL_SEARCH_MENUTEXT_USERS = """
SELECT
    'USER' AS RecordType,
    au.NAME AS ID,
    pn.MENU_TEXT AS MenuString,
    pn.PROGRAM_ID,
    COALESCE(user_perm.PERMISSION, group_perm.PERMISSION, profile_perm.PERMISSION, 'Y') AS Permission
FROM APPLICATION_USER au
CROSS JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME WHERE MENU_TEXT LIKE ?) pn
LEFT JOIN USER_PGM_AUTHORITY user_perm ON user_perm.USER_ID = au.NAME AND user_perm.PROGRAM_ID = pn.PROGRAM_ID
LEFT JOIN GROUP_USER gu ON gu.USER_ID = au.NAME
LEFT JOIN USER_PGM_AUTHORITY group_perm ON group_perm.USER_ID = gu.GROUP_ID AND group_perm.PROGRAM_ID = pn.PROGRAM_ID
LEFT JOIN USER_PROFILE up ON up.USER_ID = au.NAME
LEFT JOIN USER_PGM_AUTHORITY profile_perm ON profile_perm.USER_ID = up.PROFILE_ID AND profile_perm.PROGRAM_ID = pn.PROGRAM_ID

UNION ALL

SELECT
    'PROFILE' AS RecordType,
    p.ID AS ID,
    pn.MENU_TEXT AS MenuString,
    pn.PROGRAM_ID,
    COALESCE(profile_perm.PERMISSION, 'Y') AS Permission
FROM PROFILES p
CROSS JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME WHERE MENU_TEXT LIKE ?) pn
LEFT JOIN USER_PGM_AUTHORITY profile_perm ON profile_perm.USER_ID = p.ID AND profile_perm.PROGRAM_ID = pn.PROGRAM_ID

ORDER BY RecordType, ID;
"""

# All distinct menu strings, for autocomplete / browsing
SQL_ALL_MENU_STRINGS = """
SELECT DISTINCT PROGRAM_ID, MENU_TEXT
FROM PROGRAM_NAME
WHERE MENU_TEXT IS NOT NULL
ORDER BY MENU_TEXT;
"""

# All users (for autocomplete / browsing)
SQL_ALL_USERS = """
SELECT NAME FROM APPLICATION_USER ORDER BY NAME;
"""

# Field-level permissions for a user (direct + group + profile, default Yes)
SQL_USER_FIELD_PERMS = """
WITH AllFields AS (
    SELECT PROGRAM_ID, PROGRAM_FIELD FROM USER_FLD_AUTHORITY WHERE USER_ID = ?
    UNION
    SELECT ufa.PROGRAM_ID, ufa.PROGRAM_FIELD FROM USER_FLD_AUTHORITY ufa
    JOIN GROUP_USER gu ON ufa.USER_ID = gu.GROUP_ID WHERE gu.USER_ID = ?
    UNION
    SELECT ufa.PROGRAM_ID, ufa.PROGRAM_FIELD FROM USER_FLD_AUTHORITY ufa
    JOIN USER_PROFILE up ON ufa.USER_ID = up.PROFILE_ID WHERE up.USER_ID = ?
)
SELECT
    af.PROGRAM_ID,
    af.PROGRAM_FIELD,
    COALESCE(user_perm.PERMISSION, group_perm.PERMISSION, profile_perm.PERMISSION, 'Y') AS Permission
FROM AllFields af
LEFT JOIN USER_FLD_AUTHORITY user_perm
    ON user_perm.USER_ID = ? AND user_perm.PROGRAM_ID = af.PROGRAM_ID AND user_perm.PROGRAM_FIELD = af.PROGRAM_FIELD
LEFT JOIN GROUP_USER gu ON gu.USER_ID = ?
LEFT JOIN USER_FLD_AUTHORITY group_perm
    ON group_perm.USER_ID = gu.GROUP_ID AND group_perm.PROGRAM_ID = af.PROGRAM_ID AND group_perm.PROGRAM_FIELD = af.PROGRAM_FIELD
LEFT JOIN USER_PROFILE up ON up.USER_ID = ?
LEFT JOIN USER_FLD_AUTHORITY profile_perm
    ON profile_perm.USER_ID = up.PROFILE_ID AND profile_perm.PROGRAM_ID = af.PROGRAM_ID AND profile_perm.PROGRAM_FIELD = af.PROGRAM_FIELD
ORDER BY af.PROGRAM_ID, af.PROGRAM_FIELD;
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("indexuser.html")


@app.route("/api/users")
def api_users():
    """All usernames, for autocomplete."""
    rows = run_query(SQL_ALL_USERS)
    return jsonify([r["NAME"] for r in rows])


@app.route("/api/programs")
def api_programs():
    """All distinct (PROGRAM_ID, MENU_TEXT) pairs, for autocomplete."""
    rows = run_query(SQL_ALL_MENU_STRINGS)
    return jsonify(rows)


@app.route("/api/user/<user_id>/groups")
def api_user_groups(user_id):
    rows = run_query(SQL_USER_GROUPS, (user_id,))
    return jsonify(rows)


@app.route("/api/user/<user_id>/profiles")
def api_user_profiles(user_id):
    rows = run_query(SQL_USER_PROFILES, (user_id,))
    return jsonify(rows)


@app.route("/api/user/<user_id>/programs")
def api_user_programs(user_id):
    """All programs with this user's effective permission."""
    rows = run_query(SQL_USER_ALL_PROGRAMS, (user_id, user_id, user_id))
    for r in rows:
        r["PermissionDesc"] = PERMISSION_LABELS.get(r["Permission"], r["Permission"])
    return jsonify(rows)


@app.route("/api/user/<user_id>/fields")
def api_user_fields(user_id):
    """All field-level permissions for this user."""
    rows = run_query(SQL_USER_FIELD_PERMS, (user_id, user_id, user_id, user_id, user_id, user_id))
    for r in rows:
        r["PermissionDesc"] = PERMISSION_LABELS.get(r["Permission"], r["Permission"])
    return jsonify(rows)


@app.route("/api/search")
def api_search():
    """
    Search by program_id OR menu_text, return every user + profile
    with their effective permission for that program.

    Query params:
      program_id=VMSHPENT   -> exact match on PROGRAM_ID
      menu_text=Shipping    -> partial (LIKE) match on MENU_TEXT
      access=Y,R,N          -> optional filter on effective permission
    """
    program_id = request.args.get("program_id", "").strip()
    menu_text = request.args.get("menu_text", "").strip()
    access_filter = request.args.get("access", "").strip()

    if not program_id and not menu_text:
        return jsonify({"error": "Provide program_id or menu_text"}), 400

    if program_id:
        rows = run_query(SQL_SEARCH_PROGRAM_USERS, (program_id, program_id))
    else:
        like_term = f"%{menu_text}%"
        rows = run_query(SQL_SEARCH_MENUTEXT_USERS, (like_term, like_term))

    if access_filter:
        allowed = set(a.strip().upper() for a in access_filter.split(","))
        rows = [r for r in rows if r["Permission"] in allowed]

    for r in rows:
        r["PermissionDesc"] = PERMISSION_LABELS.get(r["Permission"], r["Permission"])

    return jsonify(rows)


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5055))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host=host, port=port, debug=debug)