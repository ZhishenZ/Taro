# Taro Daily Service Deployment Guide

This guide explains how to deploy the `taro_daily` systemd service on a Linux host (VM or bare metal) that runs daily stock data fetching tasks.

## What is taro_daily?

The `taro_daily` service is a daemon that:
- Runs continuously in the background
- Executes `taro daily` command for configured tickers
- Automatically fetches daily stock data after market close
- Logs all operations to `/logs/` directory
- Restarts automatically if it crashes

## Prerequisites

### System Requirements
- Linux server (Ubuntu, Debian, CentOS, etc.)
- Python 3.11 or higher
- systemd (standard on most modern Linux distributions)
- PostgreSQL database (local or remote RDS)
- Sudo/root access for systemd service installation

### Software
```bash
# Update system
sudo apt-get update  # Ubuntu/Debian
# or
sudo yum update      # CentOS/RHEL

# Install Python and required packages
sudo apt-get install python3 python3-venv python3-pip git
```

## Installation Steps

### 1. Clone Repository

```bash
# Clone to a permanent location (e.g., /opt or home directory)
cd ~
git clone <your-repo-url>
cd Taro
```

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install taro package
pip install -e .
```

**Important:** Note the virtual environment path for later.
Example: `/home/username/Taro/venv`

### 3. Configure Database

#### Option A: Using Local PostgreSQL
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE taro_stock;
CREATE USER taro_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE taro_stock TO taro_user;
\q
```

#### Option B: Using Remote RDS/PostgreSQL
Export the connection string:
```bash
export DATABASE_URL="postgresql://user:password@host:5432/database"
```

Or set it in your shell profile (`~/.bashrc` or `~/.bash_profile`):
```bash
echo 'export DATABASE_URL="postgresql://user:password@host:5432/database"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Initialize Database Schema

```bash
# Make sure venv is activated
source venv/bin/activate

# Drop existing tables (if any)
taro drop -y

# Create migration
python -m alembic revision --autogenerate -m 'initial_migration'

# Apply migration
python -m alembic upgrade head
```

### 5. Configure Tickers

Edit the ticker configuration in `src/taro/configs.py`:

```python
# List of stock tickers to fetch daily
tickers = ["GOOGL", "AAPL", "MSFT", "TSLA"]

# Market close time (UTC)
close_utc_hour = 21  # 21:00 UTC = 4pm EST (market close)

# Daily task execution time (UTC)
daily_task_utc_hour = 22  # Run 1 hour after market close
```

### 6. Test Manually

Before deploying as a service, test the commands:

```bash
# Make sure venv is activated
source venv/bin/activate

# Test daily fetch for a single ticker
taro daily

# Test daemon (Ctrl+C to stop)
taro daemon -s 0.1 --test
```

### 7. Deploy Systemd Service

```bash
# Navigate to deploy_service directory
cd deploy_service

# Make script executable
chmod +x deploy_service.sh

# Run deployment script (with venv activated)
source ../venv/bin/activate
./deploy_service.sh
```

**The script will:**
1. ✅ Check you're in a virtual environment
2. ✅ Verify `taro` command is available
3. 🔧 Generate systemd service file
4. 📦 Install service to `/etc/systemd/system/`
5. 🔄 Reload systemd
6. 🚀 Enable and start the service

### 8. Verify Service is Running

```bash
# Check service status
sudo systemctl status taro_daily.service

# View recent logs
sudo journalctl -u taro_daily.service -n 50

# Check log files
tail -f /path/to/Taro/logs/taro.out.log
tail -f /path/to/Taro/logs/taro.err.log
```

## Service Management

### Check Status
```bash
sudo systemctl status taro_daily.service
```

### View Logs
```bash
# Live logs
sudo journalctl -u taro_daily.service -f

# Last 100 lines
sudo journalctl -u taro_daily.service -n 100

# Logs from specific date
sudo journalctl -u taro_daily.service --since "2025-10-11"

