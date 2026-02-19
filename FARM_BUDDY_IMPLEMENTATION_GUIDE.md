# Farm Buddy → AgriGPT v2.0: Step-by-Step Implementation Guide
## 🎯 LLM-Friendly Incremental Development Plan

> **IMPORTANT**: Work on ONE phase at a time. Complete, test, and commit before moving to the next phase.

---

## 📋 HOW TO USE THIS GUIDE WITH AN LLM

### Best Practices:
1. **Copy ONE phase at a time** to your LLM (Claude, ChatGPT, etc.)
2. **Complete and test** that phase fully before moving to the next
3. **Commit to Git** after each successful phase
4. **Don't skip phases** - they build on each other
5. **Test thoroughly** between phases to catch issues early

### When Working with LLM:
- Start your prompt with: "I'm working on Phase X of my Farm Buddy project. Here are the requirements..."
- Provide context about your current project structure
- Ask for code in small, testable chunks
- Request explanations for complex parts
- Ask the LLM to show you where to place each file

---

## 🚀 PHASE-BY-PHASE BREAKDOWN

---

## **PHASE 1: MULTI-LANGUAGE FOUNDATION** (Week 1)

### Phase 1.1: Django i18n Setup (Day 1-2)
**Goal**: Set up Django's internationalization framework

**Tasks**:
1. Update `settings.py` with i18n configuration
2. Create directory structure for translation files
3. Install required packages
4. Test basic translation functionality

**Files to Modify/Create**:
- `farmbuddy_web/settings.py`
- Create: `locale/` directory with subdirectories

**LLM Prompt Template**:
```
I'm working on Phase 1.1 of my Farm Buddy Django project. I need to set up Django's internationalization framework for 4 languages: English, Hausa, Yoruba, and Igbo.

Current project structure:
- farmbuddy_web/ (Django project)
- chat/ (Django app)
- utils/

Please help me:
1. Update settings.py with proper i18n configuration
2. Show me the exact directory structure for locale files
3. Provide commands to create initial translation files
4. Give me a simple test to verify it's working

Show me ONE file at a time.
```

**Testing Checklist**:
- [ ] Django starts without errors
- [ ] Locale directories are created
- [ ] Can generate .po files successfully

---

### Phase 1.2: Language Switcher UI (Day 3)
**Goal**: Add language switcher to the header

**Tasks**:
1. Create language switcher component (HTML/CSS/JS)
2. Add language detection logic
3. Store user's language preference (localStorage for now)
4. Update header to include switcher

**Files to Modify/Create**:
- `chat/templates/chat/base.html` (or your base template)
- `chat/static/chat/css/styles.css`
- `chat/static/chat/js/language-switcher.js`

**LLM Prompt Template**:
```
I'm working on Phase 1.2 - adding a language switcher to my Farm Buddy app.

I need a dropdown in the header that shows:
- Current language (e.g., "Hausa / English")
- Options: English, Hausa, Yoruba, Igbo

Requirements:
- Plain HTML/CSS/JS (no frameworks)
- Store preference in localStorage
- Reload page when language changes
- Match the AgriGPT design style (clean, modern)

Current header structure: [paste your header HTML here]

Please provide:
1. HTML for the language switcher
2. CSS for styling
3. JavaScript for functionality

One component at a time please.
```

**Testing Checklist**:
- [ ] Dropdown appears in header
- [ ] Can select different languages
- [ ] Selection persists on page reload
- [ ] UI looks good on mobile

---

### Phase 1.3: Translate Core UI (Day 4-5)
**Goal**: Translate all existing UI elements

**Tasks**:
1. Mark all translatable strings in templates with `{% trans %}`
2. Extract messages to .po files
3. Get translations for Hausa, Yoruba, Igbo
4. Compile messages

**Files to Modify**:
- All template files in `chat/templates/`
- Translation files in `locale/`

**LLM Prompt Template**:
```
I'm working on Phase 1.3 - translating my Farm Buddy UI.

Here's my main chat template: [paste template]

Please help me:
1. Identify all translatable strings
2. Show me how to wrap them with {% trans %} tags
3. Provide example translations for these strings in Hausa

Do this for ONE template at a time.
```

