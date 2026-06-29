# COA Order Lookup

A Flask-based web application for querying customer orders from an SSSHCHEAT SQL Server database.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your database credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_SERVER=HCHDB01\SSINFOR
DB_DATABASE=SSHCHEAT
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED_CONNECTION=yes
```

### 3. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5055`

## Troubleshooting

### Database Connection Issues

Visit the health check endpoint to diagnose database connectivity:
```
GET http://localhost:5055/api/health
```

This will tell you if the database connection is working and show which server/database it's trying to reach.

### Common Errors

**Error: `Login failed for user`**
- Verify SQL Server server name in `.env`
- Ensure your Windows user has permissions on the database
- Check that the database exists and you can connect via SQL Server Management Studio

**Error: `Cannot open database`**
- Verify the database name (`SSHCHEAT`) exists
- Check database availability on the server

## API Endpoints

- `GET /` — Main UI
- `GET /api/health` — Database health check
- `GET /api/customer/search?q=<query>` — Search customers by name or ID
- `GET /api/customer/<id>/orders` — Get all orders for a customer
- `GET /api/order/<id>` — Get detailed order information (header + line items)

## Logging

Logs are output to the console by default. Check console for diagnostic information during development.
