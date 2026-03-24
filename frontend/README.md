# IntelliLearn AI - React Frontend

Modern React frontend for the IntelliLearn AI platform built with:
- **React 18** + **TypeScript**
- **Vite** for fast development
- **TailwindCSS** for styling
- **React Router** for navigation
- **Recharts** for data visualization
- **Axios** for API calls

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
copy .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Build for Production

```bash
npm run build
```

## Features

- **Modern UI**: Clean, gradient-based design with Tailwind CSS
- **Employee Management**: View and manage employee profiles
- **Skill Analysis**: Visualize skills and identify gaps
- **AI Assistant**: Chat interface for personalized guidance  
- **Course Recommendations**: AI-powered learning paths
- **Analytics Dashboard**: ROI tracking and workforce readiness
- **Admin Panel**: Data import and model training

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page components
│   ├── lib/             # Utilities and API client
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── public/              # Static assets
└── package.json         # Dependencies
```
