import os
import pyodbc
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Database connection  (READ-ONLY app — every query below is a SELECT only)
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
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def run_scalar(sql, params=None):
    rows = run_query(sql, params)
    if not rows:
        return None
    return list(rows[0].values())[0]


PERMISSION_LABELS = {"Y": "Full Access", "R": "Read Only", "N": "No Access"}


def add_permission_desc(rows, key="Permission"):
    for r in rows:
        r["PermissionDesc"] = PERMISSION_LABELS.get(r.get(key), r.get(key))
    return rows


# ---------------------------------------------------------------------------
# SQL — Overview / KPIs
# ---------------------------------------------------------------------------

SQL_KPI_COUNTS = """
SELECT
    (SELECT COUNT(*) FROM APPLICATION_USER) AS TotalUsers,
    (SELECT COUNT(*) FROM APPLICATION_USER WHERE IS_VISUAL_USER = 'Y') AS VisualUsers,
    (SELECT COUNT(*) FROM APPLICATION_USER WHERE IS_ADMIN = 'Y') AS AdminUsers,
    (SELECT COUNT(*) FROM APPLICATION_USER WHERE IS_PROFILE = 'Y') AS ProfileFlaggedUsers,
    (SELECT COUNT(*) FROM GROUPS) AS TotalGroups,
    (SELECT COUNT(*) FROM PROFILES) AS TotalProfiles,
    (SELECT COUNT(DISTINCT PROGRAM_ID) FROM PROGRAM_NAME) AS TotalPrograms,
    (SELECT COUNT(*) FROM APPLICATION_USER WHERE RESET_PW_NEXT_LOGIN = 'Y') AS PendingPasswordResets,
    (SELECT COUNT(*) FROM APPLICATION_USER WHERE FAILED_COUNT > 0) AS UsersWithFailedLogins;
"""

SQL_USERS_WITH_NO_GROUP = """
SELECT au.NAME AS UserName
FROM APPLICATION_USER au
LEFT JOIN GROUP_USER gu ON gu.USER_ID = au.NAME
LEFT JOIN USER_PROFILE up ON up.USER_ID = au.NAME
WHERE au.IS_VISUAL_USER = 'Y'
  AND gu.USER_ID IS NULL
  AND up.USER_ID IS NULL
ORDER BY au.NAME;
"""

SQL_RECENT_FAILED_LOGINS = """
SELECT NAME AS UserName, FAILED_COUNT, LAST_FAILED_DATE
FROM APPLICATION_USER
WHERE IS_VISUAL_USER = 'Y'
  AND FAILED_COUNT > 0
ORDER BY LAST_FAILED_DATE DESC;
"""

SQL_ADMIN_USERS = """
SELECT NAME AS UserName, IS_VISUAL_USER, PASS_LAST_CHANGED, RESET_PW_NEXT_LOGIN
FROM APPLICATION_USER
WHERE IS_ADMIN = 'Y'
  AND IS_VISUAL_USER = 'Y'
ORDER BY NAME;
"""

# ---------------------------------------------------------------------------
# SQL — Users
# ---------------------------------------------------------------------------

SQL_ALL_USERS_BASIC = """
SELECT
    NAME AS UserName,
    IS_VISUAL_USER,
    IS_ADMIN,
    IS_PLANNER,
    IS_BUYER,
    IS_PROFILE,
    PASS_LAST_CHANGED,
    RESET_PW_NEXT_LOGIN,
    FAILED_COUNT,
    LAST_FAILED_DATE
FROM APPLICATION_USER
WHERE IS_VISUAL_USER = 'Y'
ORDER BY NAME;
"""

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

SQL_USER_ALL_PROGRAMS = """
WITH AllPrograms AS (
    SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME
)
SELECT
    ap.PROGRAM_ID,
    ap.MENU_TEXT AS MenuString,
    COALESCE(user_perm.PERMISSION, group_perm.PERMISSION, profile_perm.PERMISSION, 'Y') AS Permission,
    CASE
        WHEN user_perm.PERMISSION IS NOT NULL THEN 'User override'
        WHEN group_perm.PERMISSION IS NOT NULL THEN 'Via group'
        WHEN profile_perm.PERMISSION IS NOT NULL THEN 'Via profile'
        ELSE 'Default'
    END AS Source
FROM AllPrograms ap
LEFT JOIN USER_PGM_AUTHORITY user_perm
    ON user_perm.USER_ID = ? AND user_perm.PROGRAM_ID = ap.PROGRAM_ID
LEFT JOIN GROUP_USER gu ON gu.USER_ID = ?
LEFT JOIN USER_PGM_AUTHORITY group_perm
    ON group_perm.USER_ID = gu.GROUP_ID AND group_perm.PROGRAM_ID = ap.PROGRAM_ID
LEFT JOIN USER_PROFILE up ON up.USER_ID = ?
LEFT JOIN USER_PGM_AUTHORITY profile_perm
    ON profile_perm.USER_ID = up.PROFILE_ID AND profile_perm.PROGRAM_ID = ap.PROGRAM_ID
ORDER BY ap.MENU_TEXT;
"""

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
# SQL — Groups
# ---------------------------------------------------------------------------

