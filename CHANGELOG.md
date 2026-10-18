# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-18

### Added
- Automated WhatsApp webhook catalog extraction powered by LangChain and Groq LLM.
- PostgreSQL database persistence with SQLAlchemy ORM and schema migration support.
- Multi-aspect CI validation including linting, unit test coverage, and container build smoke testing.
- Hardened HTTP security headers and CORS origin filtering middleware.
- Centralized exception boundary and structured JSON health probe endpoints.
- Single-command Makefile workflow for local testing, linting, formatting, and running.
- Semantic release tagging and automated weekly Dependabot scanning.