# Application logs
tail -f /path/to/Taro/logs/taro.out.log
```

### Stop Service
```bash
sudo systemctl stop taro_daily.service
```

### Start Service
```bash
sudo systemctl start taro_daily.service
```

### Restart Service
```bash
sudo systemctl restart taro_daily.service
```

### Disable Auto-start
```bash
sudo systemctl disable taro_daily.service
```

### Enable Auto-start
```bash
sudo systemctl enable taro_daily.service
```

## Update Application

When you update the code:

```bash
cd ~/Taro

# Pull latest code
git pull

# Activate venv and reinstall
source venv/bin/activate
pip install -e .

# Restart service to apply changes
sudo systemctl restart taro_daily.service

# Verify it's running
sudo systemctl status taro_daily.service
```

## Uninstall Service

```bash
cd ~/Taro/deploy_service

# Make script executable (if not already)
chmod +x remove_service.sh

# Run removal script
./remove_service.sh
```

This will:
- Stop the service
- Disable auto-start
- Remove service file
- Reload systemd

## Troubleshooting

### Service Won't Start

```bash
# Check detailed status
sudo systemctl status taro_daily.service -l

# Check logs for errors
sudo journalctl -u taro_daily.service -n 100
```

**Common issues:**
- Virtual environment path incorrect → Check `/etc/systemd/system/taro_daily.service`
- Database connection failed → Check `DATABASE_URL` environment variable
- Permission issues → Check log directory permissions

### Database Connection Failed

```bash
# Test connection manually
source venv/bin/activate
python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); print(engine.connect())"
```

### Logs Not Appearing

```bash
# Check log directory exists and is writable
ls -la /path/to/Taro/logs/

# Check service file configuration
sudo cat /etc/systemd/system/taro_daily.service
```

### Service Keeps Restarting

```bash
# Watch logs in real-time
sudo journalctl -u taro_daily.service -f
```

Check for:
- Python errors in the code
- Database connectivity issues
- Missing dependencies

## File Locations

| Item | Location |
|------|----------|
| **Application** | `~/Taro` (or your chosen path) |
| **Virtual Environment** | `~/Taro/venv` |
| **Service File** | `/etc/systemd/system/taro_daily.service` |
| **Application Logs** | `~/Taro/logs/taro.out.log`, `~/Taro/logs/taro.err.log` |
| **System Logs** | `journalctl -u taro_daily.service` |
| **Configuration** | `~/Taro/src/taro/configs.py` |

## Differences from Web Deployment

| Feature | Daily Service | Web Service |
|---------|--------------|-------------|
| **Deployment** | Systemd on host | Docker Compose |
| **Database** | Shared RDS or local | Shared RDS |
| **Purpose** | Background data fetching | Web UI for visualization |
| **Scaling** | Single instance | Can scale workers |
| **Restart** | systemd manages | Docker manages |
| **Location** | Host VM/Server | Docker containers |

Both services can run on the same server or different servers, sharing the same database.

## Security Checklist

- [ ] Virtual environment is isolated and not system-wide
- [ ] Database credentials are secured (not in git)
- [ ] Log files have appropriate permissions
- [ ] Service runs as non-root user
- [ ] Firewall allows PostgreSQL port (if remote DB)
- [ ] Regular backups configured
- [ ] Service logs are monitored

## Best Practices

1. **Use a dedicated user** - Consider creating a dedicated `taro` user for running the service
2. **Monitor logs** - Set up log rotation and monitoring
3. **Database backups** - Configure regular backups (RDS automated backups or pg_dump)
4. **Version control** - Track changes to configuration files
5. **Testing** - Test updates in a dev environment before production
6. **Documentation** - Keep notes on your specific configuration

## Next Steps

- Set up log rotation with `logrotate`
- Configure monitoring/alerting
- Set up automated backups
- Review and adjust ticker list in `configs.py`
- Set up email notifications for failures

For web interface deployment, see [DEPLOYMENT_WEB.md](DEPLOYMENT_WEB.md).
