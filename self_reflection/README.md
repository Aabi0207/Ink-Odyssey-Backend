# Self-Reflection Module

A flexible self-reflection system for tracking daily thoughts, moods, and personal metrics through customizable questions.

## Features

### ✨ Key Capabilities
- **Flexible Question Types**: Support for range (1-10), multiple choice, and text responses
- **Daily Tracking**: One reflection entry per user per day
- **Custom Questions**: Add, edit, or deactivate questions as needed
- **Statistics & Analytics**: Track averages, trends, and streaks
- **Category Organization**: Group questions by categories (Wellness, Productivity, etc.)
- **RESTful API**: Complete CRUD operations with JWT authentication

## Models

### 1. ReflectionQuestion
Represents a self-reflection question that users answer daily.

**Fields:**
- `question_text`: The question to display (max 500 chars)
- `question_type`: Type of question (`range`, `choice`, or `text`)
- `min_value`: Minimum value for range questions (default: 1)
- `max_value`: Maximum value for range questions (default: 10)
- `choices`: Array of options for multiple choice questions
- `is_active`: Whether the question is currently active
- `order`: Display order for sorting
- `category`: Optional category for grouping questions

**Question Types:**

1. **Range Questions** (1-10 scale)
   ```json
   {
     "question_text": "Rate your day out of 10",
     "question_type": "range",
     "min_value": 1,
     "max_value": 10
   }
   ```

2. **Multiple Choice**
   ```json
   {
     "question_text": "Mood of the day",
     "question_type": "choice",
     "choices": ["Happy", "Sad", "Neutral", "Excited", "Anxious"]
   }
   ```

3. **Text Response**
   ```json
   {
     "question_text": "What are you grateful for today?",
     "question_type": "text"
   }
   ```

### 2. SelfReflection
Represents a user's daily reflection entry.

**Fields:**
- `user`: Foreign key to User
- `date`: Date of the reflection
- `notes`: Optional additional thoughts
- `responses`: Related ReflectionResponse objects

**Constraints:**
- One reflection per user per day (unique together: user + date)

### 3. ReflectionResponse
Represents a user's answer to a specific question.

**Fields:**
- `daily_reflection`: Foreign key to SelfReflection
- `question`: Foreign key to ReflectionQuestion
- `range_response`: Integer value for range questions (1-10)
- `choice_response`: Selected option for choice questions
- `text_response`: Text answer for text questions

**Constraints:**
- One response per question per reflection (unique together: daily_reflection + question)

## API Endpoints

### Questions Management

#### List Questions
```http
GET /api/self-reflection/questions/
GET /api/self-reflection/questions/?is_active=true
GET /api/self-reflection/questions/?category=Wellness
```

#### Get Active Questions
```http
GET /api/self-reflection/questions/active/
```

#### Create Question
```http
POST /api/self-reflection/questions/
Content-Type: application/json

{
  "question_text": "How many hours did you sleep?",
  "question_type": "range",
  "min_value": 0,
  "max_value": 12,
  "category": "Health",
  "order": 1
}
```

#### Update Question
```http
PUT /api/self-reflection/questions/{id}/
PATCH /api/self-reflection/questions/{id}/
```

#### Delete Question
```http
DELETE /api/self-reflection/questions/{id}/
```

### Reflections Management

#### Create/Update Daily Reflection
```http
POST /api/self-reflection/reflections/
Content-Type: application/json

{
  "date": "2025-12-02",
  "notes": "Had a great day!",
  "responses": [
    {
      "question_id": 1,
      "range_response": 8
    },
    {
      "question_id": 2,
      "choice_response": "Happy"
    },
    {
      "question_id": 3,
      "text_response": "I'm grateful for my health and family."
    }
  ]
}
```

#### Get Today's Reflection
```http
GET /api/self-reflection/reflections/today/
```

#### Get Reflection by Date
```http
GET /api/self-reflection/reflections/by_date/?date=2025-12-01
```

#### Get Reflections for Date Range
```http
GET /api/self-reflection/reflections/date_range/?start_date=2025-11-01&end_date=2025-11-30
```

#### Get All User Reflections
```http
GET /api/self-reflection/reflections/
```

