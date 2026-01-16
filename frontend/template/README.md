# FinPilot HTML Templates

This directory contains modular HTML templates for all features of the FinPilot application.

## Template Files

### Core Templates

- **index.html** - Main entry point combining all templates
- **nav.html** - Navigation bar with menu links
- **footer.html** - Footer with links and information

### Feature Templates

#### 1. **auth.html** - Authentication
- User login form
- User registration form
- Form validation and submission
- Account creation and verification

**Key Elements:**
- Login/Register tab switching
- Username and password fields
- Email validation for registration
- Full name optional field

#### 2. **dashboard.html** - Main Dashboard
- Overview of financial status
- Quick statistics cards
- This month's spending
- Average daily spending
- Savings progress
- Budget status
- AI recommendations

**Key Elements:**
- 4 summary cards with key metrics
- Recommendations section
- Welcome message with user's name
- Quick access to all features

#### 3. **expenses.html** - Expense Tracking
- Add new expenses form
- Expense category selection (8 categories)
- Expense list with filtering
- Search and category filters
- Expense summary

**Key Elements:**
- Amount and category inputs
- Description field
- Date selection
- Expense list table with date, category, description, amount
- Category breakdown summary
- Filter by category and search by description

#### 4. **budgets.html** - Budget Management
- Create new budget form
- Budget name and category
- Monthly/quarterly/yearly periods
- Budget overview grid
- Budget analysis section

**Key Elements:**
- Budget creation with name and category
- Limit setting
- Period selection
- Progress tracking
- Budget status indicators
- Comparison against actual spending

#### 5. **savings.html** - Savings Goals
- Set new savings goal form
- Goal name and target amount
- Current amount tracking
- Deadline setting
- Goal description
- Overall progress summary
- Savings tips

**Key Elements:**
- Target amount and deadline inputs
- Current saved amount tracker
- Progress percentage display
- Goal list with individual progress bars
- Savings tips section

#### 6. **advisor.html** - AI Financial Advisor
- Spending analysis section
- Monthly forecast
- Smart recommendations
- Category breakdown
- Spending trends
- Budget optimization suggestions
- Personalized insights

**Key Elements:**
- Analysis and forecast cards
- Recommendations list
- Category breakdown chart
- Trend visualization
- Optimization suggestions
- Generate insights button

#### 7. **profile.html** - User Profile & Settings
- Account information display
- Account statistics (expenses, budgets, goals, savings)
- Preferences (theme, currency, notifications)
- Security section (password change)
- Data management (download, delete account)
- Session management (logout)

**Key Elements:**
- User info (username, email, name, join date)
- Statistics dashboard
- Theme and currency preferences
- Password change form
- Data export option
- Account deletion option
- Logout button

## Usage

### Integration with Main Page

These templates are combined in the index.html using JavaScript to create a single-page application experience:

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="app">
        <!-- Navigation -->
        <nav id="nav-container"></nav>
        
        <!-- Main Content -->
        <div class="container main-content">
            <div id="dashboard-container"></div>
            <div id="expenses-container"></div>
            <div id="budgets-container"></div>
            <div id="savings-container"></div>
            <div id="advisor-container"></div>
            <div id="profile-container"></div>
            <div id="auth-container"></div>
        </div>
        
        <!-- Footer -->
        <footer id="footer-container"></footer>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

### Loading Templates with JavaScript

```javascript
// Load a single template
function loadTemplate(templateName, containerId) {
    fetch(`/templates/${templateName}.html`)
        .then(response => response.text())
        .then(html => {
            document.getElementById(containerId).innerHTML = html;
        });
}

// Load all templates
function initializeApp() {
    loadTemplate('nav', 'nav-container');
    loadTemplate('dashboard', 'dashboard-container');
    loadTemplate('expenses', 'expenses-container');
    loadTemplate('budgets', 'budgets-container');
    loadTemplate('savings', 'savings-container');
    loadTemplate('advisor', 'advisor-container');
    loadTemplate('profile', 'profile-container');
    loadTemplate('auth', 'auth-container');
    loadTemplate('footer', 'footer-container');
}
```

## HTML Classes & Structure

### Common Classes

- `.page` - Main page container for each feature
- `.card` - Content card/box
- `.btn` - Button element
- `.form-group` - Form input group
- `.table` - Data table
- `.grid` - Grid layout

### Feature-Specific Classes

- `.dashboard-grid` - 4-column grid for dashboard cards
- `.budgets-grid` - Grid layout for budget items
- `.savings-grid` - Grid layout for savings goals
- `.advisor-grid` - Grid layout for advisor sections
- `.recommendations` - Recommendations list styling
- `.profile-grid` - Grid layout for profile sections

## Styling

All templates use the following CSS files:
- `style.css` - Main styling and layout
- `responsive.css` - Mobile responsive design

### Responsive Design

Templates are designed to be fully responsive:
- Desktop: Full layouts with multiple columns
- Tablet: Adjusted layouts with 2-3 columns
- Mobile: Single column layout with stacked elements

## Form Validation

All forms include:
- Required field validation
- Input type validation (email, number, date)
- Client-side validation before submission
- Server-side validation on backend

## Data Binding

Templates include IDs for JavaScript data binding:
- `#monthly-spending` - Dashboard spending amount
- `#expenses-list` - Expense table body
- `#budgets-list` - Budget items container
- `#savings-list` - Savings goals container
- `#profile-username` - Profile username display

## Customization

To customize templates:

1. **Modify HTML structure** - Edit element hierarchy in template files
2. **Add new fields** - Add form inputs with unique IDs
3. **Update styling** - Modify CSS classes
4. **Add icons** - Use emoji or icon font
5. **Change colors** - Update CSS variables in style.css

## Best Practices

1. **Keep templates focused** - Each template handles one feature
2. **Use semantic HTML** - Proper element hierarchy and semantic tags
3. **Accessibility** - Include labels, alt text, and ARIA attributes
4. **Performance** - Minimize DOM nodes and optimize rendering
5. **Consistency** - Follow same naming conventions and structure

## Integration with Backend

Templates work with the following API endpoints:

### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Expenses
- `POST /api/expenses/`
- `GET /api/expenses/`
- `PUT /api/expenses/{id}`
- `DELETE /api/expenses/{id}`

### Budgets
- `POST /api/budgets/`
- `GET /api/budgets/`
- `PUT /api/budgets/{id}`
- `DELETE /api/budgets/{id}`

### Savings
- `POST /api/savings/`
- `GET /api/savings/`
- `PUT /api/savings/{id}`
- `DELETE /api/savings/{id}`

### AI Advisor
- `GET /api/advisor/recommendations`
- `GET /api/advisor/analysis`
- `GET /api/advisor/forecast`
- `GET /api/advisor/dashboard`
