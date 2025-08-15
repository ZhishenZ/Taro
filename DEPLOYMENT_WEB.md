# Taro Production Deployment Guide

## Prerequisites

### AWS Resources Needed:
1. **EC2 Instance** (t2.medium or larger recommended)
2. **RDS PostgreSQL Instance** (or managed PostgreSQL)
3. **Security Groups** configured for:
   - HTTP (port 80)
   - HTTPS (port 443)
   - PostgreSQL (port 5432) - only from EC2 security group
4. **Domain Name** pointing to your EC2 instance
5. **Elastic IP** (recommended) for stable IP address

## Setup Instructions

### 1. Prepare Database (RDS)

Create a PostgreSQL database on RDS:
- Engine: PostgreSQL 15
- Instance class: db.t3.micro (or larger)
- Database name: `taro_stock`
- Username: `taro_user`
- Password: (generate secure password)

**Security Group**: Allow inbound on port 5432 from EC2 security group only

### 2. Setup EC2 Instance

SSH into your EC2 instance:
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

Install Docker and Docker Compose:
```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes to take effect
exit
```

### 3. Clone Repository

```bash
git clone <your-repo-url>
cd Taro
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

**If migrating from older deployment:**
If you have an existing `.env.prod` file, rename it:
```bash
mv .env.prod .env
```

Fill in:
- `DOMAIN`: Your domain (e.g., `taro.yourdomain.com`)
- `ACME_EMAIL`: Your email for SSL certificate notifications
- `DATABASE_URL`: Your RDS connection string
- `EC2_HOST`: Your domain (should match DOMAIN)

Example:
```bash
DOMAIN=taro.example.com
ACME_EMAIL=admin@example.com
DATABASE_URL=postgresql://taro_user:your_password@your-db.region.rds.amazonaws.com:5432/taro_stock
EC2_HOST=taro.example.com
```

**Note:** Docker Compose automatically loads variables from `.env` file.

### 5. Setup Database Schema

Before starting the app, initialize the database:

```bash
# Option 1: If using Alembic migrations
docker-compose -f docker-compose.prod.yml run --rm taro-app python -m alembic upgrade head

# Option 2: If starting fresh (use taro drop and migrations)
docker-compose -f docker-compose.prod.yml run --rm taro-app taro drop -y
docker-compose -f docker-compose.prod.yml run --rm taro-app python -m alembic revision --autogenerate -m 'initial_migration'
docker-compose -f docker-compose.prod.yml run --rm taro-app python -m alembic upgrade head
```

### 6. Build and Start Services

```bash
# Build the Docker image
docker-compose -f docker-compose.prod.yml build

# Start in detached mode
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

**If you get "executable file not found" error, do a clean build:**

```bash
# Stop and remove containers
docker-compose -f docker-compose.prod.yml down

# Clean build (no cache)
docker-compose -f docker-compose.prod.yml build --no-cache

# Start the services
docker-compose -f docker-compose.prod.yml up -d
```

**Quick one-liner to rebuild everything:**
```bash
docker-compose -f docker-compose.prod.yml down --rmi all && docker-compose -f docker-compose.prod.yml build --no-cache && docker-compose -f docker-compose.prod.yml up -d
```

### 7. Verify Deployment

1. **HTTP redirect**: Visit `http://your-domain.com` - should redirect to HTTPS
2. **HTTPS access**: Visit `https://your-domain.com` - should show your app with valid SSL certificate
3. **Database connection**: Try loading a ticker that has data

### 8. Load Initial Data (Optional)

```bash
# Backfill data for a ticker
docker-compose -f docker-compose.prod.yml exec taro-app taro backfill -t GOOGL
```

## Management Commands

### View Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f [service-name]
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Update Application
```bash
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Backup Database
Since you're using RDS, use AWS automated backups or:
```bash
docker-compose -f docker-compose.prod.yml exec taro-app taro query -t GOOGL -o backup.csv
```

## Security Checklist

- [ ] RDS security group only allows EC2 security group
- [ ] Strong database password (not default)
- [ ] `.env` file has restricted permissions (chmod 600)
- [ ] `.env` is listed in `.gitignore` (do not commit secrets)
- [ ] EC2 security group only allows ports 80, 443, and 22
- [ ] SSH key is secure (not shared)
- [ ] Domain SSL certificate is valid (Let's Encrypt)
- [ ] Database credentials are not in git
- [ ] Regular backups configured (RDS automated backups)

## Monitoring

### Check Application Health
```bash
curl https://your-domain.com
```

### Check SSL Certificate
```bash
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Monitor Resources
```bash
# Check Docker stats
docker stats

# Check disk usage
df -h

# Check memory
free -h
```

## Troubleshooting

### SSL Certificate Issues
If Let's Encrypt fails:
1. Check domain DNS points to EC2 IP
2. Check ports 80 and 443 are open
3. Check logs: `docker-compose -f docker-compose.prod.yml logs traefik`

### Database Connection Issues
1. Verify RDS security group allows EC2
2. Test connection: `docker-compose -f docker-compose.prod.yml exec taro-app psql $DATABASE_URL`
3. Check environment variables: `docker-compose -f docker-compose.prod.yml config`

### Application Not Starting
1. Check logs: `docker-compose -f docker-compose.prod.yml logs taro-app`
2. Verify gunicorn is installed: `docker-compose -f docker-compose.prod.yml exec taro-app pip list | grep gunicorn`

## Cost Optimization

- **EC2**: Use t3.micro or t3.small for small-medium workloads
- **RDS**: Use db.t3.micro for development, db.t3.small for production
- **Storage**: Clean up old backups and logs
- **Auto-scaling**: Consider using ECS/Fargate for better scaling

## Development vs Production

| Feature | Development (.devcontainer) | Production (docker-compose.prod.yml) |
|---------|----------------------------|-------------------------------------|
| Database | Local PostgreSQL container | External RDS |
| Volumes | Code mounted for hot-reload | Built into image |
| Server | Flask dev server | Gunicorn WSGI |
| HTTPS | No (HTTP only) | Yes (Traefik + Let's Encrypt) |
| Restart | Manual | Automatic (restart: always) |
| Port mapping | 5000:5000, 5006:5006 | 80:80, 443:443 via Traefik |