#### Get Statistics
```http
GET /api/self-reflection/reflections/stats/?days=30
```

**Response:**
```json
{
  "total_reflections": 25,
  "days_analyzed": 30,
  "current_streak": 7,
  "question_averages": [
    {
      "question_id": 1,
      "question_text": "Rate your day out of 10",
      "average": 7.5,
      "count": 25
    }
  ]
}
```

#### Get Current Streak
```http
GET /api/self-reflection/reflections/streak/
```

**Response:**
```json
{
  "current_streak": 7
}
```

## Setup

### 1. Install App
The app is already added to `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'self_reflection',
]
```

### 2. Run Migrations
```bash
python manage.py makemigrations self_reflection
python manage.py migrate
```

### 3. Add URLs
Already configured in main `urls.py`:
```python
path("api/self-reflection/", include('self_reflection.urls')),
```

### 4. Create Sample Questions
Use Django admin or API to create questions:

**Via Django Admin:**
1. Go to `http://localhost:8000/admin/`
2. Navigate to "Self Reflection" → "Reflection Questions"
3. Click "Add Reflection Question"
4. Fill in the form and save

**Via API:**
```bash
# See test_self_reflection_api.py for examples
python test_self_reflection_api.py
```

## Usage Examples

### Frontend Integration

#### 1. Fetch Active Questions for Form
```javascript
const response = await fetch('/api/self-reflection/questions/active/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const questions = await response.json();
```

#### 2. Render Dynamic Form
```javascript
questions.forEach(question => {
  if (question.question_type === 'range') {
    // Render slider/number input
    return (
      <input 
        type="range" 
        min={question.min_value} 
        max={question.max_value}
        name={`q_${question.id}`}
      />
    );
  } else if (question.question_type === 'choice') {
    // Render dropdown/radio buttons
    return (
      <select name={`q_${question.id}`}>
        {question.choices.map(choice => (
          <option value={choice}>{choice}</option>
        ))}
      </select>
    );
  } else if (question.question_type === 'text') {
    // Render textarea
    return (
      <textarea name={`q_${question.id}`} />
    );
  }
});
```

#### 3. Check if Reflection Exists
```javascript
try {
  const response = await fetch('/api/self-reflection/reflections/today/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  if (response.ok) {
    const todayReflection = await response.json();
    // Pre-fill form with existing data
    todayReflection.responses.forEach(r => {
      // Set form values
    });
  }
} catch (error) {
  // No reflection for today, show empty form
}
```

#### 4. Submit Reflection
```javascript
const formData = {
  date: new Date().toISOString().split('T')[0],
  notes: notesTextarea.value,
  responses: questions.map(q => {
    const response = { question_id: q.id };
    
    if (q.question_type === 'range') {
      response.range_response = parseInt(formInputs[`q_${q.id}`]);
    } else if (q.question_type === 'choice') {
      response.choice_response = formInputs[`q_${q.id}`];
    } else if (q.question_type === 'text') {
      response.text_response = formInputs[`q_${q.id}`];
    }
    
    return response;
  })
};

await fetch('/api/self-reflection/reflections/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(formData)
});
```

#### 5. Display Statistics
```javascript
const stats = await fetch('/api/self-reflection/reflections/stats/?days=30', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
}).then(r => r.json());

// Display averages
stats.question_averages.forEach(qa => {
  console.log(`${qa.question_text}: ${qa.average}/10`);
});

// Display streak
console.log(`${stats.current_streak} day streak!`);
```

## Admin Interface

The Django admin interface provides full CRUD operations for all models:

### ReflectionQuestion Admin
- List view with filters by type, status, and category
- Inline editing for `is_active` and `order` fields
- Search by question text and category

### SelfReflection Admin
- List view with user, date, and timestamps
- Inline responses for quick editing
- Date hierarchy navigation
- Search by user email and notes

### ReflectionResponse Admin
- List view showing user, question, and response value
- Smart response display based on question type
- Filters by question type and date

## Testing

### Run Test Script
```bash
cd backend
python test_self_reflection_api.py
```

The test script will:
1. Register/login a test user
2. Create sample questions
3. Create reflections for today and past 7 days
4. Query reflections in various ways
5. Display statistics and streak

### Manual Testing with cURL

