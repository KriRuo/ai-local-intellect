
# Welcome to your Lovable project - AI Insight Tracker

## Project info

**URL**: https://lovable.dev/projects/a341bdf5-2167-49a7-9478-5c23b96be870

## Project Overview

AI Insight Tracker is a local-first AI news aggregator application that helps users stay up-to-date with the latest developments in artificial intelligence. The application features a news feed and an AI assistant to help users understand the content.

## Current Status & Roadmap

### Original MVP Requirements
- ✅ News feed displaying AI-related articles
- ✅ Basic AI assistant integration
- ✅ Responsive design for mobile and desktop
- ✅ Apple-inspired minimalist UI with light grey and blue tones

### In Progress
- 🚧 Article loading and error handling improvements
- 🚧 Enhanced UI styling and visual feedback
- 🚧 Chat functionality refinements

### Planned Features
- 📋 User authentication
- 📋 Article bookmarking/saving
- 📋 Categorized news feed
- 📋 Advanced search and filtering
- 📋 Personalized news recommendations
- 📋 Offline support
- 📋 Integration with multiple AI news sources

## Architecture

### Application Structure

```
src/
├── components/          # UI components
│   ├── ui/              # Shadcn UI components
│   ├── Layout.tsx       # Main layout wrapper
│   ├── PostCard.tsx     # Article card display
│   ├── PostsFeed.tsx    # News feed container
│   ├── ChatBox.tsx      # AI assistant interface
│   └── ThemeToggle.tsx  # Dark/light mode switcher
├── hooks/               # Custom React hooks
│   ├── use-mobile.tsx   # Responsive design detection
│   ├── use-theme.tsx    # Theme management
│   └── use-toast.ts     # Toast notification hook
├── lib/                 # Utilities and services
│   ├── api.ts           # API communication
│   ├── store.ts         # State management (Zustand)
│   └── utils.ts         # Helper functions
├── pages/               # Page components
│   ├── Index.tsx        # Home page
│   └── NotFound.tsx     # 404 page
└── main.tsx             # Application entry point
```

### State Management

- **Zustand Store**: Centralized state management using Zustand for both posts and chat data
- State is divided into two main domains:
  - `posts`: Manages article data, loading states, and error handling
  - `chat`: Manages conversation messages, loading states, and error handling

### Data Flow

1. **API Layer**: 
   - `api.ts` handles all external data fetching with error handling
   - Fallback to mock data when API is unavailable
   - Relative API paths for deployment flexibility

2. **Component Layer**:
   - Components consume state from Zustand store
   - UI updates based on loading/error states
   - Toast notifications for user feedback

3. **Responsive Design**:
   - Adaptive layout based on device size
   - Tab-based navigation on mobile
   - Grid-based layout on desktop

### Technical Implementation
- React with TypeScript for frontend development
- Tailwind CSS for styling with custom Apple-inspired design system
- shadcn-ui component library for consistent UI elements
- Responsive layout using CSS grid and flexbox
- Tabs interface for mobile view to switch between news and chat
- Toast notifications for user feedback
- Light/dark theme support

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/a341bdf5-2167-49a7-9478-5c23b96be870) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/a341bdf5-2167-49a7-9478-5c23b96be870) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)

