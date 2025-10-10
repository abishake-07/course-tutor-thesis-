# Tudu - Smart Task & Budget Manager 🎯💰

A modern FastAPI application that combines task management and budget tracking with AI-powered insights and voice commands.

## Features

### 📋 Task Management
- Create, update, and delete tasks
- Set priorities (Low, Medium, High, Urgent) 
- Due date tracking with overdue alerts
- Task completion tracking with time logging
- AI-powered task breakdown suggestions

### 💰 Budget Tracking
- Income and expense tracking
- Category-based organization
- Monthly budget analytics
- Visual charts and trends
- AI-powered expense categorization

### 🤖 AI Integration
- Voice commands for hands-free operation
- Intelligent task and budget insights
- Automated expense categorization
- Pattern analysis and recommendations
- Speech recognition for voice input

### 🎙️ Voice Commands Examples
- "Add task: Buy groceries"
- "I spent $25 on lunch"
- "Show my tasks"
- "Budget summary"
- "Add high priority task: Finish project report"

## Technology Stack

- **Backend**: FastAPI with Python 3.9+
- **Database**: SQLAlchemy with SQLite (easily configurable for PostgreSQL)
- **Frontend**: Bootstrap 5 with Chart.js for visualizations
- **AI**: OpenAI API integration with fallback local processing
- **Voice**: Web Speech Recognition API
- **Package Manager**: UV for fast Python package management

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abishake-07/tudu.git
   cd tudu
   ```

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - API documentation available at `http://localhost:8000/docs`

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./tudu.db

# Security
SECRET_KEY=your-super-secret-key

# OpenAI (Optional - for enhanced AI features)
OPENAI_API_KEY=your-openai-api-key

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Database Setup

The application automatically creates the database tables on first run. For production, consider using PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost/tudu
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/tasks/stats` - Get task statistics

### Budget
- `GET /api/budget/` - List budget items
- `POST /api/budget/` - Create budget item
- `GET /api/budget/summary` - Get budget summary
- `GET /api/budget/analytics/monthly` - Monthly analytics

### AI Assistant
- `POST /api/ai/voice-command` - Process voice commands
- `GET /api/ai/insights` - Get AI insights
- `POST /api/ai/suggest-task-breakdown/{id}` - Task breakdown suggestions

## Voice Commands

The application supports natural language voice commands:

### Task Commands
- "Add task: [task description]"
- "Create high priority task: [description]"
- "Complete task"
- "Show my tasks"
- "List pending tasks"

### Budget Commands
- "I spent $[amount] on [description]"
- "Add expense: $[amount] for [description]"
- "I earned $[amount] from [source]"
- "Budget summary"
- "Show spending"

## AI Features

### Task Intelligence
- **Smart Suggestions**: AI analyzes your task patterns and suggests optimal scheduling
- **Task Breakdown**: Complex tasks are automatically broken into manageable subtasks
- **Priority Recommendations**: AI suggests task priorities based on due dates and content

### Budget Analysis
- **Expense Categorization**: Automatic categorization of expenses using ML
- **Spending Patterns**: Analysis of spending habits with actionable insights
- **Budget Predictions**: Forecast future expenses based on historical data

### Voice Assistant
- **Natural Language Processing**: Understand conversational commands
- **Context Awareness**: Commands are processed with user's current data context
- **Multi-modal Input**: Support for both voice and text input

## Development

### Project Structure
```
tudu/
├── app/
│   ├── models/           # Database models
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── static/           # CSS, JS files
│   ├── templates/        # HTML templates
│   ├── database.py       # Database configuration
│   ├── schemas.py        # Pydantic models
│   └── main.py          # FastAPI app
├── main.py              # Application entry point
├── pyproject.toml       # UV configuration
└── README.md
```

### Running Tests
```bash
# Run tests (when implemented)
uv run pytest
```

### Code Quality
```bash
# Format code
uv run black .

# Type checking
uv run mypy app/
```

## Deployment

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

CMD ["python", "main.py"]
```

### Using Railway/Heroku
The application is ready for deployment on modern platforms. Set the environment variables and deploy!

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Team collaboration features
- [ ] Advanced AI insights with local LLM support
- [ ] Integration with external calendars
- [ ] Recurring task templates
- [ ] Budget goal setting and tracking
- [ ] Export/import functionality
- [ ] Dark theme support

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/abishake-07/tudu/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

---

**Built with ❤️ using FastAPI, UV, and modern web technologies**