**Testing Checklist**:
- [ ] All UI text is translatable
- [ ] English works perfectly
- [ ] Other languages display (even with placeholder translations)
- [ ] No broken layouts with different text lengths

---

### Phase 1.4: AI Response Language Support (Day 6-7)
**Goal**: Make Gemini AI respond in user's selected language

**Tasks**:
1. Modify AI prompt to include language instruction
2. Pass user's language preference to AI call
3. Test AI responses in all languages

**Files to Modify**:
- `chat/views.py` (or wherever Gemini API is called)
- AI prompt configuration

**LLM Prompt Template**:
```
I'm working on Phase 1.4 - making my Gemini AI respond in the user's selected language.

Current AI call code: [paste relevant code]

Please help me:
1. Modify the system prompt to include language instruction
2. Pass the user's language preference from the session/localStorage
3. Ensure responses are in the correct language

Requirements:
- Support: English, Hausa, Yoruba, Igbo
- Fallback to English if language not supported
- Maintain context and quality
```

**Testing Checklist**:
- [ ] AI responds in English when English selected
- [ ] AI responds in Hausa when Hausa selected
- [ ] Quality of responses is maintained
- [ ] No encoding issues with special characters

---

## **PHASE 2: SOIL NUTRITION FEATURE** (Week 2-3)

### Phase 2.1: Soil Nutrition Data Model (Day 1)
**Goal**: Create database structure for soil data

**Tasks**:
1. Create Django model for soil types
2. Create model for crop-soil relationships
3. Run migrations
4. Add sample data

**Files to Create/Modify**:
- `chat/models.py`
- Create migration files

**LLM Prompt Template**:
```
I'm working on Phase 2.1 - creating database models for soil nutrition.

I need models for:
1. SoilType (name, pH range, characteristics, recommended crops)
2. CropSoilRequirement (crop name, ideal soil type, NPK requirements)
3. FertilizerRecommendation (soil type, crop, fertilizer type, amount)

Please provide:
1. Django model definitions
2. Migration commands
3. Sample data fixtures for Nigerian crops (maize, cassava, rice, yam)

Show me ONE model at a time.
```

**Testing Checklist**:
- [ ] Migrations run successfully
- [ ] Can create records via Django admin
- [ ] Sample data loads correctly
- [ ] Database queries work

---

### Phase 2.2: Soil Nutrition API Endpoint (Day 2)
**Goal**: Create API endpoint for soil recommendations

**Tasks**:
1. Create view for soil nutrition queries
2. Integrate with Gemini AI for personalized advice
3. Return structured data

**Files to Create/Modify**:
- `chat/views.py`
- `chat/urls.py`

**LLM Prompt Template**:
```
I'm working on Phase 2.2 - creating an API endpoint for soil nutrition.

Endpoint: POST /api/soil-nutrition/

Expected request body:
{
  "crop": "maize",
  "location": "Kano",
  "soil_type": "sandy" (optional),
  "language": "en"
}

Expected response:
{
  "recommendations": {
    "ideal_soil": "...",
    "current_soil_suitability": "...",
    "fertilizer_recommendations": [...],
    "npk_ratios": {...},
    "tips": [...]
  }
}

Please provide:
1. Django view function
2. URL configuration
3. Integration with Gemini AI for recommendations
4. Error handling

Current project structure: [paste structure]
```

**Testing Checklist**:
- [ ] Endpoint returns correct data structure
- [ ] Works with all crops in database
- [ ] Handles missing parameters gracefully
- [ ] Responses are in correct language

---

### Phase 2.3: Soil Nutrition UI (Day 3-4)
**Goal**: Build frontend for soil nutrition feature

**Tasks**:
1. Create soil nutrition feature card on homepage
2. Build soil nutrition query form
3. Display recommendations nicely
4. Add to main navigation

**Files to Create/Modify**:
- `chat/templates/chat/index.html`
- Create: `chat/templates/chat/soil_nutrition.html`
- `chat/static/chat/css/soil-nutrition.css`
- `chat/static/chat/js/soil-nutrition.js`

