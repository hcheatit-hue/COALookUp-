# Order Details Query for Order ID 190150

This query retrieves comprehensive order details including header information and line items for order ID 190150.

## SQL Query

```sql
-- Order Details for Order ID 190150
-- Retrieves both header information and line items

-- Order Header Information
SELECT 
    co.ID AS Order_ID,
    co.CUSTOMER_ID,
    c.NAME AS Customer_Name,
    co.CUSTOMER_PO_REF,
    co.CONTACT_FIRST_NAME,
    co.CONTACT_LAST_NAME,
    co.CONTACT_PHONE,
    co.CONTACT_MOBILE,
    co.CONTACT_EMAIL,
    co.CONTACT_POSITION,
    co.ORDER_DATE,
    co.DESIRED_SHIP_DATE,
    co.PROMISE_DATE,
    co.LAST_SHIPPED_DATE,
    co.CREATE_DATE,
    co.STATUS_EFF_DATE,
    co.STATUS,
    co.TOTAL_AMT_ORDERED,
    co.TOTAL_AMT_SHIPPED,
    co.CURRENCY_ID,
    co.SELL_RATE,
    co.BUY_RATE,
    co.TERMS_DESCRIPTION,
    co.TERMS_NET_DAYS,
    co.TERMS_DISC_PERCENT,
    co.SALESREP_ID,
    co.TERRITORY,
    co.SHIP_VIA,
    co.FREE_ON_BOARD,
    co.FREIGHT_TERMS,
    co.BACK_ORDER,
    co.BACKORDER_FLAG,
    co.WAREHOUSE_ID,
    co.SITE_ID,
    co.USER_1,
    co.USER_2,
    co.USER_3,
    co.ENTERED_BY,
    c.ADDR_1,
    c.ADDR_2,
    c.CITY,
    c.COUNTRY,
    co.TYPE,
    co.ORDER_TYPE
FROM CUSTOMER_ORDER co
LEFT JOIN CUSTOMER c ON co.CUSTOMER_ID = c.ID
WHERE co.ID = '190150' OR co.ID = '`190150';

-- Order Line Items
SELECT 
    LINE_NO,
    PART_ID,
    CUSTOMER_PART_ID,
    LINE_STATUS,
    ORDER_QTY,
    TOTAL_SHIPPED_QTY,
    UNIT_PRICE,
    TOTAL_AMT_ORDERED,
    TOTAL_AMT_SHIPPED,
    DESIRED_SHIP_DATE,
    LAST_SHIPPED_DATE,
    PROMISE_DATE,
    PRODUCT_CODE,
    MISC_REFERENCE,
    TRADE_DISC_PERCENT,
    COMMISSION_PCT,
    WAREHOUSE_ID,
    TYPE
FROM CUST_ORDER_LINE
WHERE CUST_ORDER_ID = '190150' OR CUST_ORDER_ID = '`190150'
ORDER BY LINE_NO;

-- Order Completion Status
SELECT 
    '190150' AS OrderID,
    CASE WHEN EXISTS (
        SELECT 1 FROM CUST_ORDER_LINE col 
        WHERE (col.CUST_ORDER_ID = '190150' OR col.CUST_ORDER_ID = '`190150')
        AND col.ORDER_QTY > ISNULL(col.TOTAL_SHIPPED_QTY, 0)
    ) THEN 'Incomplete' ELSE 'Complete' END AS Completion_Status,
    (SELECT COUNT(*) FROM CUST_ORDER_LINE 
     WHERE (CUST_ORDER_ID = '190150' OR CUST_ORDER_ID = '`190150')) AS Total_Lines,
    (SELECT COUNT(*) FROM CUST_ORDER_LINE 
     WHERE (CUST_ORDER_ID = '190150' OR CUST_ORDER_ID = '`190150')
     AND ORDER_QTY <= ISNULL(TOTAL_SHIPPED_QTY, 0)) AS Completed_Lines;
```

## Alternative: Using Stored Procedures

You can also use the existing stored procedures to get the same information:

```sql
-- Get order header details
EXEC sp_GetOrderDetailHeader '190150';

-- Get order line items
EXEC sp_GetOrderDetailLines '190150';

-- Check order completion status
EXEC sp_CheckOrderCompletion '190150';
```

## Notes

- The query handles both regular order IDs and those with backtick prefix (`190150)
- Order header includes customer information, dates, status, and financial details
- Line items show individual product details, quantities, and pricing
- Completion status check shows whether the order is fully shipped
- Currency information and rates are included for international orders
