# AI Chat Assistant

A full-stack AI-powered chat assistant built with React, FastAPI, and OpenAI.

## Features

- Real-time chat interface with WebSocket support
- OpenAI API integration for AI responses
- Conversation history tracking with database storage
- Modern UI with responsive design

## Project Structure

```
ai-chat-assistant/
├── backend/
│   ├── app.py           # FastAPI application
│   ├── database.py      # Database models and setup
│   └── .env             # Environment variables (not included in repo)
├── src/                 # React frontend
│   ├── components/      # UI components
│   ├── pages/           # Page components
│   ├── App.tsx          # Main React component
│   ├── index.tsx        # React entry point
│   └── types.ts         # TypeScript type definitions
├── package.json         # Frontend dependencies
├── tsconfig.json        # TypeScript configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── requirements.txt     # Backend dependencies
```

## Setup

### Backend

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the `backend` directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=sqlite:///./chat_assistant.db
   ```

4. Start the backend server:
   ```
   cd backend
   uvicorn app:app --reload
   ```

### Frontend

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Start chatting with the AI assistant by typing in the input field
3. The AI will respond in real-time using the OpenAI API

## Database

The application uses SQLite by default, but can be configured to use PostgreSQL by changing the `DATABASE_URL` in the `.env` file:

```
DATABASE_URL=postgresql://username:password@localhost:5432/chat_assistant
```

## License

MIT 