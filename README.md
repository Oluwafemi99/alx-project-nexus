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