**LLM Prompt Template**:
```
I'm working on Phase 2.3 - building the UI for soil nutrition feature.

I need:
1. A feature card on the homepage (matching AgriGPT style from the image)
2. A form where users can:
   - Select crop type
   - Enter location
   - Optionally specify soil type
3. Display area for recommendations showing:
   - Ideal soil characteristics
   - Fertilizer recommendations
   - NPK ratios (visual representation)
   - Tips and warnings

Design requirements:
- Clean, modern design matching AgriGPT
- Mobile responsive
- Loading states
- Error handling

Please provide HTML first, then CSS, then JavaScript.
One file at a time.
```

**Testing Checklist**:
- [ ] Feature card appears on homepage
- [ ] Form validates inputs
- [ ] Recommendations display correctly
- [ ] Works on mobile devices
- [ ] Loading indicators work
- [ ] Error messages are user-friendly

---

## **PHASE 3: MARKET PRICES FEATURE** (Week 3-4)

### Phase 3.1: Market Data Research & Integration (Day 1-2)
**Goal**: Identify and integrate market price data sources

**Tasks**:
1. Research Nigerian agricultural market APIs
2. Create fallback web scraping if needed
3. Set up data storage structure
4. Create scheduled task for updates

**Files to Create**:
- `utils/market_data_fetcher.py`
- `chat/models.py` (add market price models)
- `chat/management/commands/update_market_prices.py`

**LLM Prompt Template**:
```
I'm working on Phase 3.1 - integrating market price data.

I need to:
1. Create a MarketPrice model with fields:
   - crop_name
   - market_location (Lagos, Kano, Abuja, etc.)
   - price_per_kg
   - currency (NGN)
   - date
   - source
   
2. Create a function to fetch prices from [source - you'll need to specify]

3. Create a Django management command to update prices daily

Please provide:
1. Model definition
2. Data fetcher function
3. Management command setup

Show me ONE component at a time.
```

**Testing Checklist**:
- [ ] Model created and migrated
- [ ] Can manually add price data
- [ ] Data fetcher works (even with dummy data initially)
- [ ] Management command runs successfully

---

### Phase 3.2: Market Prices API (Day 3)
**Goal**: Create API endpoints for market data

**Tasks**:
1. Create endpoint to get current prices
2. Create endpoint for price trends/history
3. Create endpoint for price comparisons

**Files to Create/Modify**:
- `chat/views.py`
- `chat/urls.py`

**LLM Prompt Template**:
```
I'm working on Phase 3.2 - creating market price API endpoints.

I need three endpoints:

1. GET /api/market-prices/?crop=maize&location=Lagos
   Returns: Current price for specific crop/location

2. GET /api/market-prices/trends/?crop=maize&days=30
   Returns: Price history for last N days

3. GET /api/market-prices/compare/?crop=maize&locations=Lagos,Kano,Abuja
   Returns: Price comparison across markets

Please provide:
1. View functions with proper error handling
2. URL configurations
3. Example responses

Show one endpoint at a time.
```

**Testing Checklist**:
- [ ] All endpoints return correct data
- [ ] Handles missing parameters
- [ ] Returns appropriate HTTP status codes
- [ ] Data is properly formatted

---

### Phase 3.3: Market Prices UI (Day 4-5)
**Goal**: Build market prices interface

**Tasks**:
1. Create market prices feature card
2. Build price comparison interface
3. Add price trend charts
4. Integrate with AI for market insights

**Files to Create/Modify**:
- `chat/templates/chat/market_prices.html`
- `chat/static/chat/css/market-prices.css`
- `chat/static/chat/js/market-prices.js`

**LLM Prompt Template**:
```
I'm working on Phase 3.3 - building the market prices UI.

I need:
1. Feature card on homepage
2. Price comparison table showing:
   - Crop name
   - Prices across different markets
   - Price trend (up/down arrows)
   - Best market to sell (highlighted)
   
3. Price trend chart (line chart) using Chart.js

4. Search/filter functionality:
   - Filter by crop
   - Filter by market
   - Date range selector

Design: Match AgriGPT style, mobile-responsive

Please provide HTML first, then I'll ask for CSS and JavaScript.
```