**Create a question:**
```bash
curl -X POST http://localhost:8000/api/self-reflection/questions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Energy level",
    "question_type": "choice",
    "choices": ["Very Low", "Low", "Medium", "High", "Very High"]
  }'
```

**Create a reflection:**
```bash
curl -X POST http://localhost:8000/api/self-reflection/reflections/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-02",
    "notes": "Great day!",
    "responses": [
      {"question_id": 1, "range_response": 8},
      {"question_id": 2, "choice_response": "Happy"}
    ]
  }'
```

## Best Practices

### 1. Question Design
- Keep questions clear and concise
- Use appropriate question types for the data you want to collect
- Set meaningful categories for better organization
- Use the `order` field to control display sequence

### 2. Data Collection
- Encourage daily submissions for better insights
- Use range questions for quantitative tracking
- Use choice questions for categorical data
- Use text questions sparingly (harder to analyze)

### 3. Frontend UX
- Show questions in order
- Pre-fill existing reflections when editing
- Validate responses before submission
- Show streak count to encourage consistency
- Display trends and averages for motivation

### 4. Analytics
- Use the stats endpoint to show progress
- Calculate weekly/monthly averages
- Visualize trends with charts
- Celebrate streaks and milestones

## Common Use Cases

### 1. Daily Wellness Check
```json
[
  {"question_text": "Rate your day", "question_type": "range"},
  {"question_text": "Mood", "question_type": "choice", "choices": ["Happy", "Sad", "Neutral"]},
  {"question_text": "Energy level", "question_type": "range"},
  {"question_text": "Hours of sleep", "question_type": "range", "min_value": 0, "max_value": 12}
]
```

### 2. Productivity Tracker
```json
[
  {"question_text": "Productivity level", "question_type": "range"},
  {"question_text": "Tasks completed", "question_type": "range", "min_value": 0, "max_value": 20},
  {"question_text": "Focus quality", "question_type": "choice", "choices": ["Poor", "Fair", "Good", "Excellent"]}
]
```

### 3. Gratitude Journal
```json
[
  {"question_text": "What are you grateful for?", "question_type": "text"},
  {"question_text": "Who made you smile today?", "question_type": "text"}
]
```

### 4. Health Metrics
```json
[
  {"question_text": "Glasses of water", "question_type": "range", "min_value": 0, "max_value": 15},
  {"question_text": "Exercise minutes", "question_type": "range", "min_value": 0, "max_value": 180},
  {"question_text": "Meal quality", "question_type": "choice", "choices": ["Poor", "Fair", "Good", "Excellent"]}
]
```

## Permissions

All endpoints require JWT authentication. Users can only:
- View and manage their own reflections
- View all questions (create/update/delete restricted to staff/admin)

To modify question permissions, update the `ReflectionQuestionViewSet` permission classes in `views.py`.

## Database Schema

```
ReflectionQuestion
├── id (PK)
├── question_text
├── question_type
├── min_value
├── max_value
├── choices (JSON)
├── is_active
├── order
├── category
├── created_at
└── updated_at

SelfReflection
├── id (PK)
├── user_id (FK → User)
├── date
├── notes
├── created_at
└── updated_at
    └── UNIQUE(user_id, date)

ReflectionResponse
├── id (PK)
├── daily_reflection_id (FK → SelfReflection)
├── question_id (FK → ReflectionQuestion)
├── range_response
├── choice_response
├── text_response
├── created_at
└── updated_at
    └── UNIQUE(daily_reflection_id, question_id)
```

## Future Enhancements

Potential improvements:
- [ ] Question scheduling (show certain questions on specific days)
- [ ] Reminder notifications
- [ ] Data export (CSV, PDF)
- [ ] Advanced analytics dashboard
- [ ] Question templates/presets
- [ ] Team/group reflections
- [ ] AI-powered insights
- [ ] Mood trends visualization
- [ ] Integration with other apps (diary, habits)

## Support

For issues or questions:
1. Check the API documentation: `API_DOCUMENTATION.md`
2. Review test examples: `test_self_reflection_api.py`
3. Check Django admin for data verification
4. Enable DEBUG mode to see detailed error messages

## License

Part of the InkOdyssey project.
