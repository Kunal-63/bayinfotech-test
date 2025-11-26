# Frontend Architecture

## Overview

The AI Help Desk frontend is a React-based single-page application (SPA) that provides an intuitive interface for users to interact with the AI-powered support system.

## Tech Stack

- **Framework**: React 18.3+
- **Build Tool**: Vite 5.4+
- **UI Library**: Material-UI (MUI) 6.1+
- **State Management**: React Hooks (useState, useEffect, useContext)
- **HTTP Client**: Axios
- **Routing**: React Router DOM 6.26+
- **Styling**: Material-UI + Custom CSS
- **Deployment**: Vercel

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         React Application (Vercel)          │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │         App.jsx (Router)              │ │
│  │  - Route Configuration                │ │
│  │  - Theme Provider                     │ │
│  └──────────┬────────────────────────────┘ │
│             │                               │
│  ┌──────────▼────────────────────────────┐ │
│  │         Pages Layer                   │ │
│  │  - SelfServicePortal.jsx              │ │
│  │  - TicketDashboard.jsx                │ │
│  │  - AnalyticsDashboard.jsx             │ │
│  └──────────┬────────────────────────────┘ │
│             │                               │
│  ┌──────────▼────────────────────────────┐ │
│  │      Components Layer                 │ │
│  │  - AIChatPanel.jsx                    │ │
│  │  - TicketCard.jsx                     │ │
│  │  - MetricsCard.jsx                    │ │
│  │  - QuickActionCard.jsx                │ │
│  └──────────┬────────────────────────────┘ │
│             │                               │
│  ┌──────────▼────────────────────────────┐ │
│  │       Services Layer                  │ │
│  │  - apiClient.js                       │ │
│  │  - chatService.js                     │ │
│  │  - ticketService.js                   │ │
│  │  - metricsService.js                  │ │
│  └──────────┬────────────────────────────┘ │
│             │                               │
└─────────────┼───────────────────────────────┘
              │ HTTPS
              ▼
┌─────────────────────────────────────────────┐
│     Backend API (Render)                    │
│     https://bayinfotech-test.onrender.com   │
└─────────────────────────────────────────────┘
```

## Directory Structure

```
dsai-help-desk-main/
├── public/
│   └── vite.svg
├── src/
│   ├── components/
│   │   ├── AIChatPanel.jsx          # Main chat interface
│   │   ├── TicketCard.jsx           # Ticket display card
│   │   ├── MetricsCard.jsx          # Analytics card
│   │   └── QuickActionCard.jsx      # Quick action buttons
│   ├── pages/
│   │   ├── SelfServicePortal.jsx    # Main portal page
│   │   ├── TicketDashboard.jsx      # Ticket management
│   │   └── AnalyticsDashboard.jsx   # Metrics & analytics
│   ├── services/
│   │   ├── apiClient.js             # Axios instance
│   │   ├── chatService.js           # Chat API calls
│   │   ├── ticketService.js         # Ticket API calls
│   │   └── metricsService.js        # Metrics API calls
│   ├── utils/
│   │   └── constants.js             # App constants
│   ├── App.jsx                      # Root component
│   ├── main.jsx                     # Entry point
│   └── index.css                    # Global styles
├── .env.example                     # Environment template
├── package.json                     # Dependencies
└── vite.config.js                   # Vite configuration
```

## Core Components

### 1. AIChatPanel (`components/AIChatPanel.jsx`)

**Purpose**: Main chat interface for user-AI interactions.

**Features**:
- Real-time message streaming
- KB reference display
- Confidence score visualization
- Tier and severity badges
- Escalation indicators
- Session management

**State Management**:
```javascript
const [messages, setMessages] = useState([])
const [inputMessage, setInputMessage] = useState('')
const [isLoading, setIsLoading] = useState(false)
const [sessionId, setSessionId] = useState(null)
```

**Key Functions**:
- `handleSendMessage()`: Send user message to backend
- `displayKBReferences()`: Show knowledge base citations
- `handleEscalation()`: Handle ticket creation
- `generateSessionId()`: Create unique session ID

### 2. SelfServicePortal (`pages/SelfServicePortal.jsx`)

**Purpose**: Main landing page with quick actions and chat.

**Features**:
- Quick action cards (Reset Password, Access Lab, etc.)
- Embedded chat panel
- User role selection
- Module context

**Layout**:
```
┌─────────────────────────────────────┐
│          Header                     │
├─────────────────────────────────────┤
│  Quick Actions Grid                 │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │
│  │ Act1│ │ Act2│ │ Act3│ │ Act4│  │
│  └─────┘ └─────┘ └─────┘ └─────┘  │
├─────────────────────────────────────┤
│          AI Chat Panel              │
│  ┌───────────────────────────────┐ │
│  │  Chat Messages                │ │
│  │  ...                          │ │
│  └───────────────────────────────┘ │
│  [Input Box]              [Send]   │
└─────────────────────────────────────┘
```

### 3. TicketDashboard (`pages/TicketDashboard.jsx`)

**Purpose**: View and manage support tickets.

**Features**:
- Ticket list with filters (status, tier, severity)
- Ticket detail view
- Status updates
- Search functionality
- Real-time updates

**Filters**:
- Status: OPEN, IN_PROGRESS, RESOLVED, CLOSED
- Tier: TIER_0 to TIER_4
- Severity: LOW, MEDIUM, HIGH, CRITICAL

### 4. AnalyticsDashboard (`pages/AnalyticsDashboard.jsx`)

**Purpose**: Display help desk metrics and trends.

**Metrics**:
- Total conversations
- Total tickets
- Deflection rate
- Average confidence
- Guardrail activations
- Tickets by tier/severity

**Visualizations**:
- Line charts for trends
- Pie charts for distribution
- Summary cards

## Services Layer

### apiClient.js

**Purpose**: Centralized HTTP client configuration.

**Features**:
- Axios instance with base URL
- Request/response interceptors
- Error handling
- Timeout configuration

```javascript
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### chatService.js