**Testing Checklist**:
- [ ] Price data displays correctly
- [ ] Charts render properly
- [ ] Filters work
- [ ] Responsive on mobile
- [ ] Updates in real-time (or on refresh)

---

## **PHASE 4: UI/UX REDESIGN** (Week 5-6)

### Phase 4.1: Sidebar Navigation (Day 1-2)
**Goal**: Implement left sidebar matching AgriGPT

**Tasks**:
1. Create sidebar HTML structure
2. Add "New Chat" button
3. Add "Recent Queries" section
4. Make it collapsible on mobile

**Files to Create/Modify**:
- `chat/templates/chat/base.html`
- Create: `chat/static/chat/css/sidebar.css`
- Create: `chat/static/chat/js/sidebar.js`

**LLM Prompt Template**:
```
I'm working on Phase 4.1 - creating the sidebar navigation.

Based on the AgriGPT image I shared, I need a left sidebar with:

Structure:
- Logo at top
- "New Chat" button
- "Recent Queries" section with list items (icons + text)
- Settings icon at bottom
- Help Center icon at bottom
- User profile section at bottom (placeholder for now)

Requirements:
- Fixed position on desktop
- Slide-in drawer on mobile
- Smooth animations
- Icons for each section
- Current Django template: [paste your base template]

Please provide:
1. HTML structure
2. CSS for styling
3. JavaScript for mobile toggle

One file at a time please.
```

**Testing Checklist**:
- [ ] Sidebar appears on desktop
- [ ] Sidebar toggles on mobile
- [ ] "New Chat" button works
- [ ] Smooth animations
- [ ] Icons display correctly

---

### Phase 4.2: Homepage Hero Section (Day 3)
**Goal**: Create the main welcome section

**Tasks**:
1. Large heading: "How can I help your farm today?"
2. Subtitle with description
3. Feature cards grid (2x2)

**Files to Modify**:
- `chat/templates/chat/index.html`
- `chat/static/chat/css/homepage.css`

**LLM Prompt Template**:
```
I'm working on Phase 4.2 - redesigning the homepage hero section.

I need:
1. Large centered heading: "How can I help your farm today?"
2. Subtitle: "Your AI partner for better yields. Ask about planting schedules, pests, fertilizers, or market prices."
3. 4 feature cards in a 2x2 grid:
   - Weather Forecast
   - Soil Nutrition
   - Pest Diagnosis
   - Market Prices

Each card should have:
- Icon
- Title
- Short description
- Clickable (navigates to feature)
- Hover effect

Design: Match AgriGPT green theme, clean and modern

Please provide HTML and CSS. One at a time.
```

**Testing Checklist**:
- [ ] Hero text displays correctly
- [ ] Feature cards in grid
- [ ] Cards are clickable
- [ ] Hover effects work
- [ ] Responsive on mobile (stacks vertically)

---

### Phase 4.3: Chat Interface Redesign (Day 4)
**Goal**: Modernize chat bubbles and layout

**Tasks**:
1. Redesign message bubbles
2. Add user/bot avatars
3. Create "Farmer Tip" callout boxes
4. Add typing indicators

**Files to Modify**:
- `chat/templates/chat/chat_interface.html`
- `chat/static/chat/css/chat.css`
- `chat/static/chat/js/chat.js`

**LLM Prompt Template**:
```
I'm working on Phase 4.3 - redesigning the chat interface.

Current chat structure: [paste your chat HTML]

I need:
1. Modern message bubbles (rounded, with shadows)
2. User messages: right-aligned, different color
3. Bot messages: left-aligned, with bot avatar
4. Special "Farmer Tip" boxes (green background, icon) like in AgriGPT
5. Typing indicator when bot is responding
6. Timestamps on hover

Please provide updated HTML and CSS.
One section at a time.
```

