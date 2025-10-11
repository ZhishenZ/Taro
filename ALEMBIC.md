# Taro

A modern stock analysis platform with automated PostgreSQL database schema management.

## 🚀 **Quick Start**

This project uses **dev containers** for consistent development environments and **Alembic** for automated database schema management.

### **1. Open in Dev Container**

1. **Clone the repository**
2. **Open in VS Code**
3. **Rebuild in Container** (when prompted)
4. **Database schema automatically initialized!** ✅

### **2. Verify Setup**

Run the comprehensive tests to verify everything is working:

```bash
# Test database schema and migrations
python -m pytest tests/test_essentials.py -v

# Check migration status
alembic current
alembic history
```

## 📊 **Database Schema Management**

This project uses **Alembic** for automated database schema versioning and migrations.

### **🔄 Automatic Schema Management**

The dev container automatically:

1. **Installs all dependencies** from `pyproject.toml`
2. **Detects schema changes** with `alembic check`
3. **Creates migrations** if models are updated
4. **Applies migrations** to keep database in sync

### **📋 Manual Migration Commands**

For manual schema management:

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Check for pending schema changes
alembic check

# Create new migration (auto-generate from model changes)
alembic revision --autogenerate -m "describe_your_changes"

# Apply pending migrations
alembic upgrade head

# Rollback to previous migration
alembic downgrade -1
```

### **🏗️ Making Schema Changes**

1. **Edit models** in `src/taro/db/models.py`
2. **Create migration**:

   ```bash
   alembic revision --autogenerate -m "add_new_column"
   ```

3. **Review generated migration** in `src/taro/migrations/versions/`
4. **Apply migration**:

   ```bash
   alembic upgrade head
   ```

5. **Test changes**:

   ```bash
   python -m pytest tests/test_essentials.py::TestDatabase::test_table_structure -v
   ```

### **🧪 Schema Testing**

Comprehensive test suite validates:

```bash
# Test all database functionality
python -m pytest tests/test_essentials.py -v

# Test specific areas
python -m pytest tests/test_essentials.py::TestDatabase::test_schema_exists -v
python -m pytest tests/test_essentials.py::TestDatabase::test_tables_exist -v
python -m pytest tests/test_essentials.py::TestDatabase::test_models_match_database -v
python -m pytest tests/test_essentials.py::TestMigrations -v
```

### **⚙️ Configuration**

Database connection configured via environment variables in `.env`:

```bash
# PostgreSQL Configuration (Docker Compose)
DATABASE_URL=postgresql://taro_user:taro_password@postgres:5432/taro_stock

# Alternative individual components
DB_HOST=postgres
DB_PORT=5432
DB_NAME=taro_stock
DB_USER=taro_user
DB_PASSWORD=taro_password
```

### **🐳 Docker Integration**

- **PostgreSQL 15** automatically available via Docker Compose
- **Public schema** used for application tables
- **Dev container** handles all setup
- **Persistent volumes** maintain data between rebuilds

## 📊 **Database Models**

The database uses the **public schema** (default PostgreSQL schema) with the following tables:

> **Note**: This project uses the default PostgreSQL schema (`public`) for simplicity. This provides easier development, deployment, and maintenance without the complexity of custom schemas.

### **DailyMetrics**

Represents daily stock market metrics for a specific ticker.

**Table:** `daily_metrics`

**Columns:**

- `id` (Integer): Primary key, auto-increment
- `trade_date` (Date): Trading date, not nullable
- `ticker` (String[10]): Stock ticker symbol, not nullable

**Constraints:**

- Unique constraint on (`trade_date`, `ticker`) combination
- Primary key index on `id` (implicit)

### **Fundamentals**

Stores fundamental stock data linked to daily metrics.

**Table:** `fundamentals`

**Columns:**

- `id` (Integer): Primary key, auto-increment
- `daily_metrics_id` (Integer): Foreign key to DailyMetrics, not nullable
- `open_price` (Numeric(10,2)): Opening price
- `high_price` (Numeric(10,2)): Highest price
- `close_price` (Numeric(10,2)): Closing price
- `low_price` (Numeric(10,2)): Lowest price
- `volume` (Numeric(10,2)): Trading volume

**Relationships:**

- One-to-one relationship with DailyMetrics via `daily_metrics_id`
- Foreign key constraint ensures referential integrity
- Unique constraint on `daily_metrics_id` enforces one-to-one relationship

### **Schema Evolution**

All schema changes are managed through Alembic migrations:

```bash
# View current models
python -c "
from taro.db.models import Base
for table in Base.metadata.tables.values():
    print(f'{table.name}: {[col.name for col in table.columns]}')
    print(f'  Schema: {table.schema or \"public (default)\"}')
"

# Compare models vs database
alembic check
```

## 🧪 **Testing**

Comprehensive test suite validates all database functionality and schema management.

### **Database Tests**

**File:** `tests/test_essentials.py`

**TestDatabase Class:**

- ✅ `test_connection` - Database connectivity
- ✅ `test_models_import` - SQLAlchemy model imports
- ✅ `test_schema_exists` - Public schema validation
- ✅ `test_tables_exist` - Required tables present
- ✅ `test_table_structure` - Column structure validation
- ✅ `test_models_match_database` - Model-database synchronization
- ✅ `test_database_crud_operations` - Insert, Select, Update, Delete operations

**TestMigrations Class:**

- ✅ `test_alembic_current_version` - Migration version tracking
- ✅ `test_alembic_check_no_pending` - Schema synchronization
- ✅ `test_alembic_history` - Migration history
- ✅ `test_migration_files_exist` - Migration file presence
- ✅ `test_alembic_version_table` - Version tracking table

### **Running Tests**

```bash
# Run all database tests
python -m pytest tests/test_essentials.py -v

# Run specific test categories
python -m pytest tests/test_essentials.py::TestDatabase -v
python -m pytest tests/test_essentials.py::TestMigrations -v

# Run specific tests
python -m pytest tests/test_essentials.py::TestDatabase::test_database_crud_operations -v

# Test with coverage (if pytest-cov installed)
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### **Test Environment**

Tests automatically use the containerized PostgreSQL database:

- **Database**: `taro_stock`
- **Schema**: `public` (default)
- **User**: `taro_user`
- **Host**: `postgres` (Docker service)
- **Port**: `5432`

### **Continuous Testing**

The test suite validates:

1. **Schema Integrity** - Tables match models exactly
2. **Migration Tracking** - Alembic version management working
3. **CRUD Operations** - All database operations functional
4. **Relationship Integrity** - Foreign keys and constraints working
5. **Data Types** - Column types and constraints correct

**Example test output:**

```bash
====== test session starts ======
tests/test_essentials.py::TestDatabase::test_connection PASSED
tests/test_essentials.py::TestDatabase::test_schema_exists PASSED
tests/test_essentials.py::TestDatabase::test_alembic_current_version PASSED
====== 12 passed in 2.21s ======
```
