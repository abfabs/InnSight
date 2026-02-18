# InnSight - Smart Airbnb Explorer

## Table of Contents
- [Project Charter](#project-charter)
- [1. Project Objectives](#1-project-objectives)
- [2. Stakeholders and Roles](#2-stakeholders-and-roles)
- [3. Scope](#3-scope)
- [4. Risks and Mitigation Strategies](#4-risks-and-mitigation-strategies)
- [5. High-Level Plan](#5-high-level-plan)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [License](#license)
- [Authors](#authors)

---

## Project Charter

### Project Overview
InnSight is an interactive data visualization platform designed to help travelers make smarter, more informed decisions when choosing where to stay. Planning a trip can be overwhelming, especially when you're trying to figure out which neighborhood fits your vibe, what's a fair price, or whether other travelers actually enjoyed their experience. That's where InnSight comes in.

By combining geographic mapping, pricing analysis, machine learning-powered sentiment analysis of guest reviews, and an AI-driven travel assistant, InnSight transforms raw Airbnb data into clear, actionable insights. Instead of endlessly scrolling through listings or reading hundreds of reviews, travelers can explore cities visually, compare neighborhoods at a glance, and converse with an intelligent chatbot that draws on thousands of real guest reviews to answer questions and provide personalized recommendations.

The platform currently supports six European cities: Amsterdam, Bordeaux, Crete, Lisbon, Rome, and Sicily.

---

## 1. Project Objectives

**Purpose:**  
To create an intelligent, data-driven platform that helps travelers discover and compare Airbnb listings in multiple cities using interactive maps, pricing analytics, machine learning-powered sentiment analysis, and a conversational AI travel assistant.

**SMART Objectives:**

1. **Launch MVP by January 10, 2026** with support for at least 3 cities featuring interactive map visualization, price filtering, and ML-generated word clouds from reviews. Achieved with 6 cities.

2. **Achieve 95% data processing accuracy** by implementing automated pipelines that clean, validate, and structure CSV datasets (listings, reviews, neighborhoods, calendar) into a queryable database by December 22, 2025.

3. **Deliver sub-3-second page load times** for all interactive map features and data visualizations through optimized frontend rendering and backend API responses by March 14, 2026.

4. **Integrate a RAG-powered conversational travel assistant** that leverages FAISS vector search and sentence-transformer embeddings over the full review corpus to provide context-aware, natural-language travel recommendations. Implemented in February 2026.

---

## 2. Stakeholders and Roles

**Stakeholders:**
- **End Users:** Travelers seeking data-driven accommodation insights
- **Holberton School Tirana:** Academic evaluation and Demo Day presentation
- **Development Team:** Project execution and delivery

## Team Members & Roles

**Alba Eftimi** -- Full-Stack Developer  
*Backend API development, database design, ML model integration, RAG pipeline*

**Sokol Gjeka** -- Frontend Developer  
*Interactive map implementation, UI/UX design, JavaScript visualization*

**Renis Vukaj** -- Data Engineer  
*ETL pipelines, data cleaning, CSV processing, GeoJSON integration*

**Kevin Voka** -- ML Engineer  
*Word cloud generation, sentiment analysis, NLP model training*

*All team members contribute to testing, documentation, and Demo Day presentation.*

---

## 3. Scope

### In-Scope:
- Interactive map visualization using DeckGL and MapLibre GL with scatterplot overlays, color-coded by price range
- Price analysis dashboard with neighborhood filtering, room type selection, and dual-handle price range slider
- ML-powered word clouds generated from review text using NLTK and spaCy
- Sentiment analysis of guest reviews using VaderSentiment, with per-neighborhood breakdowns (positive, neutral, negative)
- Room type distribution donut charts and occupancy rate visualizations using Recharts
- Top hosts leaderboard ranked by listing count and average rating
- RAG-powered conversational travel assistant (InnSight chatbot) using FAISS vector search, sentence-transformers embeddings, and LLM-first architecture with multi-turn conversation memory
- Support for 6 European cities: Amsterdam, Bordeaux, Crete, Lisbon, Rome, and Sicily
- Backend REST API (Flask) with Swagger documentation via flask-restx
- Database integration (MongoDB) for structured data storage with automated index creation
- Responsive web design for desktop and mobile browsers
- Contact form with Netlify Forms integration
- Informational pages: Data methodology, Technology stack overview, About the project

### Out-of-Scope:
- Real-time Airbnb booking integration
- User authentication or saved preferences
- Mobile native applications (iOS/Android)
- Payment processing or reservation systems
- Historical price trend analysis
- Host verification or review moderation
- Multi-language support beyond English
- Cities without available dataset coverage

---

## 4. Risks and Mitigation Strategies

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Data quality issues** (outdated CSV files) | High | High | Implement robust data validation pipelines; fallback to archived datasets; automated integrity checks |
| **ML model underperformance** (poor word cloud quality) | Medium | Medium | Start with pre-trained NLP models (NLTK/spaCy); iterative testing; manual review sample validation |
| **Map rendering performance** (lag with 10k+ markers) | Medium | High | Use DeckGL with WebGL-based scatterplot layers; marker clustering via deck.gl; lazy loading of map data |
| **RAG retrieval quality** (irrelevant context in chatbot responses) | Medium | Medium | Tune FAISS similarity thresholds; filter by minimum score; combine vector retrieval with structured MongoDB queries for hybrid context |
| **Scope creep** (adding features beyond objectives) | High | Medium | Strict feature freeze after Jan 10; prioritize MVP features; document Phase 2 ideas separately |
| **Team member availability** (bootcamp workload conflicts) | Medium | High | Weekly standups; clear task ownership; buffer time in timeline; parallel workstream design |

---

## 5. High-Level Plan

### Project Timeline

| Stage | Duration | Deliverables |
|-------|----------|-------------|
| **Stage 1: Team Formation and Idea Development** | Dec 1 - Dec 5, 2025 | Team assembled, project concept finalized |
| **Stage 2: Project Charter Development** | Dec 8 - Dec 12, 2025 | Project Charter |
| **Stage 3: Technical Documentation** | Dec 15 - Dec 19, 2025 | System architecture, API specs, database schema, tech stack decisions |
| **Stage 4: MVP Development and Execution** | Dec 22, 2025 - Jan 10, 2026 | Working MVP with core features: maps, pricing, ML word clouds |
| **Stage 5: Project Closure** | Jan 12 - Feb 21, 2026 | Testing, bug fixes, documentation, code cleanup, final deployment |
| **Stage 6: Landing Page** | Feb 23 - Mar 14, 2026 | Marketing landing page, Demo Day presentation materials |

### Key Milestones
- **Dec 5:** Team and concept finalized
- **Dec 12:** Project Charter approved
- **Dec 19:** Technical documentation complete
- **Jan 10:** MVP feature-complete and deployed
- **Feb 18:** RAG chatbot integrated with LLM-first architecture
- **Feb 21:** Final testing and project closure
- **Mar 14:** Landing page live and Demo Day presentation

---

## Technology Stack

### Backend
- **Framework:** Python (Flask), flask-restx (Swagger API docs), Flask-Caching, Flask-Limiter
- **Database:** MongoDB (pymongo) with automated index creation
- **Data Processing:** Pandas, NumPy
- **ML/NLP:** scikit-learn, NLTK, spaCy, VaderSentiment, langdetect, WordCloud
- **RAG Pipeline:** FAISS (faiss-cpu) for vector similarity search, sentence-transformers for text embeddings, Google Gemini API for LLM inference
- **Other:** python-dotenv, schedule, requests

### Frontend
- **Framework:** React 19 (Vite)
- **Routing:** react-router-dom
- **Maps:** DeckGL (WebGL scatterplots), MapLibre GL, react-map-gl, Leaflet (react-leaflet)
- **Charts:** Recharts
- **HTTP Client:** Axios
- **Styling:** Vanilla CSS (modular: base, city, landing, pages, chat)

---

## Project Structure

```
InnSight/
  backend/
    app.py                  # Flask app factory
    config.py               # Centralized configuration (cities, DB, etc.)
    run.py                  # Development server entry point
    routes/                 # API endpoints
      analytics.py          #   GET /api/analytics
      chat.py               #   POST /api/chat
      cities.py             #   GET /api/cities
      listings.py           #   GET /api/listings, /api/listings-map
      neighborhoods.py      #   GET /api/neighborhoods
      neighborhood_sentiment.py
      occupancy_stats.py
      reviews_sentiment.py
      room_type_distribution.py
      sentiment_summary.py
      top_hosts_route.py
    services/
      chat_rag.py           # LLM-first RAG chatbot logic
      city_tags.py           # City tag extraction
      travel_planner.py      # Structured recommendation builder
    rag/
      embeddings.py          # Sentence-transformer model loading
      ingest.py              # FAISS index builder from reviews/guides
      retriever.py           # Vector similarity search
      vector_store.py        # FAISS index management
    tests/
      full_test.sh           # API integration tests
  frontend/
    src/
      main.jsx              # App entry point, CSS imports
      App.jsx               # Router and layout
      api/
        chat.js             # Chat API client
      components/
        ChatPanel.jsx       # Chat UI with conversation history
        ChatWidget.jsx      # Floating chat FAB + window
        ChatMessage.jsx     # Individual chat bubble
        CityCard.jsx        # City grid card
        DashboardPanel.jsx  # Right-side dashboard on city page
        MapPanel.jsx        # DeckGL + MapLibre map
        MapLegend.jsx       # Price range legend
        MonthPicker.jsx     # Month selection modal
        NeighborhoodFilter.jsx
        charts/
          OccupancyCard.jsx
          RoomTypesCard.jsx
          SentimentCard.jsx
          TopHostsCard.jsx
        Layout/
          Header.jsx
          Footer.jsx
      pages/
        Landing.jsx         # Home page with hero and city grid
        City.jsx            # City detail: map + dashboard
        Data.jsx            # Data methodology page
        Technology.jsx      # Technology stack page
        About.jsx           # About the project
        Contact.jsx         # Contact form (Netlify)
        NotFound.jsx        # 404 page
      styles/
        base.css            # Global resets, layout, grids, cards, buttons
        city.css            # City page panels, charts, map, filters
        landing.css         # Hero, sections, how-it-works
        pages.css           # Data, Tech, About, Contact, Team styles
        chat.css            # Chat widget, window, bubbles
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

The API server starts at `http://localhost:5000`. Swagger documentation is available at `/api/docs`.

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The development server starts at `http://localhost:5173`.

### RAG Pipeline (optional)
To build the FAISS vector index for the chatbot:
```bash
cd backend
python -m rag.ingest
```
This processes all reviews and text guides into a searchable vector store. The chatbot will function without it but will not have RAG context for its responses.

---

<h2 align="center">License</h2>

This project is for educational purposes only and is part of the **Holberton School** / **Foundations of Computer Science** curriculum.

---

<h2 align="center">Authors</h2>

<p>
  <strong>Alba Eftimi</strong> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <strong>Sokol Gjeka</strong> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <strong>Renis Vukaj</strong> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <strong>Kevin Voka</strong>

  GitHub: <a href="https://github.com/abfabs">abfabs</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  GitHub: <a href="https://github.com/sokolgj19">sokolgj19</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  GitHub: <a href="https://github.com/renisv">renisv</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  GitHub: <a href="https://github.com/kevin10v">kevin10v</a>
</p>

<p align="center">
  <em>December 2025 - February 2026</em><br>
  <em>Tirana, Albania</em>
</p>