**Testing Checklist**:
- [ ] Messages display correctly
- [ ] Avatars appear
- [ ] Farmer tips stand out
- [ ] Typing indicator works
- [ ] Scroll works smoothly

---

### Phase 4.4: Input Area Enhancement (Day 5)
**Goal**: Redesign chat input area

**Tasks**:
1. Bottom-fixed input bar
2. Add icons (attachment, microphone, send)
3. Make input expandable
4. Add placeholder text

**Files to Modify**:
- `chat/templates/chat/chat_interface.html`
- `chat/static/chat/css/input.css`
- `chat/static/chat/js/input.js`

**LLM Prompt Template**:
```
I'm working on Phase 4.4 - enhancing the chat input area.

I need a fixed bottom input bar with:
- Attachment icon (📎) on left
- Text input in center (expandable)
- Microphone icon (🎤) for voice
- Send button on right (green)
- Placeholder: "Ask AgriGPT anything..."

Requirements:
- Stays at bottom on scroll
- Input expands for long text
- Icons are clickable
- Mobile responsive

Please provide HTML, CSS, and basic JavaScript.
```

**Testing Checklist**:
- [ ] Input bar stays at bottom
- [ ] All icons appear
- [ ] Input expands correctly
- [ ] Send button works
- [ ] Mobile keyboard doesn't break layout

---

### Phase 4.5: Color Scheme Update (Day 6)
**Goal**: Apply AgriGPT color palette

**Tasks**:
1. Update CSS variables
2. Apply new colors throughout
3. Update dark mode colors

**Files to Modify**:
- `chat/static/chat/css/variables.css` (create if needed)
- All CSS files

**LLM Prompt Template**:
```
I'm working on Phase 4.5 - updating the color scheme to match AgriGPT.

Based on the image:
- Primary green: bright green (#00D100 or similar)
- Background: white/light gray
- Text: dark gray
- Accents: different shades of green

Please provide:
1. CSS custom properties for the new color palette
2. How to apply them throughout the app
3. Dark mode color variants

Show me the color variable definitions first.
```

**Testing Checklist**:
- [ ] New colors applied consistently
- [ ] Sufficient contrast for readability
- [ ] Dark mode still works
- [ ] Colors match AgriGPT style

---

## **PHASE 5: USER AUTHENTICATION** (Week 7-8)

### Phase 5.1: Django Auth Setup (Day 1-2)
**Goal**: Implement user registration and login

**Tasks**:
1. Create user registration view
2. Create login view
3. Create logout functionality
4. Add password reset

**Files to Create/Modify**:
- `chat/views.py`
- `chat/urls.py`
- Create: `chat/templates/registration/`
- Create: `chat/forms.py`

**LLM Prompt Template**:
```
I'm working on Phase 5.1 - setting up Django authentication.

I need:
1. User registration form (email, password, confirm password)
2. Login form (email/username, password)
3. Password reset flow
4. Proper security (CSRF, password hashing)

Please provide:
1. Forms in forms.py
2. Views in views.py
3. URLs configuration
4. Basic templates

Show ONE component at a time (registration first).
```

**Testing Checklist**:
- [ ] Can register new users
- [ ] Can login with credentials
- [ ] Can logout
- [ ] Password reset emails work (with email backend)
- [ ] Proper error messages

---

### Phase 5.2: User Profile Model (Day 3)
**Goal**: Extend user model with farming info

**Tasks**:
1. Create UserProfile model
2. Add profile fields
3. Create profile edit form

**Files to Create/Modify**:
- `chat/models.py`
- `chat/forms.py`
- Create migrations

**LLM Prompt Template**:
```
I'm working on Phase 5.2 - creating user profile model.

I need a UserProfile model with:
- OneToOne relationship to Django User
- farm_location (state/region)
- farm_size (in hectares)
- primary_crops (text field or M2M)
- language_preference (choices: en, ha, yo, ig)
- phone_number
- created_at, updated_at

Please provide:
1. Model definition
2. Profile creation signal (auto-create on user registration)
3. Migration commands

Show me the model first.
```

