from flask import Flask, jsonify, request, render_template
import pyodbc
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Flask Configuration ---
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5055))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# --- DB Configuration ---
DB_SERVER = os.getenv('DB_SERVER', 'HCHDB01\\SSINFOR')
DB_NAME = os.getenv('DB_NAME', 'SSHCHEAT')
DB_DRIVER = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_ENCRYPT = os.getenv('DB_ENCRYPT', 'yes')
DB_TRUST_CERT = os.getenv('DB_TRUST_CERT', 'yes')

def get_conn():
    """Get database connection with error handling."""
    try:
        # Build connection string based on available credentials
        if DB_USER and DB_PASSWORD:
            # SQL Server authentication
            conn_string = (
                f"DRIVER={DB_DRIVER};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_NAME};"
                f"UID={DB_USER};"
                f"PWD={DB_PASSWORD};"
                f"Encrypt={DB_ENCRYPT};"
                f"TrustServerCertificate={DB_TRUST_CERT};"
            )
            logger.debug(f"Using SQL Server authentication for {DB_USER}@{DB_SERVER}")
        else:
            # Windows integrated authentication
            conn_string = (
                f"DRIVER={DB_DRIVER};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_NAME};"
                f"Trusted_Connection=yes;"
                f"Encrypt={DB_ENCRYPT};"
                f"TrustServerCertificate={DB_TRUST_CERT};"
            )
            logger.debug(f"Using Windows integrated authentication for {DB_SERVER}")
        
        conn = pyodbc.connect(conn_string, autocommit=True)
        logger.info(f"Database connection successful to {DB_SERVER}/{DB_NAME}")
        return conn
    except pyodbc.DatabaseError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected connection error: {str(e)}")
        raise

# --- Status code mapping ---
STATUS_MAP = {
    'O': {'label': 'Open',       'color': 'status-open'},
    'B': {'label': 'Backordered','color': 'status-backorder'},
    'X': {'label': 'Closed',     'color': 'status-closed'},
    'C': {'label': 'Cancelled',  'color': 'status-cancelled'},
    'P': {'label': 'Picked',     'color': 'status-picked'},
    'S': {'label': 'Shipped',    'color': 'status-shipped'},
    'I': {'label': 'Invoiced',   'color': 'status-invoiced'},
    'H': {'label': 'On Hold',    'color': 'status-hold'},
    'Q': {'label': 'Quote',      'color': 'status-quote'},
}

LINE_STATUS_MAP = {
    'O': {'label': 'Open',      'color': 'status-open'},
    'X': {'label': 'Closed',    'color': 'status-closed'},
    'C': {'label': 'Cancelled', 'color': 'status-cancelled'},
    'S': {'label': 'Shipped',   'color': 'status-shipped'},
    'B': {'label': 'Backordered','color': 'status-backorder'},
    'A': {'label': 'Active',    'color': 'status-open'},
    'H': {'label': 'On Hold',   'color': 'status-hold'},
}

def fmt_date(val):
    if val is None:
        return None
    try:
        return val.strftime('%d %b %Y')
    except:
        return str(val)

def fmt_currency(val, currency='SAR'):
    if val is None:
        return None
    symbol = 'R' if currency in ('SAR', 'ZAR') else currency + ' '
    return f"{symbol}{float(val):,.2f}"

def row_to_dict(row, cursor):
    cols = [col[0] for col in cursor.description]
    return dict(zip(cols, row))


# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health')
def health():
    """Health check endpoint - verifies database connectivity."""
    try:
        conn = get_conn()
        conn.close()
        auth_method = 'SQL Server' if DB_USER else 'Windows Integrated'
        return jsonify({
            'status': 'healthy',
            'database': DB_NAME,
            'server': DB_SERVER,
            'auth': auth_method,
            'port': FLASK_PORT
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        auth_method = 'SQL Server' if DB_USER else 'Windows Integrated'
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'database': DB_NAME,
            'server': DB_SERVER,
            'auth': auth_method,
            'port': FLASK_PORT
        }), 503


