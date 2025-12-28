# Uni-Link

## Overview
Uni-Link is a social networking React application for connecting users, with features including authentication, user profiles, posts, friends, notifications, and chat functionality.

## Project Structure
- `client/` - React frontend application (Create React App)
  - `src/components/` - Reusable UI components
  - `src/scenes/` - Page-level components (routes)
  - `src/context/` - React context providers
  - `src/state/` - Redux state management
  - `src/config/` - API configuration

## Tech Stack
- React 18
- Redux Toolkit for state management
- React Router for navigation
- Tailwind CSS for styling
- Styled Components

## Development
The frontend runs on port 5000 via the "React Frontend" workflow.

## Backend API
This frontend connects to an external backend API configured via `REACT_APP_API_URL` environment variable (defaults to `http://localhost:3001`).

## Deployment
Configured for static deployment - builds the React app and serves the `client/build` directory.
