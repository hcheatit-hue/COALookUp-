# COA Order Lookup API Documentation

**Base URL**: `http://localhost:5055`

## Overview
This API provides endpoints for searching customers, retrieving order details, and managing payment information for the HC Heat Exchangers COA Order Lookup system.

---

## Endpoints

### 1. Health Check
**GET** `/api/health`

Checks database connectivity and server status.

**Response**:
```json
{
  "status": "healthy|unhealthy",
  "database": "SSHCHEAT",
  "server": "HCHDB01\\SSINFOR",
  "auth": "SQL Server|Windows Integrated",
  "port": 5055,
  "error": "Error message (if unhealthy)"
}
```

**Status Codes**:
- `200` - Healthy
- `503` - Database connection failed

---

### 2. Customer Search
**GET** `/api/customer/search`

Search for customers by name or ID.

**Query Parameters**:
- `q` (required) - Search query (minimum 2 characters)

**Example Request**:
```
GET /api/customer/search?q=Heat
```

**Response**:
```json
[
  {
    "id": "CUST001",
    "name": "Heat Exchanger Company",
    "city": "Johannesburg",
    "salesrep": "REP001",
    "currency": "ZAR",
    "active": true,
    "last_order_date": "15 Apr 2026"
  }
]
```

**Status Codes**:
- `200` - Success
- `503` - Database connection failed
- `500` - Unexpected error

---

### 3. Customer Orders
**GET** `/api/customer/<customer_id>/orders`

Retrieve all orders for a specific customer.

**Path Parameters**:
- `customer_id` (required) - Customer ID

**Query Parameters** (all optional):
- `status` - Comma-separated status codes (O, X, C, B, P, S, I, H, Q)
- `order_date_from` - Order date start (YYYY-MM-DD)
- `order_date_to` - Order date end (YYYY-MM-DD)
- `desired_ship_date_from` - Desired ship date start (YYYY-MM-DD)
- `desired_ship_date_to` - Desired ship date end (YYYY-MM-DD)
- `salesrep` - Sales representative ID
- `territory` - Territory (partial match)
- `currency` - Currency code
- `total_ordered_min` - Minimum order amount (float)
- `total_ordered_max` - Maximum order amount (float)
- `order_type` - Order type
- `backorder` - Backorder flag (Y/N)
- `limit` - Results limit (default: 50)
- `offset` - Results offset (default: 0)

**Example Request**:
```
GET /api/customer/CUST001/orders?status=O,S&limit=10&offset=0
```

**Response**:
```json
[
  {
    "id": "223322",
    "customer_po_ref": "PO-2026-001",
    "order_date": "10 Apr 2026",
    "desired_ship_date": "20 Apr 2026",
    "promise_date": "18 Apr 2026",
    "last_shipped_date": "15 Apr 2026",
    "status_code": "COMPLETE",
    "status_label": "Complete",
    "status_color": "status-complete",
    "total_ordered": "R 15,000.00",
    "total_shipped": "R 15,000.00",
    "total_ordered_raw": 15000.0,
    "total_shipped_raw": 15000.0,
    "currency": "ZAR",
    "salesrep": "REP001",
    "territory": "GAUTENG",
    "site": "MAIN"
  }
]
```

**Status Codes**:
- `200` - Success
- `503` - Database connection failed
- `500` - Unexpected error

---

### 4. Order Details
**GET** `/api/order/<order_id>`

Retrieve detailed information for a specific order including line items.

**Path Parameters**:
- `order_id` (required) - Order ID

**Query Parameters** (all optional):
- `part_id` - Filter by part ID (partial match)
- `line_status` - Comma-separated line status codes (O, X, C, S, B, A, H)
- `limit` - Line items limit (default: 50)
- `offset` - Line items offset (default: 0)

**Example Request**:
```
GET /api/order/223322?limit=100
```

