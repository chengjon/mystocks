# Technology Stack: MyStocks

## 1. Overview

The MyStocks project is built upon a modern, high-performance, and scalable technology stack designed to handle the complexities of quantitative trading data management and real-time processing. This stack combines robust backend services, a dynamic frontend, specialized databases, and GPU acceleration for demanding computational tasks.

## 2. Core Technologies

*   **Programming Languages:**
    *   **Python:** Primary language for backend services, data processing, machine learning, and GPU acceleration.
    *   **JavaScript/TypeScript:** Used for the interactive and dynamic frontend web application.

*   **Backend Frameworks:**
    *   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It is chosen for its excellent performance, automatic interactive API documentation (Swagger UI), and asynchronous capabilities.

*   **Frontend Frameworks:**
    *   **Vue 3:** A progressive JavaScript framework for building user interfaces. It's selected for its reactivity system, component-based architecture, and performance.
    *   **Element Plus UI:** A Vue 3 compatible UI component library that provides a rich set of customizable and high-quality UI components, ensuring a consistent and visually appealing user experience.

*   **Databases:**
    *   **TDengine:** A purpose-built time-series database optimized for high-frequency data ingestion and query. It is utilized for storing Tick data, minute K-lines, and other high-volume time-series market data due to its extreme compression ratio and superior write performance.
    *   **PostgreSQL with TimescaleDB:** PostgreSQL serves as the primary relational database, extended with TimescaleDB for advanced time-series analysis capabilities. It handles historical K-line data (daily, weekly, monthly), reference data (e.g., stock information), derived data (e.g., technical indicators, quantitative factors), transaction data, metadata, and monitoring data, providing strong ACID compliance and complex query support.

*   **GPU Acceleration:**
    *   **RAPIDS (cuDF, cuML, CuPy):** A suite of open-source software libraries and APIs that gives you the ability to execute end-to-end data science and analytics pipelines entirely on GPUs. This is critical for accelerating computationally intensive tasks such as backtesting, machine learning model training, and large-scale data processing.

## 3. Infrastructure & DevOps

*   **Docker:** Containerization platform used for packaging applications and their dependencies, ensuring consistency across different environments.
*   **Kubernetes:** An open-source container orchestration system for automating deployment, scaling, and management of containerized applications.
*   **Redis Streams:** Utilized as a message broker for high-throughput, low-latency inter-service communication and real-time data streaming.
*   **Prometheus:** An open-source monitoring system with a flexible query language (PromQL) used for collecting and storing time-series metrics.
*   **Grafana:** An open-source platform for monitoring and observability, used for visualizing the data collected by Prometheus and other sources, creating interactive dashboards for system health and performance.

## 4. Development & Utility Libraries

*   **schedule:** Python library for in-process scheduling of jobs.
*   **loguru:** A Python logging library designed to be simple and powerful.
*   **ujson:** An ultra-fast JSON encoder and decoder for Python.
*   **numba:** A JIT compiler for Python that translates Python code into optimized machine code.
*   **cachetools:** A collection of memoizing decorators and tools for caching in Python.
