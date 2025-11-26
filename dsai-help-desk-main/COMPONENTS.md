# Component Documentation

## Overview

This document provides detailed information about each React component in the AI Help Desk frontend.

---

## Core Components

### AIChatPanel

**Location**: `src/components/AIChatPanel.jsx`

**Purpose**: Main chat interface for user-AI interactions.

**Props**:
```javascript
{
  userRole: 'trainee' | 'instructor' | 'operator' | 'support_engineer',
  context: {
    module: string,
    channel: string
  }
}
```

**State**:
```javascript
{
  messages: Array<Message>,
  inputMessage: string,
  isLoading: boolean,
  sessionId: string,
  error: string | null
}
```

**Key Features**:
- Real-time chat with AI
- KB reference display with expandable cards
- Confidence score visualization (progress bar)
- Tier and severity badges
- Automatic ticket creation on escalation
- Session persistence (localStorage)

**Usage**:
```jsx
<AIChatPanel 
  userRole="trainee"
  context={{
    module: "lab-1",
    channel: "self-service-portal"
  }}
/>
```

---

### TicketCard

**Location**: `src/components/TicketCard.jsx`

**Purpose**: Display individual ticket information.

**Props**:
```javascript
{
  ticket: {
    id: string,
    subject: string,
    description: string,
    tier: string,
    severity: string,
    status: string,
    created_at: string,
    updated_at: string
  },
  onUpdate: (ticketId, updates) => void,
  onClick: (ticketId) => void
}
```

**Features**:
- Color-coded severity badges
- Status dropdown for updates
- Expandable description
- Timestamp formatting
- Click to view details

**Usage**:
```jsx
<TicketCard 
  ticket={ticketData}
  onUpdate={handleTicketUpdate}
  onClick={handleTicketClick}
/>
```

---

### MetricsCard

**Location**: `src/components/MetricsCard.jsx`

**Purpose**: Display individual metric with visualization.

**Props**:
```javascript
{
  title: string,
  value: number | string,
  icon: ReactElement,
  trend: 'up' | 'down' | 'neutral',
  trendValue: number,
  color: string
}
```

**Features**:
- Icon display
- Trend indicator (arrow up/down)
- Color customization
- Responsive sizing

**Usage**:
```jsx
<MetricsCard 
  title="Total Conversations"
  value={150}
  icon={<ChatIcon />}
  trend="up"
  trendValue={12}
  color="primary"
/>
```

---

### QuickActionCard

**Location**: `src/components/QuickActionCard.jsx`

**Purpose**: Quick action button for common tasks.

**Props**:
```javascript
{
  title: string,
  description: string,
  icon: ReactElement,
  onClick: () => void,
  color: string
}
```

**Features**:
- Icon + title + description layout
- Hover effects
- Click handler
- Customizable colors

**Usage**:
```jsx
<QuickActionCard 
  title="Reset Password"
  description="Reset your account password"
  icon={<LockResetIcon />}
  onClick={handlePasswordReset}
  color="primary"
/>
```

---

## Page Components

### SelfServicePortal

**Location**: `src/pages/SelfServicePortal.jsx`

**Purpose**: Main landing page with quick actions and chat.

**State**:
```javascript
{
  userRole: string,
  selectedModule: string,
  quickActions: Array<Action>
}
```

**Layout Sections**:
1. **Header**: App title and navigation
2. **Quick Actions Grid**: 4-column grid of action cards
3. **Chat Panel**: Full-width chat interface

**Quick Actions**:
- Reset Password
- Access Lab Environment
- View Documentation
- Report Issue
- Check System Status
- Contact Support

**Features**:
- Role-based action filtering
- Module context selection
- Persistent session
- Responsive grid layout

---

### TicketDashboard

**Location**: `src/pages/TicketDashboard.jsx`

**Purpose**: View and manage support tickets.

**State**:
```javascript
{
  tickets: Array<Ticket>,
  filters: {
    status: string,
    tier: string,
    severity: string,
    search: string
  },
  selectedTicket: Ticket | null,
  isLoading: boolean
}
```