**Testing Checklist**:
- [ ] Profile auto-created with new users
- [ ] Can update profile info
- [ ] Data saves correctly
- [ ] Can access profile from user object

---

### Phase 5.3: Profile Page UI (Day 4)
**Goal**: Build user profile interface

**Tasks**:
1. Create profile view page
2. Create profile edit form
3. Add profile picture upload (optional)

**Files to Create**:
- `chat/templates/chat/profile.html`
- `chat/templates/chat/profile_edit.html`
- `chat/static/chat/css/profile.css`

**LLM Prompt Template**:
```
I'm working on Phase 5.3 - building the profile page UI.

I need:
1. Profile view page showing:
   - User's name, email
   - Farm location, size
   - Primary crops
   - Language preference
   - Edit button
   
2. Profile edit form with all fields editable

3. Update view and URL

Design: Clean, modern, match AgriGPT style

Please provide HTML for view page first.
```

**Testing Checklist**:
- [ ] Profile displays all info
- [ ] Can access edit page
- [ ] Updates save correctly
- [ ] Form validation works
- [ ] Responsive on mobile

---

### Phase 5.4: Protect Routes (Day 5)
**Goal**: Add authentication requirements to features

**Tasks**:
1. Add @login_required decorators
2. Redirect unauthenticated users
3. Update navigation for logged-in users

**Files to Modify**:
- `chat/views.py`
- `chat/templates/chat/base.html`

**LLM Prompt Template**:
```
I'm working on Phase 5.4 - protecting routes with authentication.

I need to:
1. Add @login_required to views that need auth
2. Show different navigation for logged-in vs logged-out users
3. Redirect to login with 'next' parameter

Which views should require authentication:
- Chat interface
- Soil nutrition
- Market prices
- Profile

Please show me:
1. How to protect views
2. Updated navigation template
```

**Testing Checklist**:
- [ ] Unauthenticated users redirected to login
- [ ] After login, redirected to intended page
- [ ] Navigation shows correct options
- [ ] Logout works properly

---

## **PHASE 6: SETTINGS & NOTIFICATIONS** (Week 9)

### Phase 6.1: Settings Model & View (Day 1-2)
**Goal**: Create user settings system

**Tasks**:
1. Create UserSettings model
2. Create settings form
3. Create settings page

**Files to Create/Modify**:
- `chat/models.py`
- `chat/forms.py`
- `chat/views.py`
- Create: `chat/templates/chat/settings.html`

**LLM Prompt Template**:
```
I'm working on Phase 6.1 - creating user settings.

UserSettings model should have:
- OneToOne to UserProfile
- notifications_enabled (boolean)
- weather_alerts (boolean)
- price_alerts (boolean)
- pest_alerts (boolean)
- email_notifications (boolean)
- theme_preference (light/dark)

Please provide:
1. Model definition
2. Settings form
3. View to display and update settings
4. URL configuration

Show model first.
```

**Testing Checklist**:
- [ ] Settings save correctly
- [ ] Defaults applied for new users
- [ ] All toggles work
- [ ] Changes reflect in app behavior

---

### Phase 6.2: Notification System Backend (Day 3-4)
**Goal**: Create notification infrastructure

**Tasks**:
1. Create Notification model
2. Create notification creation functions
3. Add notification triggers

**Files to Create/Modify**:
- `chat/models.py`
- Create: `chat/notifications.py`
- Create: `chat/tasks.py` (for scheduled checks)

**LLM Prompt Template**:
```
I'm working on Phase 6.2 - building the notification system.

Notification model should have:
- user (ForeignKey)
- notification_type (weather/price/pest/system)
- title
- message
- is_read (boolean)
- created_at
- related_data (JSONField for extra info)

Please provide:
1. Model definition
2. Function to create notifications
3. Function to mark as read
4. Query functions (get unread count, get recent)

Show model first.
```

**Testing Checklist**:
- [ ] Can create notifications
- [ ] Can query unread notifications
- [ ] Can mark as read
- [ ] Related data stores correctly

---

### Phase 6.3: Notification UI (Day 5)
**Goal**: Build notification bell and panel

