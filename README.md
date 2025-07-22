# Taro

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

### Model Tests (`test_models.py`):
- Table creation verification
- Column existence and properties validation
- Relationship integrity checks
- Data insertion and retrieval tests

### Database Tests (`test_postgress.py`):
- Connection reliability
- Version verification
- Basic query functionality
- Database configuration validation