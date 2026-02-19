# Todo AI Chatbot Frontend

AI-powered chatbot interface for managing todos through natural language using OpenAI ChatKit.

## Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

## Setup Instructions

### 1. Install Dependencies

```bash
cd chatbot-frontend
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file:

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here  # Optional for local dev
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

## OpenAI ChatKit Setup (Production)

To use the hosted ChatKit option in production, you must configure the domain allowlist:

### 1. Deploy Your Frontend

Deploy to Vercel, GitHub Pages, or your custom domain to get a production URL.

### 2. Add Domain to OpenAI Allowlist

1. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add domain"
3. Enter your frontend URL (without trailing slash)
4. Save changes

### 3. Get Domain Key

After adding the domain, OpenAI will provide a domain key. Add it to your environment:

```env
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
```

**Note:** Local development (`localhost`) typically works without domain allowlist configuration.

## Project Structure

```
chatbot-frontend/
├── app/                    # Next.js app router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page with chat
│   └── globals.css        # Global styles
├── components/            # React components
│   └── ChatInterface.tsx  # Main chat UI
├── lib/                   # Utility functions
│   └── api.ts            # API client
├── package.json          # Dependencies
└── README.md            # This file
```

## Features

- **Natural Language Commands**: Add, list, complete, update, and delete tasks
- **Conversation History**: Persistent chat sessions
- **Real-time Responses**: Streaming AI responses
- **Tool Call Indicators**: See which tools the AI used
- **Responsive Design**: Works on desktop and mobile

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Natural Language Commands

The chatbot understands these commands:

| User Says | Agent Action |
|-----------|--------------|
| "Add a task to buy groceries" | Creates new task |
| "Show me all my tasks" | Lists all tasks |
| "What's pending?" | Lists pending tasks |
| "Mark task 3 as complete" | Marks task as done |
| "Delete the meeting task" | Deletes task after confirmation |
| "Change task 1 to 'Call mom tonight'" | Updates task |
| "I need to remember to pay bills" | Creates task |
| "What have I completed?" | Lists completed tasks |

## Technology Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Chat UI**: OpenAI ChatKit / Custom Interface
- **HTTP Client**: Native fetch

## Architecture Benefits

| Aspect | Benefit |
|--------|---------|
| **MCP Tools** | Standardized interface for AI to interact with your app |
| **Single Endpoint** | Simpler API — AI handles routing to tools |
| **Stateless Server** | Scalable, resilient, horizontally scalable |
| **Tool Composition** | Agent can chain multiple tools in one turn |

## Troubleshooting

### Connection Error
If you see "I'm having trouble connecting", ensure:
- Backend API is running on http://localhost:8000
- CORS is configured properly in backend

### ChatKit Domain Error
If you see domain-related errors:
- For local dev: Remove `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` from `.env.local`
- For production: Ensure domain is added to OpenAI allowlist

## Deployment

### Vercel (Recommended)

```bash
npm i -g vercel
vercel
```

Add environment variables in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` - Your backend API URL
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` - Your OpenAI domain key

## License

MIT
