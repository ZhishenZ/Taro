# Taro

## Database Setup

### 1. Create the Database

First, log in to your PostgreSQL instance from the EC2 server:

```sh
psql -h <your-host>.rds.amazonaws.com -U taro_master -d postgres -p 5432
```

Then create the database:

```sql
CREATE DATABASE tarodb;
```

You can verify the database was created with:

```sql
\l
```

You should see an entry like:

```sh
 tarodb    | taro_master | UTF8     | en_US.UTF-8 | en_US.UTF-8 | 
```

### 2. Configure Environment Variables

Create a `.env` file in the same directory as `create_db.py` with the following content (replace with your actual values):

```sh
DB_USER=taro_master
DB_PASSWORD=your_password
DB_HOST=your-host.rds.amazonaws.com
DB_PORT=5432
DB_NAME=tarodb
```

**Note:**  

- Do **not** commit `.env` to version control. Add `.env` to your `.gitignore`.

### 3. Create Database Tables

Install the following dependencies:

```sh
pip3 install sqlalchemy
pip3 install python-dotenv
pip3 install psycopg2-binary
```

Run the following command in the `src/taro/db/` directory:

```sh
python3 create_db.py
```

This script will:

- Load environment variables from `.env`
- Connect to your PostgreSQL database
- Create all tables defined in `models.py`
- Print a success or error message

If any required environment variable is missing, the script will raise an error and list the missing variables.

### 4. Verify Table Creation

Connect to your database:

```sh
psql -h <your-host>.rds.amazonaws.com -U taro_master -d tarodb -p 5432
```

List all tables:

```sql
\dt
```

You should see:

```sql
 public | daily_metrics | table owner | ...
 public | fundamentals  | table owner | ...
```

You can inspect table structure with:

```sql
\d daily_metrics
\d fundamentals
```

## Models

### DailyMetrics

Represents daily stock market metrics for a specific ticker.

**Table Name:** `daily_metrics`

**Columns:**

- `id` (Integer): Primary key
- `trade_date` (Date): Trading date, not nullable
- `ticker` (String[10]): Stock ticker symbol, not nullable

**Constraints:**

- Unique constraint on (`trade_date`, `ticker`) combination

### Fundamentals

Stores fundamental stock data linked to daily metrics.

**Table Name:** `fundamentals`

**Columns:**

- `id` (Integer): Primary key
- `daily_metrics_id` (Integer): Foreign key to DailyMetrics
- `open_price` (Numeric(10,2)): Opening price
- `high_price` (Numeric(10,2)): Highest price
- `close_price` (Numeric(10,2)): Closing price
- `low_price` (Numeric(10,2)): Lowest price
- `volume` (Numeric(10,2)): Trading volume

**Relationships:**

- One-to-one relationship with DailyMetrics through `daily_metrics_id`
- Enforced by unique constraint on `daily_metrics_id`

## Testing

The models include comprehensive test coverage:

### Model Tests (`test_models.py`)

- Table creation verification
- Column existence and properties validation
- Relationship integrity checks
- Data insertion and retrieval tests

### Database Tests (`test_postgress.py`)

- Connection reliability
- Version verification
- Basic query functionality
- Database configuration validation