SQL_ALL_GROUPS = """
SELECT
    g.ID AS GroupID,
    g.DESCRIPTION,
    g.SITE_ID,
    (
    SELECT COUNT(*)
    FROM GROUP_USER gu
    JOIN APPLICATION_USER au
        ON au.NAME = gu.USER_ID
    WHERE gu.GROUP_ID = g.ID
      AND au.IS_VISUAL_USER = 'Y'
) AS MemberCount
    (SELECT COUNT(*) FROM USER_PGM_AUTHORITY upa WHERE upa.USER_ID = g.ID) AS DirectProgramRules
FROM GROUPS g
ORDER BY g.ID;
"""

SQL_GROUP_MEMBERS = """
SELECT gu.USER_ID AS UserName, gu.IS_LEADER, au.IS_ADMIN, au.IS_VISUAL_USER
FROM GROUP_USER gu
LEFT JOIN APPLICATION_USER au ON au.NAME = gu.USER_ID
WHERE gu.GROUP_ID = ?
ORDER BY gu.USER_ID;
"""

SQL_GROUP_PROGRAM_RULES = """
SELECT upa.PROGRAM_ID, pn.MENU_TEXT AS MenuString, upa.PERMISSION
FROM USER_PGM_AUTHORITY upa
LEFT JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME) pn
    ON pn.PROGRAM_ID = upa.PROGRAM_ID
WHERE upa.USER_ID = ?
ORDER BY pn.MENU_TEXT;
"""

# ---------------------------------------------------------------------------
# SQL — Profiles
# ---------------------------------------------------------------------------

SQL_ALL_PROFILES = """
SELECT
    p.ID AS ProfileID,
    p.DESCRIPTION,
    (SELECT COUNT(*) FROM USER_PROFILE up WHERE up.PROFILE_ID = p.ID) AS AssignedUserCount,
    (SELECT COUNT(*) FROM USER_PGM_AUTHORITY upa WHERE upa.USER_ID = p.ID) AS DirectProgramRules
FROM PROFILES p
ORDER BY p.ID;
"""

SQL_PROFILE_MEMBERS = """
SELECT up.USER_ID AS UserName, au.IS_ADMIN, au.IS_VISUAL_USER
FROM USER_PROFILE up
LEFT JOIN APPLICATION_USER au ON au.NAME = up.USER_ID
WHERE up.PROFILE_ID = ?
ORDER BY up.USER_ID;
"""

SQL_PROFILE_PROGRAM_RULES = """
SELECT upa.PROGRAM_ID, pn.MENU_TEXT AS MenuString, upa.PERMISSION
FROM USER_PGM_AUTHORITY upa
LEFT JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME) pn
    ON pn.PROGRAM_ID = upa.PROGRAM_ID
WHERE upa.USER_ID = ?
ORDER BY pn.MENU_TEXT;
"""

# ---------------------------------------------------------------------------
# SQL — Programs / search
# ---------------------------------------------------------------------------

SQL_ALL_MENU_STRINGS = """
SELECT DISTINCT PROGRAM_ID, MENU_TEXT
FROM PROGRAM_NAME
WHERE MENU_TEXT IS NOT NULL
ORDER BY MENU_TEXT;
"""

SQL_SEARCH_PROGRAM_USERS = """
SELECT
    'USER' AS RecordType,
    au.NAME AS ID,
    pn.MENU_TEXT AS MenuString,
    pn.PROGRAM_ID,
    COALESCE(user_perm.PERMISSION, group_perm.PERMISSION, profile_perm.PERMISSION, 'Y') AS Permission
FROM (
    SELECT *
    FROM APPLICATION_USER
    WHERE IS_VISUAL_USER = 'Y'
) au
CROSS JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME WHERE PROGRAM_ID = ?) pn
LEFT JOIN USER_PGM_AUTHORITY user_perm ON user_perm.USER_ID = au.NAME AND user_perm.PROGRAM_ID = pn.PROGRAM_ID
LEFT JOIN GROUP_USER gu ON gu.USER_ID = au.NAME
LEFT JOIN USER_PGM_AUTHORITY group_perm ON group_perm.USER_ID = gu.GROUP_ID AND group_perm.PROGRAM_ID = pn.PROGRAM_ID
LEFT JOIN USER_PROFILE up ON up.USER_ID = au.NAME
LEFT JOIN USER_PGM_AUTHORITY profile_perm ON profile_perm.USER_ID = up.PROFILE_ID AND profile_perm.PROGRAM_ID = pn.PROGRAM_ID
WHERE au.IS_VISUAL_USER = 'Y'
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

UNION ALL

SELECT
    'GROUP' AS RecordType,
    g.ID AS ID,
    pn.MENU_TEXT AS MenuString,
    pn.PROGRAM_ID,
    COALESCE(group_perm2.PERMISSION, 'Y') AS Permission
FROM GROUPS g
CROSS JOIN (SELECT DISTINCT PROGRAM_ID, MENU_TEXT FROM PROGRAM_NAME WHERE PROGRAM_ID = ?) pn
LEFT JOIN USER_PGM_AUTHORITY group_perm2 ON group_perm2.USER_ID = g.ID AND group_perm2.PROGRAM_ID = pn.PROGRAM_ID

ORDER BY RecordType, ID;
"""