@app.route('/api/customer/search')
def customer_search():
    try:
        q = request.args.get('q', '').strip()
        if len(q) < 2:
            return jsonify([])
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP 15
                ID,
                NAME,
                CITY,
                SALESREP_ID,
                CURRENCY_ID,
                ACTIVE_FLAG,
                LAST_ORDER_DATE
            FROM CUSTOMER
            WHERE NAME LIKE ? OR ID LIKE ?
            ORDER BY NAME
        """, (f'%{q}%', f'%{q}%'))
        rows = cur.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            results.append({
                'id': r[0],
                'name': r[1],
                'city': r[2],
                'salesrep': r[3],
                'currency': r[4],
                'active': r[5],
                'last_order_date': fmt_date(r[6]),
            })
        return jsonify(results)
    except pyodbc.DatabaseError as e:
        logger.error(f"Database error in customer_search: {str(e)}")
        return jsonify({'error': 'Database connection failed'}), 503
    except Exception as e:
        logger.error(f"Error in customer_search: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/api/customer/<customer_id>/orders')
def customer_orders(customer_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                co.ID,
                co.CUSTOMER_PO_REF,
                co.ORDER_DATE,
                co.DESIRED_SHIP_DATE,
                co.PROMISE_DATE,
                co.LAST_SHIPPED_DATE,
                co.STATUS,
                co.TOTAL_AMT_ORDERED,
                co.TOTAL_AMT_SHIPPED,
                co.CURRENCY_ID,
                co.SALESREP_ID,
                co.TERRITORY,
                co.USER_1
            FROM CUSTOMER_ORDER co
            WHERE co.CUSTOMER_ID = ?
            ORDER BY co.ORDER_DATE DESC
        """, (customer_id,))
        rows = cur.fetchall()
        conn.close()
        
        orders = []
        for r in rows:
            status_code = (r[6] or '').strip()
            status_info = STATUS_MAP.get(status_code, {'label': status_code or 'Unknown', 'color': 'status-unknown'})
            currency = r[9] or 'SAR'
            orders.append({
                'id': (r[0] or '').strip().lstrip('`'),
                'customer_po_ref': r[1],
                'order_date': fmt_date(r[2]),
                'desired_ship_date': fmt_date(r[3]),
                'promise_date': fmt_date(r[4]),
                'last_shipped_date': fmt_date(r[5]),
                'status_code': status_code,
                'status_label': status_info['label'],
                'status_color': status_info['color'],
                'total_ordered': fmt_currency(r[7], currency),
                'total_shipped': fmt_currency(r[8], currency),
                'total_ordered_raw': float(r[7] or 0),
                'total_shipped_raw': float(r[8] or 0),
                'currency': currency,
                'salesrep': r[10],
                'territory': r[11],
                'site': r[12],
            })
        return jsonify(orders)
    except pyodbc.DatabaseError as e:
        logger.error(f"Database error in customer_orders: {str(e)}")
        return jsonify({'error': 'Database connection failed'}), 503
    except Exception as e:
        logger.error(f"Error in customer_orders: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/api/order/<order_id>')
def order_detail(order_id):
    try:
        conn = get_conn()
        cur = conn.cursor()

        # --- Header ---
        cur.execute("""
            SELECT
                co.ID, co.CUSTOMER_ID, co.CUSTOMER_PO_REF,
                co.CONTACT_FIRST_NAME, co.CONTACT_LAST_NAME,
                co.CONTACT_PHONE, co.CONTACT_MOBILE, co.CONTACT_EMAIL,
                co.CONTACT_POSITION,
                co.ORDER_DATE, co.DESIRED_SHIP_DATE, co.PROMISE_DATE,
                co.LAST_SHIPPED_DATE, co.CREATE_DATE, co.STATUS_EFF_DATE,
                co.STATUS,
                co.TOTAL_AMT_ORDERED, co.TOTAL_AMT_SHIPPED,
                co.CURRENCY_ID, co.SELL_RATE, co.BUY_RATE,
                co.TERMS_DESCRIPTION, co.TERMS_NET_DAYS, co.TERMS_DISC_PERCENT,
                co.SALESREP_ID, co.TERRITORY,
                co.SHIP_VIA, co.FREE_ON_BOARD, co.FREIGHT_TERMS,
                co.BACK_ORDER, co.BACKORDER_FLAG,
                co.WAREHOUSE_ID, co.SITE_ID,
                co.USER_1, co.USER_2, co.USER_3,
                co.ENTERED_BY,
                c.NAME AS CUSTOMER_NAME,
                c.ADDR_1, c.ADDR_2, c.CITY, c.COUNTRY,
                co.TYPE, co.ORDER_TYPE
            FROM CUSTOMER_ORDER co
            LEFT JOIN CUSTOMER c ON co.CUSTOMER_ID = c.ID
            WHERE co.ID = ? OR co.ID = ?
        """, (order_id, f'`{order_id}'))

        row = cur.fetchone()
        if not row:
            conn.close()
            logger.warning(f"Order not found: {order_id}")
            return jsonify({'error': 'Order not found'}), 404

        status_code = (row[15] or '').strip()
        status_info = STATUS_MAP.get(status_code, {'label': status_code or 'Unknown', 'color': 'status-unknown'})
        currency = row[18] or 'SAR'
        total_ordered = float(row[16] or 0)
        total_shipped = float(row[17] or 0)
        shipped_pct = round((total_shipped / total_ordered * 100) if total_ordered > 0 else 0, 1)

        header = {
            'id': (row[0] or '').strip().lstrip('`'),
            'customer_id': row[1],
            'customer_name': row[37],
            'customer_po_ref': row[2],
            'contact': {
                'name': f"{row[3] or ''} {row[4] or ''}".strip(),
                'position': row[8],
                'phone': row[5],
                'mobile': row[6],
                'email': row[7],
            },
            'dates': {
                'order': fmt_date(row[9]),
                'desired_ship': fmt_date(row[10]),
                'promise': fmt_date(row[11]),
                'last_shipped': fmt_date(row[12]),
                'created': fmt_date(row[13]),
                'status_eff': fmt_date(row[14]),
            },
            'status_code': status_code,
            'status_label': status_info['label'],
            'status_color': status_info['color'],
            'financials': {
                'total_ordered': fmt_currency(total_ordered, currency),
                'total_shipped': fmt_currency(total_shipped, currency),
                'total_ordered_raw': total_ordered,
                'total_shipped_raw': total_shipped,
                'shipped_pct': shipped_pct,
                'currency': currency,
                'sell_rate': row[19],
                'buy_rate': row[20],
            },
            'terms': {
                'description': row[21],
                'net_days': row[22],
                'disc_percent': row[23],
            },
            'sales': {
                'rep': row[24],
                'territory': row[25],
            },
            'shipping': {
                'ship_via': row[26],
                'fob': row[27],
                'freight_terms': row[28],
                'backorder': row[29],
                'warehouse': row[31],
                'site': row[32],
            },
            'address': {
                'addr_1': row[38],
                'addr_2': row[39],
                'city': row[40],
                'country': row[41],
            },
            'user_fields': {
                'user_1': row[33],
                'user_2': row[34],
                'user_3': row[35],
            },
            'entered_by': row[36],
            'type': row[42],
            'order_type': row[43],
        }

        # --- Line Items ---
        cur.execute("""
            SELECT
                LINE_NO, PART_ID, CUSTOMER_PART_ID,
                LINE_STATUS, ORDER_QTY, TOTAL_SHIPPED_QTY,
                UNIT_PRICE, TOTAL_AMT_ORDERED, TOTAL_AMT_SHIPPED,
                DESIRED_SHIP_DATE, LAST_SHIPPED_DATE, PROMISE_DATE,
                PRODUCT_CODE, MISC_REFERENCE,
                TRADE_DISC_PERCENT, COMMISSION_PCT,
                WAREHOUSE_ID, TYPE
            FROM CUST_ORDER_LINE
            WHERE CUST_ORDER_ID = ? OR CUST_ORDER_ID = ?
            ORDER BY LINE_NO
        """, (order_id, f'`{order_id}'))

        line_rows = cur.fetchall()
        conn.close()

        lines = []
        for lr in line_rows:
            ls_code = (lr[3] or '').strip()
            ls_info = LINE_STATUS_MAP.get(ls_code, {'label': ls_code or '—', 'color': 'status-unknown'})
            lines.append({
                'line_no': lr[0],
                'part_id': lr[1],
                'customer_part_id': lr[2],
                'status_code': ls_code,
                'status_label': ls_info['label'],
                'status_color': ls_info['color'],
                'order_qty': float(lr[4] or 0),
                'shipped_qty': float(lr[5] or 0),
                'unit_price': fmt_currency(lr[6], currency),
                'total_ordered': fmt_currency(lr[7], currency),
                'total_shipped': fmt_currency(lr[8], currency),
                'desired_ship_date': fmt_date(lr[9]),
                'last_shipped_date': fmt_date(lr[10]),
                'promise_date': fmt_date(lr[11]),
                'product_code': lr[12],
                'description': lr[13],
                'disc_pct': lr[14],
                'commission_pct': lr[15],
                'warehouse': lr[16],
                'type': lr[17],
            })

        logger.info(f"Order detail loaded: {order_id}")
        return jsonify({'header': header, 'lines': lines})
    
    except pyodbc.DatabaseError as e:
        logger.error(f"Database error in order_detail: {str(e)}")
        return jsonify({'error': 'Database connection failed'}), 503
    except Exception as e:
        logger.error(f"Error in order_detail: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    logger.info(f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)