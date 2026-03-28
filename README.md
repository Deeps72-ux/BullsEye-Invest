# 🎯 BullsEye-Invest

Empowering Indian retail investors with AI-driven insights. Transforming financial data into actionable recommendations, tailored to your investment goals.
A hackathon project by **Team Catalyst GPT** for the ET Hackathon 🚀

---

## 🧠 Problem Statement

India has **14+ crore demat accounts**, yet most retail investors:

* React to tips instead of data
* Miss critical filings and insider activity
* Struggle with technical analysis
* Manage portfolios based on intuition rather than insights

**BullsEye-Invest** aims to bridge this gap by building an **AI-powered intelligence layer** on top of financial data.

---

## 🚀 What We Are Building

### 🔍 Opportunity Radar

AI engine that continuously scans:

* Corporate filings
* Quarterly results
* Bulk/block deals
* Insider trades
* Regulatory updates

👉 Outputs **high-confidence actionable signals**, not just summaries.

---

### 📈 Chart Pattern Intelligence

* Detects real-time technical patterns (breakouts, reversals, etc.)
* Provides **plain-English explanations**
* Includes **historical success rates (backtesting)**

---

### 🤖 Market ChatGPT (Next Gen)

* Ask questions like:

  > “Why is Reliance going up?”
* Portfolio-aware responses
* Multi-step reasoning + source-backed insights

---

### 🎥 AI Market Video Engine *(Planned)*

* Auto-generated 30–90 sec market videos
* Visual insights like:

  * Sector rotation
  * FII/DII flows
  * IPO trackers

---

## 🏗️ Tech Architecture

### 🔧 Backend (Django)

Project: `bullseye_invest`

Modular apps:

* **accounts** → User authentication & profiles
* **market_data** → Stock data, filings, trades
* **signals** → Opportunity detection engine
* **analytics** → Indicators, patterns, backtesting
* **portfolio** → Holdings, performance, insights
* **alerts** → Notifications & subscriptions
* **ai_engine** → LLM-powered insights & chat
* **api** → Unified API gateway

---

## ⚙️ Tech Stack

* **Backend:** Django, Django REST Framework
* **Database:** PostgreSQL
* **Async Processing:** Celery + Redis
* **AI Layer:** OpenAI / LLM integration
* **Data Processing:** Pandas, NumPy
* **Deployment:** Docker

---

## 📡 API Overview

Base URL:

```
http://127.0.0.1:8000/api/
```

Key modules:

* Auth APIs (login/register)
* Market data APIs
* Signals (Opportunity Radar)
* Analytics (patterns + indicators)
* Portfolio insights
* AI chat engine

---

## 🐳 Running with Docker

### 1️⃣ Build & Start

```
docker-compose up --build
```

### 2️⃣ Run Migrations

```
docker-compose exec web python manage.py migrate
```

### 3️⃣ Create Superuser

```
docker-compose exec web python manage.py createsuperuser
```

---

## 🧪 API Testing

Use **Postman Collection** (included in repo) to test all endpoints.

---

## 🔥 Key Highlights

* ✅ AI-first architecture
* ✅ Modular & scalable design
* ✅ Real-time signal generation (planned)
* ✅ Portfolio-aware insights
* ✅ Plug-and-play data + AI layers

---

## 🛣️ Roadmap

* [ ] Integrate real NSE market data
* [ ] Build advanced signal algorithms
* [ ] Add JWT authentication
* [ ] Implement real-time alerts (WebSockets)
* [ ] Train custom ML models for prediction
* [ ] Deploy to cloud (AWS/GCP)

---

## 👥 Team

**Team Catalyst GPT** 💡
Built for the ET Hackathon

---

## 📌 Disclaimer

This project is for **educational and hackathon purposes only**.
Not intended as financial advice.

---

## ⭐ Contributing

Contributions are welcome!
Feel free to fork, raise issues, or submit PRs.

---

## 📬 Contact

For queries or collaboration:

* Reach out via GitHub issues

---

**Let’s make investing smarter, not harder 🚀**
