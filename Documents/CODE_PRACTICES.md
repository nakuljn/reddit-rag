# Code Architectural Practices & Principles

This document tracks the architectural and coding principles followed in the Reddit-Powered LLM project. It serves as a reference for current and future contributors to ensure code quality and maintainability.

---

## Core Principles

### 1. SOLID Principles
- **Single Responsibility Principle (SRP):**
  - Each module and function is designed to do one thing well (e.g., ingestion, search, LLM integration are separate modules).
  - Functions like `fetch_top_posts()`, `search_similar_documents()`, `generate_response()` have clear, single purposes.
- **Open/Closed Principle (OCP):**
  - Code is written to be easily extended (e.g., new ingestion sources, new LLMs) without modifying existing logic.
  - LLMService can be extended to support different models without changing core logic.
- **Liskov Substitution Principle (LSP):**
  - Interfaces and abstractions (where used) allow for safe substitution (e.g., LLM service can be swapped from OpenAI to Claude).
- **Interface Segregation Principle (ISP):**
  - Functions and classes expose only the methods needed for their role, avoiding "fat" interfaces.
  - Pydantic models only include fields relevant to their specific use case.
- **Dependency Inversion Principle (DIP):**
  - High-level modules do not depend on low-level modules; both depend on abstractions (e.g., use of environment variables, dependency injection for clients).

### 2. DRY (Don't Repeat Yourself)
- Common logic (e.g., Reddit client creation, document structuring) is centralized in utility functions.
- Tests use fixtures and mocks to avoid duplication.
- Pydantic models provide reusable validation patterns.

### 3. KISS (Keep It Simple, Stupid)
- Code is written for clarity and simplicity, avoiding unnecessary abstraction or complexity.
- MVP-first approach: only build what is needed for the current feature set.
- Direct function calls instead of complex dependency injection frameworks.

### 4. YAGNI (You Aren't Gonna Need It)
- Features and abstractions are only added when there is a clear, immediate need.
- Avoid premature optimization and over-engineering.
- Simple mocking in tests instead of complex test frameworks.

---

## Current Practices in This Project

### Architecture Patterns
- **Modular Structure:** Each major concern (ingestion, search, LLM, API) is in its own module.
- **Service Layer Pattern:** LLMService encapsulates OpenAI integration logic.
- **Repository Pattern:** Vector store operations are abstracted in vector_store.py.
- **API Layer Pattern:** FastAPI endpoints with Pydantic models for validation.

### Code Quality Standards
- **Type Hints & Docstrings:** All public functions and classes use type hints and docstrings for clarity.
- **Environment Variables:** Secrets and configuration are managed via environment variables and .env files.
- **Testing:** All new logic is covered by unit tests, with mocks for external dependencies.
- **Error Handling:** Functions raise clear exceptions for missing configuration or invalid input. All modules now handle edge cases and failures gracefully, returning user-friendly errors.
- **Readability:** Code is formatted and commented for easy understanding by new contributors.

### Testing Strategy
- **Unit Tests:** Each module has comprehensive unit tests with mocked external dependencies.
- **Mocking:** External APIs (Reddit, OpenAI, ChromaDB) are mocked to ensure fast, reliable tests.
- **Validation Testing:** API endpoints are tested for both success and error cases.
- **Edge Case Coverage:** Tests cover invalid input, network/API failures, empty results, and error propagation.
- **Test Coverage:** All critical paths are covered with meaningful assertions.

### API Design
- **RESTful Endpoints:** Clear, predictable API structure (GET /, POST /search, POST /ask).
- **Request/Response Models:** Pydantic models ensure type safety and automatic validation.
- **Error Handling:** Proper HTTP status codes and descriptive error messages. All endpoints now handle service failures and validation errors robustly.
- **Documentation:** FastAPI auto-generates API documentation from type hints.

---

## Recent Improvements & Fixes (July 2025)

### Data Validation & Type Safety
- **Metadata Type Conversion:** All PRAW objects are converted to proper Python types (str, int) before storing in ChromaDB
- **Flexible Content Handling:** Posts without selftext are handled gracefully (common in r/askreddit)
- **Environment Variable Validation:** Robust checking for required API credentials

### Error Handling Enhancements
- **Graceful Degradation:** System continues to function even when some posts/comments are invalid
- **Clear Error Messages:** User-friendly error messages for missing credentials or API failures
- **Data Integrity:** Validation ensures only properly formatted data reaches the vector store

### Development Environment
- **Python Version Management:** Consistent use of Python 3.11 across development and production
- **Virtual Environment Isolation:** Proper dependency management with requirements.txt
- **Package Version Control:** Specific version pinning to prevent compatibility issues

---

## Best Practices for Future Development

### Adding New Features
1. **Start with Tests:** Write tests first to define expected behavior
2. **Handle Edge Cases:** Consider empty data, network failures, and invalid inputs
3. **Validate Data Types:** Ensure all data passed to external services is properly typed
4. **Update Documentation:** Keep this document and code comments current

### Code Review Checklist
- [ ] Type hints present on all public functions
- [ ] Docstrings explain purpose and parameters
- [ ] Error handling covers expected failure modes
- [ ] Tests cover success and failure scenarios
- [ ] No hardcoded secrets or configuration
- [ ] Code follows existing patterns and conventions

### Performance Considerations
- **Batch Processing:** Use batch operations for ChromaDB when possible
- **Lazy Loading:** Only fetch data when needed
- **Connection Pooling:** Reuse API clients where appropriate
- **Memory Management:** Process large datasets in chunks

---

## To Review/Improve
- As the project grows, periodically review for code duplication, unnecessary complexity, or violation of these principles.
- Encourage all contributors to read and update this document as practices evolve.
- Consider adding integration tests for end-to-end workflows.
- Monitor test execution time and optimize slow tests.
- Continue to expand edge case coverage as new features are added.
- Regular dependency updates to maintain security and compatibility. 