**Response**:
```json
{
  "header": {
    "id": "223322",
    "customer_id": "CUST001",
    "customer_name": "Heat Exchanger Company",
    "customer_po_ref": "PO-2026-001",
    "contact": {
      "name": "John Doe",
      "position": "Purchasing Manager",
      "phone": "+27 11 123 4567",
      "mobile": "+27 82 123 4567",
      "email": "john@heatexchanger.com"
    },
    "dates": {
      "order": "10 Apr 2026",
      "desired_ship": "20 Apr 2026",
      "promise": "18 Apr 2026",
      "last_shipped": "15 Apr 2026",
      "created": "10 Apr 2026",
      "status_eff": "10 Apr 2026"
    },
    "status_code": "COMPLETE",
    "status_label": "Complete",
    "status_color": "status-complete",
    "financials": {
      "total_ordered": "R 15,000.00",
      "total_shipped": "R 15,000.00",
      "total_ordered_raw": 15000.0,
      "total_shipped_raw": 15000.0,
      "shipped_pct": 100.0,
      "currency": "ZAR",
      "sell_rate": 19.5,
      "buy_rate": 19.2
    },
    "terms": {
      "description": "NET 30",
      "net_days": 30,
      "disc_percent": 0.0
    },
    "sales": {
      "rep": "REP001",
      "territory": "GAUTENG"
    },
    "shipping": {
      "ship_via": "COURIER",
      "fob": "JOHANNESBURG",
      "freight_terms": "PREPAID",
      "backorder": "N",
      "warehouse": "WH01",
      "site": "MAIN"
    },
    "address": {
      "addr_1": "123 Industrial Road",
      "addr_2": "Unit 5",
      "city": "Johannesburg",
      "country": "South Africa"
    },
    "user_fields": {
      "user_1": "Project Site",
      "user_2": "",
      "user_3": ""
    },
    "entered_by": "ADMIN",
    "type": "SO",
    "order_type": "STANDARD"
  },
  "lines": [
    {
      "line_no": 1,
      "part_id": "HE001",
      "customer_part_id": "CUST-HE001",
      "status_code": "S",
      "status_label": "Shipped",
      "status_color": "status-shipped",
      "order_qty": 10.0,
      "shipped_qty": 10.0,
      "unit_price": "R 1,500.00",
      "total_ordered": "R 15,000.00",
      "total_shipped": "R 15,000.00",
      "desired_ship_date": "20 Apr 2026",
      "last_shipped_date": "15 Apr 2026",
      "promise_date": "18 Apr 2026",
      "product_code": "HEAT-EX",
      "description": "Heat Exchanger Unit - Model X",
      "disc_pct": 0.0,
      "commission_pct": 5.0,
      "warehouse": "WH01",
      "type": "ITEM"
    }
  ]
}
```

**Status Codes**:
- `200` - Success
- `404` - Order not found
- `503` - Database connection failed
- `500` - Unexpected error

---

### 5. Orders Search
**GET** `/api/orders/search`

Search for orders by customer PO reference or customer name.

**Query Parameters**:
- `q` (required) - Search query (minimum 2 characters)
- `status` - Comma-separated status codes
- `order_date_from` - Order date start (YYYY-MM-DD)
- `order_date_to` - Order date end (YYYY-MM-DD)
- `salesrep` - Sales representative ID
- `territory` - Territory (partial match)
- `currency` - Currency code
- `total_ordered_min` - Minimum order amount (float)
- `total_ordered_max` - Maximum order amount (float)
- `order_type` - Order type
- `backorder` - Backorder flag (Y/N)
- `limit` - Results limit (default: 50)
- `offset` - Results offset (default: 0)

**Example Request**:
```
GET /api/orders/search?q=PO-2026&status=COMPLETE
```