SQL_SEARCH_MENUTEXT_USERS = SQL_SEARCH_PROGRAM_USERS.replace(
    "PROGRAM_ID = ?", "MENU_TEXT LIKE ?"
)


# ---------------------------------------------------------------------------
# Routes — Pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("dashboard-c.html")


# ---------------------------------------------------------------------------
# Routes — Overview
# ---------------------------------------------------------------------------

@app.route("/api/overview")
def api_overview():
    counts = run_query(SQL_KPI_COUNTS)[0]
    no_group = run_query(SQL_USERS_WITH_NO_GROUP)
    failed_logins = run_query(SQL_RECENT_FAILED_LOGINS)
    admins = run_query(SQL_ADMIN_USERS)
    return jsonify({
        "counts": counts,
        "usersWithNoGroupOrProfile": no_group,
        "failedLogins": failed_logins,
        "adminUsers": admins,
    })


# ---------------------------------------------------------------------------
# Routes — Users
# ---------------------------------------------------------------------------

@app.route("/api/users")
def api_users():
    detailed = request.args.get("detailed", "")
    if detailed:
        rows = run_query(SQL_ALL_USERS_BASIC)
        return jsonify(rows)
    rows = run_query("""
SELECT NAME
FROM APPLICATION_USER
WHERE IS_VISUAL_USER = 'Y'
ORDER BY NAME;
""")
    return jsonify([r["NAME"] for r in rows])


@app.route("/api/user/<user_id>/groups")
def api_user_groups(user_id):
    return jsonify(run_query(SQL_USER_GROUPS, (user_id,)))


@app.route("/api/user/<user_id>/profiles")
def api_user_profiles(user_id):
    return jsonify(run_query(SQL_USER_PROFILES, (user_id,)))


@app.route("/api/user/<user_id>/programs")
def api_user_programs(user_id):
    rows = run_query(SQL_USER_ALL_PROGRAMS, (user_id, user_id, user_id))
    return jsonify(add_permission_desc(rows))


@app.route("/api/user/<user_id>/fields")
def api_user_fields(user_id):
    rows = run_query(SQL_USER_FIELD_PERMS, (user_id,) * 6)
    return jsonify(add_permission_desc(rows))


# ---------------------------------------------------------------------------
# Routes — Groups
# ---------------------------------------------------------------------------

@app.route("/api/groups")
def api_groups():
    return jsonify(run_query(SQL_ALL_GROUPS))


@app.route("/api/group/<group_id>/members")
def api_group_members(group_id):
    return jsonify(run_query(SQL_GROUP_MEMBERS, (group_id,)))


@app.route("/api/group/<group_id>/programs")
def api_group_programs(group_id):
    rows = run_query(SQL_GROUP_PROGRAM_RULES, (group_id,))
    return jsonify(add_permission_desc(rows))


# ---------------------------------------------------------------------------
# Routes — Profiles
# ---------------------------------------------------------------------------

@app.route("/api/profiles")
def api_profiles():
    return jsonify(run_query(SQL_ALL_PROFILES))


@app.route("/api/profile/<profile_id>/members")
def api_profile_members(profile_id):
    return jsonify(run_query(SQL_PROFILE_MEMBERS, (profile_id,)))


@app.route("/api/profile/<profile_id>/programs")
def api_profile_programs(profile_id):
    rows = run_query(SQL_PROFILE_PROGRAM_RULES, (profile_id,))
    return jsonify(add_permission_desc(rows))


# ---------------------------------------------------------------------------
# Routes — Programs / Search
# ---------------------------------------------------------------------------

@app.route("/api/programs")
def api_programs():
    return jsonify(run_query(SQL_ALL_MENU_STRINGS))


@app.route("/api/search")
def api_search():
    program_id = request.args.get("program_id", "").strip()
    menu_text = request.args.get("menu_text", "").strip()
    access_filter = request.args.get("access", "").strip()

    if not program_id and not menu_text:
        return jsonify({"error": "Provide program_id or menu_text"}), 400

    if program_id:
        rows = run_query(SQL_SEARCH_PROGRAM_USERS, (program_id, program_id, program_id))
    else:
        like_term = f"%{menu_text}%"
        rows = run_query(SQL_SEARCH_MENUTEXT_USERS, (like_term, like_term, like_term))

    if access_filter:
        allowed = set(a.strip().upper() for a in access_filter.split(","))
        rows = [r for r in rows if r["Permission"] in allowed]

    return jsonify(add_permission_desc(rows))


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5055))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host=host, port=port, debug=debug)