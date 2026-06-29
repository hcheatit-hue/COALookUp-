from flask import Flask, render_template, request, jsonify
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
    )
    return pyodbc.connect(conn_str)

@app.route('/order-search')
def order_search():
    return render_template('order_search.html')

@app.route('/api/order-search')
def api_order_search():
    customer_name = request.args.get('customer_name', '').strip()
    order_id      = request.args.get('order_id', '').strip()

    if not customer_name and not order_id:
        return jsonify({'error': 'Provide at least a customer name or order ID.'}), 400

    query = """
        SELECT
            co.ID                                                        AS Order_ID,
            c.NAME                                                       AS Customer_Name,
            co.CUSTOMER_PO_REF                                           AS COA_Number,
            co.ORDER_DATE,
            co.STATUS,
            col.LINE_NO,
            col.PART_ID,
            p.DESCRIPTION                                                AS Part_Description,
            col.ORDER_QTY,
            col.TOTAL_SHIPPED_QTY,
            col.ORDER_QTY - ISNULL(col.TOTAL_SHIPPED_QTY, 0)            AS Outstanding_QTY,
            col.UNIT_PRICE,
            col.TRADE_DISC_PERCENT,
            col.UNIT_PRICE * (1 - ISNULL(col.TRADE_DISC_PERCENT, 0) / 100)
                                                                         AS Net_Unit_Price,
            col.TOTAL_AMT_ORDERED                                        AS Line_Total,
            col.LINE_STATUS,
            SUM(col.TOTAL_AMT_ORDERED) OVER (PARTITION BY co.ID)        AS Order_Grand_Total,
            SUM(col.TOTAL_AMT_SHIPPED) OVER (PARTITION BY co.ID)        AS Order_Total_Shipped
        FROM CUSTOMER_ORDER co
        JOIN CUSTOMER c           ON co.CUSTOMER_ID = c.ID
        JOIN CUST_ORDER_LINE col  ON col.CUST_ORDER_ID = co.ID
        LEFT JOIN PART p          ON col.PART_ID = p.ID
        WHERE
            (? = '' OR c.NAME LIKE '%' + ? + '%')
        AND (? = '' OR co.ID  LIKE '%' + ? + '%')
        ORDER BY co.ORDER_DATE ASC, co.ID, col.LINE_NO
    """

    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, customer_name, customer_name, order_id, order_id)
        columns = [col[0] for col in cursor.description]
        rows    = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        # Format dates and decimals for JSON
        for row in rows:
            for key, val in row.items():
                if hasattr(val, 'strftime'):
                    row[key] = val.strftime('%Y-%m-%d') if val else None
                elif hasattr(val, '__float__'):
                    row[key] = float(val) if val is not None else None

        return jsonify({'results': rows, 'count': len(rows)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5010)