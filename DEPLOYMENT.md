# 🚀 ZeusAI Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the ZeusAI platform locally, including testing, health checks, and monitoring.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Docker**: Version 20.10+ with Docker Compose
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 10GB free space
- **CPU**: 4 cores minimum (8 cores recommended)

### Software Requirements
- Docker Desktop or Docker Engine
- Docker Compose
- Git
- curl (for health checks)

## 🛠️ Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd zeusai
make setup
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Deploy
```bash
make deploy
# or
./scripts/deploy-local.sh
```

### 4. Access the Platform
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/zeusai)
- **Prometheus**: http://localhost:9090

## 🧪 Testing

### Running Tests

#### All Tests
```bash
make test
# or
./scripts/run-tests.sh --type all
```

#### Specific Test Types
```bash
# Unit tests
make test-unit
./scripts/run-tests.sh --type unit

# API tests
make test-api
./scripts/run-tests.sh --type api

# Integration tests
make test-integration
./scripts/run-tests.sh --type integration

# Frontend tests
make test-frontend
./scripts/run-tests.sh --type frontend
```

#### Test with Coverage
```bash
make test-coverage
./scripts/run-tests.sh --type all
```

### Test Reports
- **Coverage Report**: `htmlcov/index.html`
- **Test Summary**: `test-reports/summary.md`
- **JUnit XML**: `test-results.xml`

## 🏥 Health Checks

### Automated Health Check
```bash
./scripts/health-check.sh
# or
make health
```

### Manual Health Checks

#### Service Status
```bash
make status
docker-compose ps
```

#### Individual Service Checks
```bash
# Backend API
curl -f http://localhost:8000/health

# Frontend
curl -f http://localhost:3000

# Database
docker-compose exec postgres pg_isready -U zeusai

# Redis
docker-compose exec redis redis-cli ping
```

#### Log Monitoring
```bash
# All services
make logs
docker-compose logs -f

# Specific service
make logs-backend
make logs-frontend
```

## 🚀 Deployment Options

### Full Deployment (Default)
```bash
make deploy
./scripts/deploy-local.sh --type full
```

### Minimal Deployment
```bash
make deploy-minimal
./scripts/deploy-local.sh --type minimal
```

### Production Deployment
```bash
make deploy-prod
./scripts/deploy-local.sh --type production
```

### Clean Deployment
```bash
make deploy-clean
./scripts/deploy-local.sh --type full --clean-start
```

## 🔧 Development Commands

### Service Management
```bash
# Start services
make start

# Stop services
make stop

# Restart services
make restart

# Check status
make status
```

### Building
```bash
# Build all images
make build

# Build specific components
make build-backend
make build-frontend
make build-mcp
```

### Development Shells
```bash
# Backend shell
make shell-backend

# Frontend shell
make shell-frontend
```

## 🧹 Maintenance

### Cleaning
```bash
# Clean everything
make clean

# Clean logs only
make clean-logs

# Clean data volumes
make clean-data
```

### Backup and Restore
```bash
# Create backup
make backup

# Restore from backup
make restore BACKUP_FILE=backups/zeusai_20240101_120000.sql
```

### Database Management
```bash
# Run migrations
make db-migrate

# Reset database
make db-reset
```

## 📊 Monitoring

### Access Monitoring Tools
```bash
make monitor
```

### Performance Testing
```bash
# Performance tests
make perf-test

# Load testing
make load-test
```

## 🔍 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker status
docker info

# Check available resources
docker system df

# Restart Docker
sudo systemctl restart docker
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Stop conflicting services
sudo lsof -ti:3000 | xargs kill -9
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Check database health
docker-compose exec postgres pg_isready -U zeusai
```

#### Memory Issues
```bash
# Check memory usage
free -h

# Increase Docker memory limit
# (In Docker Desktop settings)
```

### Log Analysis
```bash
# View recent errors
docker-compose logs --since=10m | grep -i error

# View specific service errors
docker-compose logs zeusai-orchestrator | grep -i error

# Follow logs in real-time
docker-compose logs -f --tail=100
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check disk space
df -h

# Clean up Docker
docker system prune -a
```

## 🔒 Security

### Security Checks
```bash
# Run security audit
make security

# Check for vulnerabilities
npm audit
pip-audit
```

### Environment Security
- Never commit `.env` files
- Use strong passwords in production
- Enable HTTPS in production
- Regular security updates

## 📈 Production Considerations

### Scaling
- Use multiple replicas for high availability
- Implement load balancing
- Use external databases for production
- Enable auto-scaling

### Monitoring
- Set up external monitoring (DataDog, New Relic)
- Configure alerting
- Regular backup schedules
- Performance monitoring

### Security
- Use secrets management
- Enable RBAC
- Network segmentation
- Regular security audits

## 📚 Additional Resources

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [README.md](README.md)
- [Architecture Guide](ARCHITECTURE.md)

### Support
- Check logs: `make logs`
- Health check: `make health`
- System info: `make info`

### Quick Reference
```bash
# Start everything
make quick-start

# Check everything is working
make health

# View logs
make logs

# Stop everything
make stop
```

## 🎯 Success Criteria

After deployment, verify:
- [ ] All services are running (`make status`)
- [ ] Health checks pass (`make health`)
- [ ] Dashboard is accessible (http://localhost:3000)
- [ ] API documentation is available (http://localhost:8000/docs)
- [ ] All tests pass (`make test`)
- [ ] No errors in logs (`make logs`)

## 🚨 Emergency Procedures

### Complete Reset
```bash
# Stop and remove everything
docker-compose down --volumes --remove-orphans
docker system prune -a --force

# Fresh deployment
make deploy-clean
```

### Data Recovery
```bash
# Restore from latest backup
make restore BACKUP_FILE=$(ls -t backups/*.sql | head -1)
```

### Service Recovery
```bash
# Restart specific service
docker-compose restart <service-name>

# Rebuild and restart
docker-compose up --build -d <service-name>
```

---

**Note**: This deployment guide covers local development and testing. For production deployments, additional security, monitoring, and scaling considerations apply.
