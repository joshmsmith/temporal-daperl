# Customer Support DAPERL Dashboard

A web-based dashboard for monitoring and controlling customer support automation workflows powered by the DAPERL framework.

## Overview

This dashboard provides real-time visualization of the DAPERL workflow execution:

- **Detection**: View detected support issues and problems
- **Analysis**: Review root cause analysis and recommendations
- **Planning**: Approve or reject execution plans
- **Execution**: Monitor action execution and results
- **Reporting**: View metrics and performance data
- **Learning**: Explore insights and patterns

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Customer Support Dashboard                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Frontend (React + Vite)      Backend (FastAPI)         │
│  ┌──────────────────┐         ┌─────────────────────┐  │
│  │ Real-time UI     │◄────────┤ REST API            │  │
│  │ - Phase Progress │  HTTP   │ - Workflow Queries  │  │
│  │ - Plan Approval  │  WebSocket │ - Signal Handling│  │
│  │ - Results View   │         │ - Real-time Updates │  │
│  └──────────────────┘         └─────────────────────┘  │
│                                        ▲                 │
│                                        │                 │
│                                ┌───────┴───────┐        │
│                                │ Temporal      │        │
│                                │ Workflows     │        │
│                                └───────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Features

### 🔄 Real-time Updates
- WebSocket connection for live workflow status updates
- Automatic progress tracking through DAPERL phases
- Dynamic UI updates without page refresh

### ✅ Plan Approval
- Interactive approval interface for execution plans
- Detailed action breakdown with confidence scores
- Risk assessment and estimated duration
- Approve or cancel workflows with a click

### 📊 Rich Visualizations
- Color-coded phase progress indicators
- Severity-based problem highlighting
- Execution statistics and success rates
- Custom metrics display

### 🎨 Customer Support Specific
- SLA violation tracking
- Customer health scores
- Ticket priority visualization
- Support tier indicators

## Prerequisites

1. **Temporal Server** running
2. **DAPERL Worker** running
3. **Python 3.10+** with project dependencies
4. **Node.js 18+** and npm

## Installation

### Backend Setup

The backend Python dependencies are managed via Poetry in the parent `customer_support` directory:

```bash
cd examples/customer_support

# Install all dependencies (including UI backend)
poetry install
```

This installs:
- The main DAPERL framework
- FastAPI and Uvicorn for the backend
- WebSockets support
- All required dependencies

### Frontend Setup

```bash
cd examples/customer_support/ui/frontend

# Install Node dependencies
npm install
```

## Usage

### Quick Start (Recommended)

Use the provided launcher script to start both frontend and backend:

```bash
cd examples/customer_support
poetry run python run_ui.py
```

This will:
1. Check dependencies
2. Start the FastAPI backend (http://localhost:8000)
3. Start the React frontend (http://localhost:5173)
4. Display URLs and next steps

### Manual Start

#### Start Backend

```bash
cd examples/customer_support/ui/backend
python main.py
```

Backend will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

#### Start Frontend

```bash
cd examples/customer_support/ui/frontend
npm run dev
```

Frontend will be available at http://localhost:5173

## Running a Complete Example

1. **Start Temporal Server** (if not already running):
   ```bash
   temporal server start-dev
   ```

2. **Start DAPERL Worker**:
   ```bash
   poetry run python scripts/run_worker.py
   ```

3. **Launch the Dashboard**:
   ```bash
   cd examples/customer_support
   poetry run python run_ui.py
   ```

4. **Start a Workflow**:
   ```bash
   # In a new terminal
   poetry run python examples/customer_support/run_example.py
   ```

5. **Open Browser**:
   - Navigate to http://localhost:5173
   - Enter workflow ID: `customer-support-demo`
   - Click "Load Workflow"

6. **Interact with Workflow**:
   - Watch real-time progress through DAPERL phases
   - Approve execution plan when prompted
   - View results as they become available

## API Endpoints

### GET /api/workflows/{workflow_id}
Get complete workflow data including status, plan, and results.

### GET /api/workflows/{workflow_id}/status
Get current workflow status (lighter query).

### GET /api/workflows/{workflow_id}/plan
Get the execution plan.

### POST /api/workflows/{workflow_id}/approve
Approve or cancel the workflow.
```json
{
  "approved": true  // or false to cancel
}
```

### WebSocket /ws/workflows/{workflow_id}
Real-time status updates via WebSocket.

## Project Structure

```
ui/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── App.tsx          # Main application
    │   ├── App.css          # Global styles
    │   ├── lib/
    │   │   └── api.ts       # API client
    │   └── components/
    │       ├── Dashboard.tsx        # Main dashboard
    │       ├── PhaseProgress.tsx    # DAPERL phase indicator
    │       ├── PlanApproval.tsx     # Plan approval UI
    │       ├── DetectionResults.tsx # Detection phase results
    │       ├── AnalysisResults.tsx  # Analysis phase results
    │       ├── ExecutionResults.tsx # Execution statistics
    │       └── ReportingResults.tsx # Reporting metrics
    │
    ├── package.json         # Node dependencies
    └── vite.config.ts       # Vite configuration
```

## Customization

### Adding Custom Metrics

Edit `ReportingResults.tsx` to add domain-specific metric displays:

```typescript
// Add custom metric rendering
{data.metrics.custom_metric && (
  <div className="metric-item">
    <div className="metric-label">Custom Metric</div>
    <div className="metric-value">{data.metrics.custom_metric}</div>
  </div>
)}
```

### Styling

Modify `App.css` to customize colors, layouts, and animations:

```css
/* Change primary color */
.btn-primary {
  background: your-color-here;
}
```

### API Configuration

Update the API base URL in `frontend/src/lib/api.ts`:

```typescript
const API_BASE_URL = 'http://your-backend-url:8000';
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Temporal connection settings in `.env`
- Ensure Python dependencies are installed: `cd examples/customer_support && poetry install`

### Frontend won't start
- Check if port 5173 is available
- Run `npm install` in frontend directory
- Clear npm cache: `npm cache clean --force`

### Workflow not found
- Verify workflow ID is correct
- Check if workflow is actually running in Temporal
- View Temporal UI: http://localhost:8233

### WebSocket connection fails
- Ensure backend is running
- Check browser console for errors
- Verify CORS settings in backend

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Enable debug mode:
```python
# In main.py
uvicorn.run("main:app", reload=True, log_level="debug")
```

### Frontend Development

Vite provides hot module replacement for instant updates:
```bash
npm run dev
```

Build for production:
```bash
npm run build
npm run preview
```

## Production Deployment

### Backend

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend

```bash
# Build production bundle
npm run build

# Serve with your preferred static server
# (nginx, Apache, or serve package)
```

## Future Enhancements

Potential additions for production use:

- **Authentication**: JWT tokens, OAuth integration
- **Multiple Workflows**: List view and filtering
- **Historical Data**: Workflow execution history
- **Charts**: Trend analysis and visualizations
- **Notifications**: Browser notifications for events
- **Mobile**: Responsive mobile-first design
- **Theming**: Dark mode and custom themes
- **Export**: PDF reports and CSV data export

## Support

For issues or questions:
1. Check the main DAPERL documentation
2. Review Temporal documentation
3. Check browser console for errors
4. Verify all services are running

## License

Same as DAPERL framework.
