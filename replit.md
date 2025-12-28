# UniLink - Professional University Community

## Overview
UniLink is a modern React-based social networking application for university communities with a sleek, LinkedIn-inspired design. Features user authentication, posts/feeds, chat messaging, notifications, and professional networking.

## Recent Changes (UI Redesign)
- **Modern Color Scheme**: Transitioned from grey palette to blue/slate/indigo gradients
- **Enhanced Typography**: Larger, bolder headlines with gradient text effects
- **Modernized Cards**: Rounded corners (2xl), shadow effects, backdrop blur, better spacing
- **Refined Navigation**: Sleek navbar with gradient logo, improved active state indicators
- **Professional Login**: Hero section with feature cards, gradient backgrounds, smooth animations
- **Glass Morphism**: Subtle backdrop blur effects and transparent backgrounds throughout
- **Improved Buttons**: Gradient backgrounds, better hover states, shadow effects

## Project Structure
- `client/` - React frontend (Create React App)
  - `src/components/` - Reusable UI components (WidgetWrapper, UserWidget, etc.)
  - `src/scenes/` - Page-level components (homePage, loginPage, profilePage, etc.)
  - `src/context/` - React context providers (Chat, Notifications)
  - `src/state/` - Redux store configuration
  - `src/config/api.js` - API endpoint configuration

## Tech Stack
- React 18 with Create React App
- Redux Toolkit for state management
- TailwindCSS for modern styling
- Framer Motion for animations
- Lucide React for icons
- Material-UI for some components
- Socket.io-client for real-time features

## Design Features
- **Gradient Accents**: Blue-to-indigo gradients for modern look
- **Dark Mode Support**: Full dark mode with appropriate color variants
- **Responsive Design**: Mobile-first, works on all screen sizes
- **Smooth Animations**: Fade-ins, transitions, and hover effects
- **Professional Shadows**: Modern shadow depth for better hierarchy
- **Glass Effects**: Subtle blur and transparency effects

## Development
Frontend runs on port 5000 in development:
```bash
cd client && npm start
```

## Environment Variables
- `REACT_APP_API_URL` - Backend API URL (defaults to http://localhost:3001)

## Deployment
Configured for static deployment:
- **Target**: Static site
- **Build**: `cd client && npm run build`
- **Public Directory**: `client/build`

## Notes
- Login page: Modern hero layout with features section
- Navigation: Sleek top bar with improved styling
- Cards: All widgets use new rounded corners and shadow system
- Colors: Blue (#0A66C2 primary), Slate greys for neutral tones
- The design maintains professional appearance while being modern and stylish
