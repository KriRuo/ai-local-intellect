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

## Backend Setup & Usage

The backend is a FastAPI application that provides the API for news aggregation and scraping. To run the backend locally:

```sh
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

See `backend/README.md` for more details on backend setup, development, and API usage.

## Environment Variables

- `VITE_API_URL`: The base URL for the backend API (e.g., `http://localhost:8081`). Set this in your `.env` or via your deployment environment.
- The backend may use additional environment variables for database configuration, etc. See `backend/README.md` for details.

## Backend API Endpoints (Summary)

- `GET /api/posts` — Get all posts
- `GET /api/rss-sources` — Get all RSS sources
- `GET /api/rss-runs` — Get recent RSS scrape runs
- `GET /api/scrape/rss` — Scrape an RSS feed (query params: url, source, platform)
- `POST /api/scrape/rss/save` — Scrape and save an RSS feed (JSON body)
- `POST /api/scrape/rss/trigger` — Trigger the RSS scraping script
- `GET /api/scrape/substack` — Scrape a Substack feed (query param: url)
- `POST /api/scrape/substack/save` — Scrape and save a Substack feed (JSON body)
- `GET /health` — Health check endpoint

See `backend/README.md` for full details and request/response formats.

## Frontend-Backend Integration

- The frontend communicates with the backend via the API endpoints above.
- The health check endpoint (`/health`) is used to display backend status in the UI.
- News posts, sources, and chat features rely on backend data.
- If the backend is offline, the frontend may fall back to mock data or display an error.

## Frontend Test Coverage

The project includes basic smoke tests for the main pages and layout. These tests ensure that the application renders without crashing and that key UI elements are present. All tests are located in `src/_tests_/`.

**Current Coverage:**
- `App.test.tsx`: Verifies the root App component renders and shows the dashboard by default.
- `Dashboard.test.tsx`: Checks the Dashboard page renders and displays the "most recent news" heading.
- `Preferences.test.tsx`: Ensures the Preferences page renders and shows a loading state.
- `SavedContent.test.tsx`: Confirms the Saved Content page renders and displays the heading.
- `Layout.test.tsx`: Verifies the Layout component renders its children.

**Limitations:**
- No tests for user interactions, error states, or edge cases.
- No unit tests for utility functions or custom hooks.
- No API mocking or async data loading tests.

**Recommendations:**
- Add tests for user interactions (e.g., button clicks, form submissions).
- Test error and empty states.
- Add unit tests for utility functions and hooks.
- Mock API calls to test data loading and error handling.

To run the frontend tests:
```sh
npm test
```

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/a341bdf5-2167-49a7-9478-5c23b96be870) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)

## Model Setup

The application uses the Sentence Transformers model for text embeddings. The model files are stored in a dedicated directory:

- Windows: `%USERPROFILE%\.ai-local-intellect\models`
- Linux/Mac: `~/.ai-local-intellect/models`

The first time you run the application, it will automatically download the required model files (about 90MB).

### Virtual Environment

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

This setup provides several benefits:

1. Model files are stored in a user-specific location, not in the repository
2. The virtual environment keeps dependencies isolated
3. The model cache is shared between different projects using the same models
4. Git won't track large model files
5. Easy to clear cache if needed (just delete the .ai-local-intellect directory)

Would you like me to help you implement these changes? We can also add some utility scripts to manage the model cache (download, clear, etc.) if you'd find that helpful.

