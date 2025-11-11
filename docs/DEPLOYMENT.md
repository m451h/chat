# Deployment Guide

## Quick Deployment Options

### Option 1: Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Run application
streamlit run main.py
```

Or use the run script:
```bash
# Linux/Mac
./run.sh

# Windows
run.bat
```

### Option 2: Docker Deployment

#### 2.1 Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2.2 Create docker-compose.yml

```yaml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=sqlite:///./data/ehr_chatbot.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  # Optional: Add PostgreSQL for production
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ehr_chatbot
      POSTGRES_USER: ehr_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 2.3 Build and Run

```bash
# Build image
docker build -t ehr-chatbot .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: Cloud Deployment (Streamlit Cloud)

#### 3.1 Prepare Repository

```bash
# Create GitHub repository
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

#### 3.2 Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository and branch
4. Add secrets in Settings:
   ```
   OPENAI_API_KEY = "sk-..."
   DATABASE_URL = "sqlite:///./ehr_chatbot.db"
   ```
5. Click "Deploy"

### Option 4: Cloud Server (VPS/EC2)

#### 4.1 Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv -y

# Install nginx (optional, for reverse proxy)
sudo apt install nginx -y
```

#### 4.2 Setup Application

```bash
# Clone repository
git clone <your-repo-url>
cd ehr_chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
nano .env
# Add OPENAI_API_KEY
```

#### 4.3 Setup Systemd Service

Create `/etc/systemd/system/ehr-chatbot.service`:

```ini
[Unit]
Description=EHR Medical Chatbot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ehr_chatbot
Environment="PATH=/home/ubuntu/ehr_chatbot/venv/bin"
ExecStart=/home/ubuntu/ehr_chatbot/venv/bin/streamlit run main.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ehr-chatbot
sudo systemctl start ehr-chatbot
sudo systemctl status ehr-chatbot
```

#### 4.4 Setup Nginx Reverse Proxy

Create `/etc/nginx/sites-available/ehr-chatbot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/ehr-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4.5 Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Production Configuration

### PostgreSQL Setup

#### 1. Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
```

#### 2. Create Database

```bash
sudo -u postgres psql

CREATE DATABASE ehr_chatbot;
CREATE USER ehr_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ehr_chatbot TO ehr_user;
\q
```

#### 3. Update Configuration

Edit `.env`:
```
DATABASE_URL=postgresql://ehr_user:secure_password@localhost:5432/ehr_chatbot
```

Install driver:
```bash
pip install psycopg2-binary
```

### Environment Variables

Production `.env`:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ehr_chatbot

# Application
APP_NAME=EHR Medical Chatbot
MAX_CONVERSATION_HISTORY=20
CHUNK_SIZE=4000

# Security (add these)
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### Security Checklist

- [ ] API keys stored in environment variables
- [ ] Database credentials secured
- [ ] SSL/HTTPS enabled
- [ ] Firewall configured (only 80, 443, 22)
- [ ] Regular security updates
- [ ] Backup strategy implemented
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Error messages sanitized
- [ ] Audit logging enabled

### Monitoring Setup

#### 1. Application Logs

Create `logs/` directory:
```bash
mkdir logs
```

Update code to log:
```python
import logging

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### 2. Log Rotation

Install logrotate:
```bash
sudo nano /etc/logrotate.d/ehr-chatbot
```

```
/home/ubuntu/ehr_chatbot/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
}
```

#### 3. Monitoring Tools

**Option A: Simple monitoring**
```bash
# Install htop
sudo apt install htop

# Monitor logs
tail -f logs/app.log

# Check service status
sudo systemctl status ehr-chatbot
```

**Option B: Advanced monitoring (Prometheus + Grafana)**
- Setup Prometheus to scrape metrics
- Setup Grafana dashboards
- Configure alerts

### Backup Strategy

#### 1. Database Backup

Create backup script `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup SQLite
cp ehr_chatbot.db $BACKUP_DIR/ehr_chatbot_$DATE.db

# Or PostgreSQL
pg_dump -U ehr_user ehr_chatbot > $BACKUP_DIR/ehr_chatbot_$DATE.sql

# Compress
gzip $BACKUP_DIR/ehr_chatbot_$DATE.*

# Delete old backups (older than 30 days)
find $BACKUP_DIR -name "ehr_chatbot_*.gz" -mtime +30 -delete
```

#### 2. Setup Cron Job

```bash
crontab -e
```

Add:
```
0 2 * * * /home/ubuntu/ehr_chatbot/backup.sh
```

### Scaling Considerations

#### Horizontal Scaling

1. **Use PostgreSQL** (shared database)
2. **Load Balancer** (nginx or cloud LB)
3. **Multiple App Instances**
4. **Session Stickiness** (if using in-memory cache)

#### Vertical Scaling

1. **Increase server resources**
2. **Optimize database queries**
3. **Add caching layer** (Redis)
4. **Use connection pooling**

### Integration with Real EHR

Replace mock functions in `mock_data/backend.py`:

```python
import requests

EHR_API_BASE = os.getenv("EHR_API_BASE")
EHR_API_KEY = os.getenv("EHR_API_KEY")

def get_user_conditions(user_id: int) -> List[Dict]:
    """Fetch from real EHR API"""
    response = requests.get(
        f"{EHR_API_BASE}/patients/{user_id}/conditions",
        headers={"Authorization": f"Bearer {EHR_API_KEY}"}
    )
    return response.json()
```

### Authentication Integration

Add OAuth2 authentication:

```python
# In main.py
from streamlit_oauth import OAuth2Component

oauth2 = OAuth2Component(
    client_id=os.getenv("OAUTH_CLIENT_ID"),
    client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
    authorize_endpoint="https://ehr-system.com/oauth/authorize",
    token_endpoint="https://ehr-system.com/oauth/token",
)

result = oauth2.authorize_button("Login with EHR")
if result:
    user_id = result["user_id"]
    st.session_state.user_id = user_id
```

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor API usage
- Verify backups

**Weekly:**
- Review system performance
- Update dependencies (if needed)
- Check disk space

**Monthly:**
- Security updates
- Review API costs
- Optimize database
- Test backup restoration

### Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart ehr-chatbot
```

### Rollback Procedure

```bash
# Revert to previous version
git revert HEAD
git push

# Or restore from backup
cp /home/ubuntu/backups/ehr_chatbot_YYYYMMDD.db ehr_chatbot.db

# Restart service
sudo systemctl restart ehr-chatbot
```

## Support

For deployment issues:
1. Check logs: `sudo journalctl -u ehr-chatbot -f`
2. Verify environment variables
3. Test database connection
4. Check API key validity
5. Review nginx error logs: `sudo tail -f /var/log/nginx/error.log`

---

**Ready for production deployment! 🚀**
