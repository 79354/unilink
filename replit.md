# UniLink - Professional University Community

## Overview
UniLink is a React-based social networking application for university communities. It provides features for user authentication, posts/feeds, chat messaging, notifications, and friend connections.

## Project Structure
- `client/` - React frontend application (Create React App)
  - `src/components/` - Reusable UI components (ChatInterface, NotificationBell, etc.)
  - `src/scenes/` - Page-level components (homePage, loginPage, profilePage, etc.)
  - `src/context/` - React context providers for chat and notifications
  - `src/state/` - Redux store configuration
  - `src/config/api.js` - API endpoint configuration

## Tech Stack
- React 18 with Create React App
- Redux Toolkit for state management
- Material-UI (MUI) for components
- Framer Motion for animations
- Tailwind CSS for styling
- Socket.io-client for real-time features

## Development
The frontend runs on port 5000:
```bash
cd client && npm start
```

## Environment Variables
- `REACT_APP_API_URL` - Backend API URL (defaults to http://localhost:3001)

## Deployment
Configured for static deployment with build output in `client/build`.
