# InnSight - Smart Airbnb Explorer

## Table of Contents
- [Project Charter](#project-charter)
- [1. Project Objectives](#1-project-objectives)
- [2. Stakeholders and Roles](#2-stakeholders-and-roles)
- [3. Scope](#3-scope)
- [4. Risks and Mitigation Strategies](#4-risks-and-mitigation-strategies)
- [5. High-Level Plan](#5-high-level-plan)
- [Technology Stack](#technology-stack)
- [License](#license)
- [Authors](#authors)

---

## Project Charter

### Project Overview
InnSight is an interactive data visualization platform designed to help travelers make smarter, more informed decisions when choosing where to stay. Planning a trip can be overwhelming, especially when you're trying to figure out which neighborhood fits your vibe, what's a fair price, or whether other travelers actually enjoyed their experience. That's where InnSight comes in.

By combining geographic mapping, pricing analysis, and machine learning-powered sentiment analysis of guest reviews, InnSight transforms raw Airbnb data into clear, actionable insights. Instead of endlessly scrolling through listings or reading hundreds of reviews, travelers can explore cities visually, compare neighborhoods at a glance, and understand the true character of an area through data-driven word clouds and sentiment scores.

While other platforms focus on the socioeconomic impacts of short-term rentals, InnSight is built for the traveler. Whether you're on a tight budget looking for the best deal, seeking a lively nightlife district, or hunting for a quiet residential area to unwind, InnSight gives you the tools to find your perfect match based on real data from real guests.

---

## 1. Project Objectives

**Purpose:**  
To create an intelligent, data-driven platform that helps travelers discover and compare Airbnb listings in multiple cities using interactive maps, pricing analytics, and machine learning-powered sentiment analysis.

**SMART Objectives:**

1. **Launch MVP by January 10, 2026** with support for at least 3 cities (Amsterdam, Prague, and Rome), featuring interactive map visualization, price filtering and ML-generated word clouds from reviews.

2. **Achieve 95% data processing accuracy** by implementing automated pipelines that clean, validate, and structure CSV datasets (listings, reviews, neighborhoods, calendar) into a queryable database by December 22, 2025.

3. **Deliver sub-3-second page load times** for all interactive map features and data visualizations through optimized frontend rendering and backend API responses by March 14, 2026.

---

## 2. Stakeholders and Roles

**Stakeholders:**
- **End Users:** Travelers seeking data-driven accommodation insights
- **Holberton School Tirana:** Academic evaluation and Demo Day presentation
- **Development Team:** Project execution and delivery

## Team Members & Roles

**Alba Eftimi** — Full-Stack Developer  
*Backend API development, database design, ML model integration*

**Sokol Gjeka** — Frontend Developer  
*Interactive map implementation, UI/UX design, JavaScript visualization*

**Renis Vukaj** — Data Engineer  
*ETL pipelines, data cleaning, CSV processing, GeoJSON integration*

**Kevin Voka** — ML Engineer  
*Word cloud generation, sentiment analysis, NLP model training*

*All team members contribute to testing, documentation, and Demo Day presentation.*

---

## 3. Scope

### In-Scope:
- Interactive map visualization using D3.js and Chart.js with overlays
- Price analysis dashboard with filters (by area, property type, date range)
- ML-powered word clouds generated from review text
- Support for 3-5 major cities with comprehensive listing data
- Backend REST API (Flask) serving listing and review data
- Database integration (NoSQL/MongoDB) for structured data storage
- Responsive web design for desktop and mobile browsers
- Search and filter functionality (price range, ratings)
- Neighborhood vibe scores calculated from review sentiment

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
| **Map rendering performance** (lag with 10k+ markers) | Medium | High | Implement marker clustering; lazy loading; optimize GeoJSON file sizes; use CDN for static assets |
| **Scope creep** (adding features beyond objectives) | High | Medium | Strict feature freeze after Jan 10; prioritize MVP features; document Phase 2 ideas separately |
| **Team member availability** (bootcamp workload conflicts) | Medium | High | Weekly standups; clear task ownership; buffer time in timeline; parallel workstream design |
| **Holiday season delays** (December break) | High | Medium | Front-load critical work in December; async communication protocols; flexible deadline buffers |

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
- **Feb 21:** Final testing and project closure
- **Mar 14:** Landing page live and Demo Day presentation

---

## Technology Stack

- **Backend:** Python (Flask), Pandas
- **Frontend:** JavaScript (React), D3.js, Chart.js
- **Database:** NoSQL (MongoDB)
- **ML/NLP:** Word cloud generation, sentiment analysis  
- **Data:** CSV datasets (listings, reviews, calendar)

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
  <em>December 2025</em><br>
  <em>Tirana, Albania</em>
</p>