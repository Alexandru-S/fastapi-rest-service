# Example FastAPI + Next.js + Postgres Service

### The project includes:
- FastAPI
- Next.JS
- PostreSQL

The repo is an example project that connects a FastAPI backend and a Next.js frontend to a Postgres database. The app pulls data from the Rick and Morty API, stores it in Postgres, and exposes it through a FastAPI service that the frontend consumes.

## Overview

The app centers on creating hotels and assigning characters to them:

- The frontend fetches a list of characters from the Rick and Morty API.
- Users can create a hotel associated with a location that is also pulled from the API.
- Users can select characters from the list and add them to a hotel.
- All data is saved and persisted in Postgres.
- Data flows through the FastAPI service,

## Why FastAPI, Next.js, and Postgres

These technologies were chosen because they are popular, easy to use, and open source:

- **FastAPI**: a modern, high-performance Python framework with excellent developer ergonomics.
- **Next.js**: a flexible React framework with a strong developer experience and a large ecosystem.
- **Postgres**: a reliable, widely adopted relational database with powerful features and strong community support.