**Tasks**:
1. Add notification bell to header
2. Show unread count badge
3. Create notification dropdown panel
4. Real-time updates (polling)

**Files to Create/Modify**:
- `chat/templates/chat/base.html`
- Create: `chat/templates/chat/partials/notifications.html`
- `chat/static/chat/css/notifications.css`
- `chat/static/chat/js/notifications.js`

**LLM Prompt Template**:
```
I'm working on Phase 6.3 - building the notification UI.

I need:
1. Bell icon in header (top-right, next to language switcher)
2. Badge showing unread count
3. Dropdown panel when clicked showing:
   - List of recent notifications
   - Title, message, time ago
   - Mark as read button
   - "View all" link
   
4. Auto-refresh every 30 seconds

Design: Match AgriGPT style

Please provide HTML first.
```

**Testing Checklist**:
- [ ] Bell icon appears in header
- [ ] Badge shows correct count
- [ ] Dropdown opens/closes
- [ ] Notifications display correctly
- [ ] Mark as read works
- [ ] Auto-refresh works

---

## **PHASE 7: CHAT HISTORY & POLISH** (Week 10)

### Phase 7.1: Chat History Backend (Day 1-2)
**Goal**: Save and retrieve chat conversations

**Tasks**:
1. Create ChatConversation and ChatMessage models
2. Save messages automatically
3. Create API to fetch history

**Files to Create/Modify**:
- `chat/models.py`
- `chat/views.py`

**LLM Prompt Template**:
```
I'm working on Phase 7.1 - implementing chat history.

I need:
1. ChatConversation model:
   - user (ForeignKey)
   - title (auto-generated from first message)
   - created_at, updated_at
   
2. ChatMessage model:
   - conversation (ForeignKey)
   - role (user/assistant)
   - content (text)
   - timestamp
   
3. Function to save messages during chat
4. Function to retrieve conversation history

Please provide models first.
```

**Testing Checklist**:
- [ ] Messages save automatically
- [ ] Can retrieve conversation by ID
- [ ] Can list user's conversations
- [ ] Performance is acceptable with many messages

---

### Phase 7.2: Recent Queries Sidebar (Day 3)
**Goal**: Populate sidebar with chat history

**Tasks**:
1. Query recent conversations
2. Display in sidebar
3. Click to load conversation
4. Delete conversation option

**Files to Modify**:
- `chat/templates/chat/base.html`
- `chat/static/chat/js/sidebar.js`

**LLM Prompt Template**:
```
I'm working on Phase 7.2 - showing recent queries in sidebar.

I need to:
1. Fetch user's last 5 conversations
2. Display them in sidebar under "Recent Queries"
3. Each item shows:
   - Icon (based on topic)
   - Truncated title
   - Click to load that conversation
   
4. "New Chat" button starts fresh conversation

Please provide:
1. View to fetch recent conversations
2. Updated sidebar template
3. JavaScript to handle loading

Show the view first.
```

**Testing Checklist**:
- [ ] Recent conversations appear in sidebar
- [ ] Clicking loads correct conversation
- [ ] New Chat button works
- [ ] List updates when new chat started

---

### Phase 7.3: Final UI Polish (Day 4-5)
**Goal**: Add finishing touches and animations

**Tasks**:
1. Add loading spinners
2. Add smooth transitions
3. Improve error messages
4. Add success notifications
5. Test on multiple devices

**Files to Modify**:
- Various CSS files
- Various JS files

**LLM Prompt Template**:
```
I'm working on Phase 7.3 - final UI polish.

Please help me add:
1. Loading spinner component (reusable)
2. Smooth fade-in animations for content
3. Toast notifications for success/error messages
4. Skeleton loaders for content loading

Show me the loading spinner component first.
```

**Testing Checklist**:
- [ ] All async operations show loading
- [ ] Animations are smooth
- [ ] No jarring transitions
- [ ] Error messages are friendly
- [ ] Success feedback is clear

---

## **PHASE 8: TESTING & DEPLOYMENT** (Week 11-12)

### Phase 8.1: Testing (Day 1-3)
**Goal**: Comprehensive testing