**Features**:
- **Filters**:
  - Status dropdown (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
  - Tier dropdown (TIER_0 - TIER_4)
  - Severity dropdown (LOW, MEDIUM, HIGH, CRITICAL)
  - Search input (by subject/description)

- **Ticket List**:
  - Sortable columns
  - Pagination
  - Click to view details

- **Ticket Detail Modal**:
  - Full ticket information
  - Status update dropdown
  - Conversation history
  - AI analysis display

**API Integration**:
```javascript
useEffect(() => {
  const fetchTickets = async () => {
    const data = await ticketService.getTickets(filters)
    setTickets(data)
  }
  fetchTickets()
}, [filters])
```

---

### AnalyticsDashboard

**Location**: `src/pages/AnalyticsDashboard.jsx`

**Purpose**: Display help desk metrics and trends.

**State**:
```javascript
{
  summary: MetricsSummary,
  trends: MetricsTrends,
  period: number,
  isLoading: boolean
}
```

**Sections**:

1. **Summary Cards** (Top Row):
   - Total Conversations
   - Total Tickets
   - Deflection Rate
   - Average Confidence
   - Guardrail Activations

2. **Trend Charts** (Middle):
   - Conversation Volume (Line Chart)
   - Ticket Volume (Line Chart)
   - Deflection Rate (Line Chart)
   - Average Confidence (Line Chart)

3. **Distribution Charts** (Bottom):
   - Tickets by Tier (Pie Chart)
   - Tickets by Severity (Pie Chart)

**Features**:
- Period selector (7, 14, 30, 90 days)
- Auto-refresh every 5 minutes
- Export to CSV
- Print view

**Chart Library**: Recharts or Chart.js

---

## Utility Components

### LoadingSpinner

**Purpose**: Display loading state.

**Props**:
```javascript
{
  size: 'small' | 'medium' | 'large',
  color: string
}
```

**Usage**:
```jsx
{isLoading && <LoadingSpinner size="medium" />}
```

---

### ErrorMessage

**Purpose**: Display error messages.

**Props**:
```javascript
{
  message: string,
  severity: 'error' | 'warning' | 'info',
  onClose: () => void
}
```

**Usage**:
```jsx
{error && (
  <ErrorMessage 
    message={error}
    severity="error"
    onClose={() => setError(null)}
  />
)}
```

---

### ConfidenceBar

**Purpose**: Visualize confidence score.

**Props**:
```javascript
{
  value: number,
  showLabel: boolean
}
```

**Usage**:
```jsx
<ConfidenceBar value={0.85} showLabel={true} />
```

**Display**:
- 0-0.5: Red
- 0.5-0.7: Orange
- 0.7-0.85: Yellow
- 0.85-1.0: Green

---

## Component Best Practices

### 1. Props Validation

Use PropTypes for runtime validation:

```javascript
import PropTypes from 'prop-types'

AIChatPanel.propTypes = {
  userRole: PropTypes.oneOf(['trainee', 'instructor', 'operator', 'support_engineer']).isRequired,
  context: PropTypes.shape({
    module: PropTypes.string,
    channel: PropTypes.string
  })
}
```

### 2. Error Boundaries

Wrap components in error boundaries:

```javascript
<ErrorBoundary>
  <AIChatPanel />
</ErrorBoundary>
```

### 3. Memoization

Use React.memo for expensive components:

```javascript
export default React.memo(TicketCard)
```

### 4. Custom Hooks

Extract reusable logic:

```javascript
const useTickets = (filters) => {
  const [tickets, setTickets] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  
  useEffect(() => {
    const fetchTickets = async () => {
      setIsLoading(true)
      const data = await ticketService.getTickets(filters)
      setTickets(data)
      setIsLoading(false)
    }
    fetchTickets()
  }, [filters])
  
  return { tickets, isLoading }
}
```

### 5. Accessibility

Add ARIA labels:

```jsx
<button 
  aria-label="Send message"
  onClick={handleSend}
>
  <SendIcon />
</button>
```

---

## Testing

### Unit Tests

```javascript
import { render, screen, fireEvent } from '@testing-library/react'
import AIChatPanel from './AIChatPanel'

test('sends message on button click', () => {
  render(<AIChatPanel userRole="trainee" />)
  
  const input = screen.getByPlaceholderText('Type your message...')
  const button = screen.getByRole('button', { name: /send/i })
  
  fireEvent.change(input, { target: { value: 'Hello' } })
  fireEvent.click(button)
  
  expect(screen.getByText('Hello')).toBeInTheDocument()
})
```

### Integration Tests

```javascript
test('displays KB references after API response', async () => {
  const mockResponse = {
    answer: 'Test answer',
    kb_references: [
      { id: 'KB-001', title: 'Test KB', excerpt: 'Test excerpt' }
    ]
  }
  
  jest.spyOn(chatService, 'sendMessage').mockResolvedValue(mockResponse)
  
  render(<AIChatPanel userRole="trainee" />)
  
  // Send message
  // ...
  
  await waitFor(() => {
    expect(screen.getByText('Test KB')).toBeInTheDocument()
  })
})
```
