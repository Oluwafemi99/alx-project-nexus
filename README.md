# ALX Project Nexus — E-commerce Backend Platform

**ALX Project Nexus** is a robust, scalable e-commerce backend built with Django and Django REST Framework. Designed as part of the ALX Software Engineering program, this project powers core functionalities for online retail platforms — from user authentication and product management to order processing and asynchronous task handling.

---

## What is Project Nexus?

Project Nexus is the engine behind a modern e-commerce experience. It provides:

**User Authentication & Profiles** — Secure login with JWT, user roles, and profile management
**Product Catalog API** — Create, update, and browse products with categories and inventory tracking
**Order Management** — Place orders, track status, and manage payments
**Email Notifications** — Send order confirmations and alerts via Celery tasks
**Scheduled Jobs** — Auto-clear abandoned carts, send promotional emails, and sync inventory
**RESTful API** — Clean endpoints for frontend integration (React, Vue, mobile apps)
**Swagger/OpenAPI** — Interactive API docs for developers
**Cloud Deployment** — Hosted on Render with PostgreSQL and Redis

---

## Tech Stack

| Layer         | Technology                     |
|---------------|--------------------------------|
| Backend       | Django 4.2, Django REST Framework |
| Auth          | JWT via `djangorestframework-simplejwt` |
| Task Queue    | Celery                         |
| Scheduler     | Celery Beat + `django-celery-beat` |
| Cache/Broker  | Redis                          |
| Database      | PostgreSQL                     |
| Deployment    | Render                         |
| Docs          | Swagger (via `drf-yasg`)       |

---

## 🛒 Core Features

- **User Registration & Login**
- **Product Listings & Categories**
- **Cart & Checkout APIs**
- **Order History & Status Tracking**
- **Admin Dashboard (via Django Admin)**
- **Background Tasks for Email & Inventory**
- **Secure Token-based Authentication**

---

## 🚦 API Endpoints

| Method | Endpoint                  | Description                  |
|--------|---------------------------|------------------------------|
| POST   | `/api/token/`             | Obtain JWT token             |
| GET    | `/api/products/`          | List all products            |
| POST   | `/api/orders/`            | Place a new order            |
| GET    | `/api/user/detail/<uuid>/`| Retrieve user details        |

> Full API documentation available at `/swagger/` once deployed.

---

## 🧪 Running Locally

```bash
# Clone the repo
git clone https://github.com/yourusername/alx-project-nexus.git
cd alx-project-nexus

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver


Deployment on Render

Render uses render.yaml to configure services:

Web Service: Django + Gunicorn

Worker Service: Celery

Beat Service: Celery Beat

Redis: Broker and cache

PostgreSQL: Database

Author: Oluwafemi Dojumo  ALX Software Engineering Program Lagos, Nigeria


## Key Technologies Covered

1. Python

- Mastered core programming concepts, including OOP, error handling, and testing.
- Learned to write clean, modular, and maintainable code.

2. Django

- Built custom user models, authentication, and role-based access.
- Explored Django ORM for database queries and migrations.
- Django REST Framework (DRF)
- Designed RESTful APIs with serializers, viewsets, and routers.
- Implemented authentication and authorization with JWT.

3. GraphQL

- Set up schemas, queries, and mutations.
- Compared REST and GraphQL for flexibility and performance.

4. Docker

- Containerized applications for consistent development and deployment.
- Created Dockerfile and docker-compose.yml for services, including web and database.

5. CI/CD

- Implemented Git workflows, including feature branches and pull requests.
- Automated testing and deployments using GitHub Actions.

## Important Backend Development Concepts 

1. Database Design
- Learned about normalization and relationships like one-to-many and many-to-many.

- Applied indexing to improve performance.

2. Asynchronous Programming
- Worked with async and await in Python.

3. Integrated Celery and Rabbitmq for background tasks, such as sending emails.

4. Caching Strategies
- Implemented Redis for query caching.
- Applied caching at both the view and database levels to reduce latency.

## Challenges Faced and Solutions Implemented

1. Handling Circular Imports in Django
Solution: Refactored code into modular apps and used get_user_model() to avoid hard dependencies.

2. Managing State Across Containers
Solution: Used Docker volumes for persistent database storage.

3. Slow Queries on Large Tables
Solution: Added indexes and optimized ORM queries with .select_related() and .prefetch_related().

4. Debugging Authentication Issues with JWT
Solution: Managed token refresh and blacklist carefully, and wrote tests for edge cases.

5. CI/CD Failures Due to Environment Variables
Solution: Used .env files with GitHub Secrets to store and inject configs securely.

## Best Practices and Personal Takeaways

1. Code Quality
- Followed PEP8 guidelines and enforced linting and type hints.
- Practiced writing unit tests and integration tests for reliability.

2. Security First
- Used environment variables for secrets.
- Applied input validation and permissions at both the model and view levels.

3. Scalability Mindset
- Designed APIs to be stateless and modular.
- Used caching and async tasks for high-performance applications.

4. Collaboration and Workflow
- Adopted GitFlow for structured branching.
- Understood the importance of CI/CD in reducing deployment risks.

5. Personal Growth
- Learned to think like a problem-solver, not just a coder.
- Gained confidence in deploying real-world apps from start to finish.