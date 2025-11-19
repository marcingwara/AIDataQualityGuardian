# AIDataQualityGuardian

AIDataQualityGuardian is an intelligent, automated Data Quality monitoring system for Tableau dashboards. It detects anomalies, validates metrics, evaluates data quality scores, generates automated tests, and sends professional alerts to Slack, email, or JIRA.

Designed for the Tableau Developer Challenge, this project showcases the power of combining Tableau Metadata API, REST API, automated DQ logic, anomaly detection, AI-driven explanations, and DevOps-style automation.

---

## 🚀 Key Features

### **1. Automated Data Quality Scanning**
- Scans Tableau dashboards using Metadata API and REST API
- Extracts metrics, worksheets, datasources, and structures
- Supports numerical KPI extraction and structure validation

### **2. Data Quality Rules Engine**
- Detects null/zero values
- Detects negative numbers
- Flatline detection (no variation)
- Extreme value detection

### **3. Anomaly Detection Engine**
- Sudden spike detection
- Sudden drop detection
- Outlier detection (based on std deviation)

### **4. AI-Driven Issue Explanation**
- Optional OpenAI integration for insights
- Provides root-cause suggestions
- Works in fallback mode without API key

### **5. Data Quality Scoring (0–100)**
- Weighted scoring: critical, major, and minor issues
- One score per dashboard for instant assessment

### **6. Automated Test Generation**
- Builds pytest-based regression tests
- Generates code dynamically per dashboard
- Exports tests as `.py` files

### **7. Multi-channel Alerting**
- Slack (text + Block Kit formatted alerts)
- Email (plain text + HTML)
- JIRA ticket auto-creation

### **8. Modular, Extensible Architecture**
- Clean folder structure
- Easy to extend with new rules, connectors, exporters

---

## 🧩 Architecture Overview

```
AIDataQualityGuardian/
│
├── src/
│   ├── tableau/
│   │   ├── metadata_client.py
│   │   ├── rest_client.py
│   │   ├── data_fetcher.py
│   │   └── parsers/
│   │       ├── metrics_parser.py
│   │       └── structure_parser.py
│   │
│   ├── dq/
│   │   ├── quality_rules.py
│   │   ├── anomaly_detector.py
│   │   ├── report_builder.py
│   │   ├── ai_analyzer.py
│   │   ├── score_calculator.py
│   │   └── validators.py
│   │
│   ├── alerts/
│   │   ├── slack_notifier.py
│   │   ├── email_notifier.py
│   │   └── message_templates.py
│   │
│   ├── tests_generator/
│   │   ├── test_builder.py
│   │   └── exporters/
│   │       ├── file_exporter.py
│   │       └── jira_exporter.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   └── helper.py
│   │
│   └── main.py
│
├── .env
├── .env.example
└── README.md
```

---

## ⚙️ Installation

### **1. Clone the repository**
```bash
git clone https://github.com/your/repo.git
cd AIDataQualityGuardian
```

### **2. Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🔐 Configuration (.env)

Copy the example file:
```bash
cp .env.example .env
```

Fill in the values:
```env
# Tableau
TABLEAU_SITE=your_site
TABLEAU_SERVER=https://your-server.tableau.com
TABLEAU_TOKEN_NAME=your_pat_name
TABLEAU_TOKEN_SECRET=your_pat_secret

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_BOT_TOKEN=

# Email
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=
EMAIL_TO=

# AI (optional)
OPENAI_API_KEY=

# Logging
LOG_TO_FILE=true
```

---

## ▶️ Running the Project

```bash
python -m src.main
```

This will:
1. Authenticate with Tableau
2. Fetch dashboards & metrics
3. Run quality rules
4. Run anomaly detection
5. Add AI insights (optional)
6. Calculate DQ Scores
7. Build a report
8. Send Slack & email alerts
9. Generate automated tests

---

## 📤 Output Examples

### **Slack Block Kit Alert**
- Dashboard name
- Issues grouped by metric
- AI explanations
- Data Quality Score

### **Generated Tests**
```
generated_tests/sales_overview_tests.py
```

### **JIRA Tickets**
Automatically created:
```
[DQ] Sales Overview – Revenue: Sudden spike detected
```

---

## 🧠 APIs & Tools Used

- **Tableau Metadata API (GraphQL)**
- **Tableau REST API**
- **OpenAI API (optional)**
- **Slack Webhooks + Block Kit**
- **SMTP Email**
- **JIRA Cloud REST API**
- **pytest test generation**
- **Python logging system**

---

## 🏆 Why It Stands Out (Competition Notes)

- End-to-end Data Quality solution for Tableau
- Combines automation, analytics, and AI
- Automatically generates regression tests
- Provides actionable insights, not just alerts
- Multi-channel alerting (Slack, email, JIRA)
- Extensible architecture for enterprise use

---

## 📅 Roadmap

- Tableau Extract API support
- Historical anomaly learning
- Dashboard-to-dashboard comparisons
- Automated workbook structure regression testing
- CI/CD integration for regression suite

---

## 📄 License
MIT License.

---

## 👤 Author
Marcin Gwara — QA Automation Engineer & Data Quality Enthusiast.