**Response**:
```json
[
  {
    "id": "223322",
    "customer_id": "CUST001",
    "customer_name": "Heat Exchanger Company",
    "customer_po_ref": "PO-2026-001",
    "order_date": "10 Apr 2026",
    "desired_ship_date": "20 Apr 2026",
    "promise_date": "18 Apr 2026",
    "last_shipped_date": "15 Apr 2026",
    "status_code": "COMPLETE",
    "status_label": "Complete",
    "status_color": "status-complete",
    "total_ordered": "R 15,000.00",
    "total_shipped": "R 15,000.00",
    "total_ordered_raw": 15000.0,
    "total_shipped_raw": 15000.0,
    "currency": "ZAR",
    "salesrep": "REP001",
    "territory": "GAUTENG",
    "site": "MAIN"
  }
]
```

**Status Codes**:
- `200` - Success
- `503` - Database connection failed
- `500` - Unexpected error

---

### 6. Sales Representatives
**GET** `/api/salesreps`

Retrieve list of sales representatives and territories.

**Response**:
```json
{
  "salesreps": [
    {
      "id": "REP001",
      "label": "REP001"
    },
    {
      "id": "REP002",
      "label": "REP002"
    }
  ],
  "territories": [
    "GAUTENG",
    "WESTERN CAPE",
    "KWAZULU-NATAL"
  ]
}
```

**Status Codes**:
- `200` - Success
- `503` - Database connection failed
- `500` - Unexpected error

---

### 7. Outstanding Payments
**GET** `/api/outstanding-payments`

Retrieve orders with outstanding payment amounts.

**Query Parameters** (all optional):
- `date_from` - Order date start (YYYY-MM-DD)
- `date_to` - Order date end (YYYY-MM-DD)
- `limit` - Results limit (default: 50)
- `offset` - Results offset (default: 0)

**Example Request**:
```
GET /api/outstanding-payments?date_from=2026-01-01&date_to=2026-12-31
```

**Response**:
```json
[
  {
    "id": "223323",
    "customer_po_ref": "PO-2026-002",
    "contact_first_name": "Jane",
    "ship_via": "COURIER",
    "salesrep_id": "REP001",
    "freight_terms": "PREPAID",
    "terms_description": "NET 30",
    "status": "O",
    "total_ordered": "R 8,500.00",
    "total_shipped": "R 8,500.00",
    "amt_outstanding": "R 8,500.00",
    "order_date": "12 Apr 2026",
    "currency_id": "ZAR",
    "customer_name": "Another Company"
  }
]
```

**Status Codes**:
- `200` - Success
- `503` - Database connection failed
- `500` - Unexpected error

---

## Status Codes Reference

### Order Status Codes
- `O` - Open
- `B` - Backordered
- `X` - Closed
- `C` - Cancelled
- `P` - Picked
- `S` - Shipped
- `I` - Invoiced
- `H` - On Hold
- `Q` - Quote
- `COMPLETE` - Complete (100% fulfilled)

### Line Status Codes
- `O` - Open
- `X` - Closed
- `C` - Cancelled
- `S` - Shipped
- `B` - Backordered
- `A` - Active
- `H` - On Hold

---

## Error Response Format

All endpoints return errors in the following format:

```json
{
  "error": "Error description"
}
```

Common error status codes:
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (order/customer not found)
- `500` - Internal Server Error
- `503` - Service Unavailable (database connection failed)

---

## Postman Collection Setup

1. **Environment Variables**:
   - `baseUrl`: `http://localhost:5055`

2. **Headers** (no authentication required):
   - `Content-Type`: `application/json`

3. **Example Collection Structure**:
   ```
   COA Order Lookup API
   |-- Health Check
   |-- Customer Search
   |-- Customer Orders
   |-- Order Details
   |-- Orders Search
   |-- Sales Representatives
   |-- Outstanding Payments
   ```

4. **Test Examples**:
   - Test customer search with query "Heat"
   - Test order details for order "223322"
   - Test outstanding payments with date range
   - Test customer orders with status filters

---

## Notes

- All dates are returned in `DD MMM YYYY` format
- All monetary values are formatted with currency symbol and thousands separator
- The API automatically calculates order completion status (100% shipped = Complete)
- Pagination is supported on list endpoints using `limit` and `offset` parameters
- No authentication is required for this API
- Server runs on port 5055 by default
