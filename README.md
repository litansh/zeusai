# ZeusAI: The DevOps CoPilot

## Overview
**ZeusAI** is the ultimate DevOps CoPilot – an all-in-one, AI-powered, no-code platform that radically simplifies the entire DevOps lifecycle. Designed for DevOps engineers, platform teams, and developers alike, ZeusAI automates, visualizes, and orchestrates everything from infrastructure provisioning to deployment, monitoring, alerting, cost optimization, and audit.

> One dashboard. Zero YAML. Full control.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Node.js 18+
- AWS CLI configured (optional for cloud features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/zeusai.git
   cd zeusai
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

3. **Start the platform**
   ```bash
   docker-compose up --build
   ```

4. **Access the dashboard**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Grafana: http://localhost:3001 (admin/zeusai)
   - Prometheus: http://localhost:9090

## 🏗️ Architecture

### Core Components

#### 🧠 AI-Powered Orchestrator (FastAPI)
- **Intent routing**: Maps commands or UI actions to MCP microservices
- **Guardrail enforcement**: Policy-based validation before execution
- **Signal aggregation**: Metrics, logs, and external APIs
- **Predictive analytics**: AI-driven decision making
- **Auditable history**: Complete audit trail of all changes

#### 🧩 MCP Microservices (Model Context Protocol)
Each tool is a containerized FastAPI service:
- `obs-mcp`: Prometheus metrics aggregation & anomaly detection
- `k8s-mcp`: Kubernetes interaction (scale, rollout, describe)
- `git-mcp`: PR generation (Terraform diffs, approvals)
- `cloud-mcp`: AWS CE, usage metrics, IAM scanning
- `kb-mcp`: Vector-based RAG knowledgebase
- `deploy-mcp`: Helm/Argo CD deployments
- `slo-mcp`: Enforce SLO thresholds for actions
- `tf-migrator`: Imports code or existing infra and converts to Terraform

#### 🖱️ Visual Terraform Builder
- **Drag & Drop Interface**: Build infrastructure visually
- **Auto-generation**: ZeusAI generates Terraform dynamically
- **GitOps Integration**: PRs created automatically
- **State Management**: Import and visualize existing infrastructure

#### 🔁 GitOps & CI/CD Automation
- **Best Practices Pipeline**: Terraform fmt, validate, plan
- **Security Scanning**: tfsec, checkov integration
- **Team-based Approvals**: RBAC with GitHub integration
- **Auto-triggered**: CI/CD on PR approvals

#### 📊 Observability Stack
- **Metrics**: Prometheus + Grafana (embedded)
- **Logs**: FluentBit → Loki
- **AI Anomaly Detection**: Predictive scaling and remediation
- **Alerting**: Telegram, Slack, MS Teams integration

#### 🔐 Guardrails & Policy Engine
- **YAML-defined Policies**: Change windows, RBAC, scaling limits
- **Real-time Enforcement**: Clear blocking reasons
- **Override Tracking**: Audited user overrides
- **Team Permissions**: Multi-team support with fallback reviewers

## 🎯 Key Features

### 🧠 AI-Powered Infrastructure Design
- **Visual Designer**: Drag & drop infrastructure components
- **Smart Recommendations**: AI suggests optimal configurations
- **Cost Optimization**: Real-time cost analysis and recommendations
- **Best Practices**: Enforced security and performance standards

### 🔄 GitOps-Native Workflow
- **Zero YAML**: Visual interface generates all configurations
- **PR-Based Changes**: All changes go through GitHub PRs
- **Approval Workflows**: Team-based approval processes
- **Audit Trail**: Complete history of all changes

### 📊 Unified Observability
- **Single Dashboard**: Metrics, logs, and alerts in one place
- **AI Anomaly Detection**: Predictive scaling and issue detection
- **Cost Monitoring**: Real-time cost tracking and optimization
- **Performance Insights**: AI-driven performance recommendations

### 🛡️ Enterprise Security
- **RBAC**: Role-based access control
- **Guardrails**: Policy enforcement at every step
- **Audit Logging**: Complete audit trail
- **Compliance**: SOC2, HIPAA, GDPR ready

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async API framework
- **PostgreSQL**: Primary database with audit logging
- **Redis**: Caching and session management
- **Prometheus**: Metrics collection and monitoring
- **Loki**: Log aggregation and querying
- **Qdrant**: Vector database for RAG

### Frontend
- **React 18**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Data visualization
- **Monaco Editor**: Code editing (Terraform preview)
- **React DnD**: Drag and drop functionality

### Infrastructure
- **Docker Compose**: Local development and testing
- **Kubernetes**: Production deployment
- **Terraform**: Infrastructure as Code
- **Helm**: Kubernetes package management

### AI/ML
- **OpenAI GPT**: Natural language processing
- **Vector Embeddings**: Document search and retrieval
- **Anomaly Detection**: Predictive analytics
- **Recommendation Engine**: Infrastructure optimization

## 📖 Usage Guide

### 1. Infrastructure Design

1. **Navigate to Infrastructure Designer**
   - Go to http://localhost:3000/infrastructure

2. **Drag & Drop Components**
   - Select components from the palette
   - Drop them onto the canvas
   - Configure each component's settings

3. **Generate Terraform**
   - Click "Generate Terraform" to create IaC
   - Review the generated code
   - Submit for approval

4. **Deploy Infrastructure**
   - Approve the PR in GitHub
   - Monitor deployment progress
   - View real-time status updates

### 2. Observability & Monitoring

1. **View Dashboard**
   - Access unified metrics at http://localhost:3000/observability
   - Monitor system health and performance
   - View cost analysis and trends

2. **Set Up Alerts**
   - Configure alert thresholds
   - Choose notification channels (Slack, Telegram)
   - Test alert delivery

3. **AI Insights**
   - Review AI-generated recommendations
   - Implement performance optimizations
   - Monitor cost savings

### 3. Deployment Management

1. **Create Deployments**
   - Use the deployment interface
   - Configure deployment strategies
   - Set up rollback procedures

2. **Monitor Deployments**
   - Track deployment progress
   - View deployment history
   - Analyze deployment metrics

3. **Automated Rollbacks**
   - Configure automatic rollback triggers
   - Monitor SLO compliance
   - Review rollback decisions

## 🔧 Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-west-2

# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=your-org/zeusai-infra

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
DATABASE_URL=postgresql://zeusai:zeusai@postgres:5432/zeusai
REDIS_URL=redis://redis:6379

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
```

### Guardrails Configuration

```yaml
guardrails:
  change_windows:
    production:
      allowed_hours: [2, 3, 4, 5]  # 2 AM to 5 AM UTC
      timezone: "UTC"
  
  rbac:
    admin: ["*"]
    dev: ["read", "deploy"]
    viewer: ["read"]
  
  scaling_limits:
    max_instances: 100
    max_memory_gb: 512
    max_cpu_cores: 64
  
  prod_lockdown:
    enabled: true
    required_approvals: 2
```

## 🚀 Deployment

### Local Development
```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f zeusai-orchestrator

# Access services
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Grafana: http://localhost:3001
```

### Production Deployment

1. **Kubernetes Deployment**
   ```bash
   kubectl apply -f k8s/
   ```

2. **Helm Chart**
   ```bash
   helm install zeusai ./helm/zeusai
   ```

3. **Terraform**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## 🔍 Monitoring & Troubleshooting

### Health Checks
- **API Health**: `GET /health`
- **Service Status**: Check individual MCP service health
- **Database**: PostgreSQL connection status
- **Redis**: Cache connectivity

### Logs
- **Application Logs**: `docker-compose logs zeusai-orchestrator`
- **MCP Services**: `docker-compose logs obs-mcp`
- **Infrastructure**: Terraform and deployment logs

### Metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Custom Dashboards**: Pre-configured ZeusAI dashboards

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup
```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend development
cd frontend
npm install
npm start
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent async web framework
- **React** for the powerful frontend framework
- **Tailwind CSS** for the utility-first CSS framework
- **Prometheus** for metrics collection
- **Grafana** for visualization
- **Terraform** for infrastructure as code

## 📞 Support

- **Documentation**: [docs.zeusai.com](https://docs.zeusai.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/zeusai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/zeusai/discussions)
- **Email**: support@zeusai.com

---

**Made with ❤️ by someone who's been in war rooms long enough to know the real problem… is repeating yourself.**