**Purpose**: Chat API integration.

**Methods**:
- `sendMessage(sessionId, message, userRole, context)`: Send chat message
- Returns: `{ answer, kb_references, confidence, tier, severity, needs_escalation, ticket_id }`

### ticketService.js

**Purpose**: Ticket API integration.

**Methods**:
- `createTicket(data)`: Create new ticket
- `getTickets(filters)`: List tickets with filters
- `getTicket(id)`: Get single ticket
- `updateTicket(id, updates)`: Update ticket status

### metricsService.js

**Purpose**: Metrics API integration.

**Methods**:
- `getSummary()`: Get summary metrics
- `getTrends(period)`: Get trend data
- `getDeflection()`: Get deflection metrics
- `getGuardrails()`: Get guardrail metrics

## State Management

### Session Management

```javascript
const generateSessionId = () => {
  return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

useEffect(() => {
  const storedSessionId = localStorage.getItem('sessionId')
  if (storedSessionId) {
    setSessionId(storedSessionId)
  } else {
    const newSessionId = generateSessionId()
    setSessionId(newSessionId)
    localStorage.setItem('sessionId', newSessionId)
  }
}, [])
```

### Message History

```javascript
const [messages, setMessages] = useState([])

const addMessage = (role, content, metadata = {}) => {
  setMessages(prev => [...prev, {
    id: Date.now(),
    role,
    content,
    timestamp: new Date(),
    ...metadata
  }])
}
```

## Styling

### Theme Configuration

Material-UI theme with custom colors:

```javascript
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
})
```

### Responsive Design

- Mobile-first approach
- Breakpoints: xs, sm, md, lg, xl
- Grid system for layouts
- Flexible components

## Performance Optimizations

1. **Code Splitting**: React.lazy() for route-based splitting
2. **Memoization**: useMemo() and useCallback() for expensive computations
3. **Virtualization**: For long lists (ticket dashboard)
4. **Debouncing**: For search inputs
5. **Image Optimization**: Lazy loading images

## Error Handling

### API Error Handling

```javascript
try {
  const response = await chatService.sendMessage(...)
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error('Server error:', error.response.data)
  } else if (error.request) {
    // No response received
    console.error('Network error')
  } else {
    // Request setup error
    console.error('Error:', error.message)
  }
}
```

### Error Boundaries

```javascript
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo)
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />
    }
    return this.props.children
  }
}
```

## Security Considerations

1. **XSS Prevention**: React's built-in escaping
2. **HTTPS Only**: Enforced by Vercel
3. **Environment Variables**: Sensitive data in .env
4. **CORS**: Backend validates origin
5. **Input Validation**: Client-side validation before API calls

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance (WCAG AA)
