# Taro - Stock Analysis Platform

A comprehensive stock analysis platform with automated data fetching, database management, and web visualization capabilities. Deployed on AWS EC2 with PostgreSQL database backend.

## Project Overview

Taro is a production-ready stock market data platform that combines:
- **Automated data collection**: Background service that fetches daily stock metrics
- **Database management**: PostgreSQL with automated schema migrations via Alembic
- **Web interface**: Interactive visualization dashboard built with Bokeh and Flask
- **CI/CD pipeline**: Automated testing and deployment via GitHub Actions

## Architecture

### Deployment Target
- **Platform**: AWS EC2 (t2.medium or larger recommended)
- **Database**: Amazon RDS PostgreSQL 15 (or local PostgreSQL)
- **Domain**: Custom domain with automatic SSL via Let's Encrypt
- **Networking**: Configured security groups for HTTP/HTTPS/PostgreSQL access

### Two Main Components

#### 1. Daily Service (Database Management)
**Purpose**: Background daemon for automated stock data fetching

- **Deployment**: systemd service running directly on EC2 host
- **Functionality**:
  - Runs `taro daily` command at scheduled times
  - Fetches daily stock metrics for configured tickers
  - Automatically executes after market close
  - Restarts automatically on failure
  - Logs to `/logs/` directory
- **Configuration**: `src/taro/configs.py` - ticker list and schedule
- **Service Management**: systemctl commands (start/stop/restart/status)
- **Documentation**: [DEPLOYMENT_DAILY.md](DEPLOYMENT_DAILY.md)

**Key Features**:
- Virtual environment isolation
- Continuous background operation
- Database migration support
- Comprehensive logging and error handling

#### 2. Web Service (Website)
**Purpose**: Interactive web interface for stock visualization