**Tasks**:
1. Test all features in each language
2. Test on different devices
3. Test with different user types
4. Fix bugs

**Testing Checklist**:
- [ ] All features work in English
- [ ] All features work in Hausa/Yoruba/Igbo
- [ ] Mobile responsive (iPhone, Android)
- [ ] Tablet responsive
- [ ] Desktop (different browsers)
- [ ] Forms validate correctly
- [ ] No console errors
- [ ] Good performance (page load < 3s)

---

### Phase 8.2: Production Setup (Day 4-5)
**Goal**: Prepare for deployment

**Tasks**:
1. Set up production environment
2. Configure environment variables
3. Set up database (PostgreSQL)
4. Configure static files
5. Set up SSL

**LLM Prompt Template**:
```
I'm working on Phase 8.2 - production deployment setup.

I'm deploying to [Heroku/DigitalOcean/AWS - specify].

Please help me:
1. Update settings.py for production
2. Create requirements.txt for production
3. Set up environment variables (.env.example)
4. Configure static files (WhiteNoise or S3)
5. Provide deployment checklist

Show me settings.py changes first.
```

**Testing Checklist**:
- [ ] Production settings configured
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Static files serve correctly
- [ ] HTTPS works
- [ ] Can access site via domain

---

### Phase 8.3: Monitoring & Launch (Day 6-7)
**Goal**: Set up monitoring and go live

**Tasks**:
1. Set up error tracking (Sentry)
2. Configure logging
3. Set up uptime monitoring
4. Create backup strategy
5. Launch!

**LLM Prompt Template**:
```
I'm working on Phase 8.3 - setting up monitoring for production.

Please help me:
1. Integrate Sentry for error tracking
2. Set up Django logging configuration
3. Recommend uptime monitoring tools
4. Create database backup script

Show me Sentry integration first.
```

**Testing Checklist**:
- [ ] Error tracking works
- [ ] Logs are being captured
- [ ] Uptime monitoring active
- [ ] Backups running
- [ ] Ready for users!

---

## 📝 QUICK REFERENCE: COMMAND CHECKLIST

### After Each Phase:
```bash
# 1. Test your changes
python manage.py runserver

# 2. Create/run migrations (if models changed)
python manage.py makemigrations
python manage.py migrate

# 3. Collect static files (if CSS/JS changed)
python manage.py collectstatic --noinput

# 4. Commit to Git
git add .
git commit -m "Phase X.Y: [description]"
git push
```

### Before Starting a New Phase:
```bash
# 1. Make sure you're on latest
git pull

# 2. Create a branch (optional but recommended)
git checkout -b phase-X-Y

# 3. Check everything still works
python manage.py runserver
```

---

## 🎯 TIPS FOR WORKING WITH LLM

### Do's:
✅ Copy ONE phase at a time to your LLM
✅ Provide context about your current file structure
✅ Ask for explanations of complex code
✅ Request code in small, testable chunks
✅ Test thoroughly before moving to next phase
✅ Commit after each successful phase

### Don'ts:
❌ Don't ask LLM to build everything at once
❌ Don't skip testing between phases
❌ Don't move on if something doesn't work
❌ Don't forget to commit your work
❌ Don't paste enormous code blocks without context

### When You Get Stuck:
1. Test in isolation (create a simple test file)
2. Check Django error messages carefully
3. Ask LLM: "This isn't working: [error]. What's wrong?"
4. Google the specific error message
5. Check Django documentation
6. Take a break and come back fresh!

---

## 🎉 FINAL NOTES

### Success Metrics:
- [ ] All 4 languages work perfectly
- [ ] Soil nutrition feature functional
- [ ] Market prices feature functional  
- [ ] UI matches AgriGPT style
- [ ] User authentication works
- [ ] Settings and notifications work
- [ ] Mobile responsive
- [ ] No critical bugs
- [ ] Good performance
- [ ] Ready for real users!

### Remember:
- Quality over speed
- Test everything
- Commit often
- Don't get overwhelmed
- One phase at a time!

**You've got this! 🚀🌾**