- **Deployment**: Docker Compose with multi-container setup
- **Components**:
  - **taro-app**: Flask application with Gunicorn WSGI server
  - **traefik**: Reverse proxy with automatic SSL (Let's Encrypt)
- **Functionality**:
  - Interactive stock charts and analysis
  - Real-time data visualization with Bokeh
  - RESTful API endpoints
  - Responsive web UI
- **Ports**: 80 (HTTP) → 443 (HTTPS redirect)
- **SSL**: Automatic certificate management via Traefik
- **Documentation**: [DEPLOYMENT_WEB.md](DEPLOYMENT_WEB.md)

**Key Features**:
- Production-ready with Gunicorn workers
- Automatic HTTPS with certificate renewal
- Health monitoring and auto-restart
- Scalable container architecture

## Core Technology Stack

### Main Program: `taro` Python Package
**Entry Point**: CLI tool installed as `taro` command

**Package Structure**:
```
src/taro/
├── cli/              # Command-line interface and web server
│   ├── __main__.py   # Main entry point
│   └── templates/    # Web UI HTML templates
├── db/               # Database models and connections
│   └── models.py     # SQLAlchemy models (DailyMetrics, Fundamentals)
├── fetcher/          # Stock data fetching logic
├── migrations/       # Alembic database migrations
├── analysis/         # Data analysis utilities
├── bokeh_figures/    # Interactive chart generation
├── tickersync/       # Ticker synchronization
└── configs.py        # Application configuration
```

**Command-Line Interface**:
- `taro daily` - Fetch daily stock data for configured tickers
- `taro daemon` - Run continuous background service
- `taro backfill -t TICKER` - Backfill historical data
- `taro query -t TICKER` - Query data from database
- `taro drop -y` - Drop database tables
- `taro serve` - Start web server (development)

### Database Schema

**Tables**:
1. **daily_metrics**: Core stock data (date, ticker)
   - Primary key: `id`
   - Unique constraint: (`trade_date`, `ticker`)

2. **fundamentals**: Price and volume data
   - Foreign key: `daily_metrics_id` (one-to-one)
   - Columns: open_price, high_price, close_price, low_price, volume

**Schema Management**:
- Automated migrations with Alembic
- Version control for database changes
- Automatic schema detection and updates
- Rollback capability for migrations

### Dependencies
**Core**:
- Python 3.11+
- Flask (web framework)
- Bokeh (data visualization)
- SQLAlchemy (ORM)
- Alembic (migrations)
- yfinance (stock data)
- psycopg2-binary (PostgreSQL driver)
- gunicorn (WSGI server)

**Development**:
- pytest (testing framework)
- pytest-cov (coverage reporting)
- black (code formatting)

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Continuous Integration (`.github/workflows/ci.yml`)
**Triggers**: Push to main, Pull requests

**Steps**:
1. Checkout code
2. Setup Python 3.11
3. Start PostgreSQL service container
4. Install dependencies (`pip install -e ".[dev]"`)
5. Run Alembic migrations (`alembic upgrade head`)
6. Execute test suite (`pytest tests/ -v`)

**Testing**:
- Database connectivity and CRUD operations
- Schema validation and migration tracking
- Model-database synchronization
- Comprehensive test suite in `tests/test_essentials.py`

#### 2. Deployment (`.github/workflows/deploy.yml`)
**Triggers**: Merge to main branch

**Functionality**:
- Automated deployment to EC2
- Uses SSH with secrets (EC2_HOST, EC2_KEY)
- Deploys via custom composite action
- Manages environment variables and configurations

**Deployment Workflow**:
1. Connect to EC2 via SSH
2. Pull latest code from repository
3. Rebuild Docker images
4. Restart services with zero downtime
5. Verify deployment health

## Development Environment

### Dev Container Setup
The project uses VS Code Dev Containers for consistent development:

**Automatic Setup**:
1. PostgreSQL 15 container
2. Python dependencies installation
3. Database schema initialization
4. Migration application
5. Development server startup

**Container Features**:
- Hot-reload for code changes
- Persistent database volumes
- Port forwarding (5000, 5006)
- Integrated debugging support

### Local Development
```bash
# Clone repository
git clone <repo-url>
cd Taro

# Open in VS Code Dev Container
# OR manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Setup database
alembic upgrade head

# Run tests
pytest tests/ -v

# Start development server
taro serve
```

## Deployment Guides

### Quick Deployment Overview

#### Daily Service Deployment
1. Clone repository to EC2
2. Setup Python virtual environment
3. Configure database connection (DATABASE_URL)
4. Initialize database schema (Alembic migrations)
5. Deploy systemd service: `cd deploy_service && ./deploy_service.sh`
6. Verify: `sudo systemctl status taro_daily.service`

#### Web Service Deployment
1. Clone repository to EC2
2. Install Docker and Docker Compose
3. Configure environment variables in `.env`
4. Build images: `docker-compose -f docker-compose.prod.yml build`
5. Start services: `docker-compose -f docker-compose.prod.yml up -d`
6. Verify: Access `https://your-domain.com`

**Both services can run concurrently** on the same EC2 instance, sharing the same PostgreSQL database.

## Project Structure

```
Taro/
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   │   ├── ci.yml         # Test automation
│   │   └── deploy.yml     # Deployment automation
│   └── actions/           # Custom GitHub Actions
├── .devcontainer/         # Dev container configuration
├── deploy_service/        # Systemd service deployment scripts
├── src/taro/             # Main Python package
│   ├── cli/              # CLI and web interface
│   ├── db/               # Database models
│   ├── fetcher/          # Data fetching
│   ├── migrations/       # Alembic migrations
│   └── ...
├── tests/                # Comprehensive test suite
├── docker-compose.prod.yml  # Production Docker config
├── pyproject.toml        # Package configuration
├── alembic.ini          # Migration configuration
├── .env.example         # Environment template
├── README.md            # Development guide
├── DEPLOYMENT_DAILY.md  # Daily service deployment
├── DEPLOYMENT_WEB.md    # Web service deployment
└── CLAUDE.md            # This file

```

## Key Features

### Automated Operations
- **Daily data fetching**: Scheduled after market close
- **Database migrations**: Automatic schema updates
- **Service recovery**: Auto-restart on failure
- **SSL management**: Automatic certificate renewal

### Production Ready
- **Monitoring**: Comprehensive logging and status tracking
- **Security**: Encrypted connections, secure credentials
- **Scalability**: Docker containers, database optimization
- **Reliability**: Health checks, automatic restarts

### Developer Experience
- **Dev containers**: One-click development environment
- **Testing**: Comprehensive automated test suite
- **CI/CD**: Automated testing and deployment
- **Documentation**: Detailed deployment guides

## Configuration

### Environment Variables
```bash
# Database (required for both services)
DATABASE_URL=postgresql://user:password@host:5432/taro_stock

# Web service (Docker deployment)
DOMAIN=taro.example.com
ACME_EMAIL=admin@example.com
EC2_HOST=taro.example.com

# Individual DB components (alternative to DATABASE_URL)
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=taro_stock
DB_USER=taro_user
DB_PASSWORD=your_password
```

### Ticker Configuration
Edit `src/taro/configs.py`:
```python
tickers = ["GOOGL", "AAPL", "MSFT", "TSLA"]
daily_task_utc_hour = 22  # 10 PM UTC (1 hour after market close)
```

## Monitoring and Management

### Daily Service
```bash
# Status check
sudo systemctl status taro_daily.service

# View logs
sudo journalctl -u taro_daily.service -f

# Restart service
sudo systemctl restart taro_daily.service
```

### Web Service
```bash
# Status check
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Database
```bash
# Check migration status
alembic current

# View migration history
alembic history

# Apply pending migrations
alembic upgrade head
```

## Security Considerations

- **Database credentials**: Never commit to git, use environment variables
- **RDS security groups**: Restrict PostgreSQL access to EC2 only
- **SSH keys**: Secure EC2 access with strong key pairs
- **SSL/TLS**: Automatic HTTPS via Let's Encrypt
- **Environment files**: Protected with restricted permissions (chmod 600)
- **Service isolation**: Docker containers and systemd isolation

## Testing

### Test Coverage
- Database connectivity and CRUD operations
- Schema validation and integrity
- Migration tracking and versioning
- Model-database synchronization
- Foreign key relationships
- Data type validation

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test categories
pytest tests/test_essentials.py::TestDatabase -v
pytest tests/test_essentials.py::TestMigrations -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Troubleshooting

### Common Issues

**Database Connection Failed**:
- Verify DATABASE_URL is correct
- Check RDS security group allows EC2
- Test connection: `psql $DATABASE_URL`

**Service Won't Start**:
- Check logs: `sudo journalctl -u taro_daily.service -n 100`
- Verify virtual environment path in service file
- Check database accessibility

**Docker Issues**:
- Clean rebuild: `docker-compose -f docker-compose.prod.yml build --no-cache`
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Verify environment variables: `docker-compose -f docker-compose.prod.yml config`

**SSL Certificate Issues**:
- Verify DNS points to EC2 IP
- Check ports 80/443 are open
- Review Traefik logs: `docker-compose -f docker-compose.prod.yml logs traefik`

## Cost Optimization

**AWS Resources**:
- **EC2**: t3.micro or t3.small for small-medium workloads
- **RDS**: db.t3.micro for dev, db.t3.small for production
- **Storage**: Regular cleanup of logs and old data
- **Elastic IP**: Recommended for stable DNS

## Future Enhancements

- Multi-instance scaling with load balancer
- Real-time streaming data support
- Advanced analytics and ML predictions
- Mobile-responsive UI improvements
- API rate limiting and authentication
- Automated backup and disaster recovery

## Support and Documentation

- **Development Guide**: [README.md](README.md)
- **Daily Service**: [DEPLOYMENT_DAILY.md](DEPLOYMENT_DAILY.md)
- **Web Service**: [DEPLOYMENT_WEB.md](DEPLOYMENT_WEB.md)
- **Test Suite**: `tests/test_essentials.py`
- **Package Config**: `pyproject.toml`

## License and Attribution

This project demonstrates modern software engineering practices including containerization, CI/CD, database migrations, and production deployment on AWS infrastructure.
