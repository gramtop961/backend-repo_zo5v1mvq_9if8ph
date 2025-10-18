# Database Usage Guide

This guide covers how to use MongoDB with your Flames application, including setup, common patterns, and best practices.

## Getting Started

### 1. Database Availability

MongoDB is automatically available in every Flames project. You can start using it immediately without any setup.

```python
# The database is automatically configured and the following are available:
from database import db, create_document, get_documents, update_document, delete_document
```

### 2. Basic Operations

#### Creating Documents
```python
# Using helper function (recommended)
user_id = create_document("users", {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})

# Using direct MongoDB access
from database import db
result = db.users.insert_one({
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "created_at": datetime.utcnow()
})
user_id = str(result.inserted_id)
```

#### Reading Documents
```python
# Get all documents
users = get_documents("users")

# Get with filter
young_users = get_documents("users", {"age": {"$lt": 25}})

# Get with limit
recent_users = get_documents("users", limit=10)

# Using direct MongoDB access
from database import db
users = list(db.users.find({"age": {"$gte": 18}}))
```

#### Updating Documents
```python
# Using helper function
success = update_document("users", {"email": "john@example.com"}, {"age": 31})

# Using direct MongoDB access
from database import db
from bson import ObjectId
result = db.users.update_one(
    {"_id": ObjectId(user_id)},
    {"$set": {"age": 31, "updated_at": datetime.utcnow()}}
)
```

#### Deleting Documents
```python
# Using helper function
success = delete_document("users", {"email": "john@example.com"})

# Using direct MongoDB access
from database import db
from bson import ObjectId
result = db.users.delete_one({"_id": ObjectId(user_id)})
```

## Common Patterns

### 1. User Management
```python
def create_user(name: str, email: str):
    # Check if user exists
    existing = get_documents("users", {"email": email})
    if existing:
        raise ValueError("User already exists")
    
    user_data = {
        "name": name,
        "email": email,
        "status": "active",
        "profile": {
            "avatar_url": None,
            "bio": "",
            "preferences": {}
        }
    }
    return create_document("users", user_data)

def get_user_by_email(email: str):
    users = get_documents("users", {"email": email})
    return users[0] if users else None
```

### 2. Content Management (Blog/CMS)
```python
def create_post(title: str, content: str, author_id: str):
    post_data = {
        "title": title,
        "content": content,
        "author_id": author_id,
        "slug": title.lower().replace(" ", "-"),
        "status": "draft",
        "tags": [],
        "view_count": 0,
        "comments": []
    }
    return create_document("posts", post_data)

def publish_post(post_id: str):
    from bson import ObjectId
    return update_document("posts", {"_id": ObjectId(post_id)}, {"status": "published"})
```

### 3. E-commerce
```python
def create_product(name: str, price: float, category: str):
    product_data = {
        "name": name,
        "price": price,
        "category": category,
        "sku": f"PROD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "stock": 0,
        "status": "active",
        "rating": {"average": 0.0, "count": 0}
    }
    return create_document("products", product_data)

def create_order(customer_id: str, items: list):
    total = sum(item["price"] * item["quantity"] for item in items)
    order_data = {
        "customer_id": customer_id,
        "items": items,
        "total_amount": total,
        "status": "pending",
        "order_number": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }
    return create_document("orders", order_data)
```

### 4. Task Management
```python
def create_project(name: str, owner_id: str):
    project_data = {
        "name": name,
        "owner_id": owner_id,
        "members": [owner_id],
        "status": "active",
        "task_count": 0,
        "progress": 0
    }
    return create_document("projects", project_data)

def create_task(title: str, project_id: str, assignee_id: str = None):
    task_data = {
        "title": title,
        "project_id": project_id,
        "assignee_id": assignee_id,
        "status": "todo",
        "priority": "medium",
        "due_date": None
    }
    return create_document("tasks", task_data)
```

## Advanced MongoDB Operations

### Aggregation Pipeline
```python
from database import db

# Group and count
pipeline = [
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
category_counts = list(db.products.aggregate(pipeline))

# Match and project
pipeline = [
    {"$match": {"status": "published"}},
    {"$project": {"title": 1, "view_count": 1, "created_at": 1}},
    {"$sort": {"view_count": -1}},
    {"$limit": 10}
]
popular_posts = list(db.posts.aggregate(pipeline))
```

### Text Search
```python
from database import db

# Create text index (do this once)
db.posts.create_index([("title", "text"), ("content", "text")])

# Search
results = list(db.posts.find({"$text": {"$search": "python mongodb"}}))
```

### Geospatial Queries
```python
from database import db

# Create geospatial index
db.locations.create_index([("coordinates", "2dsphere")])

# Find nearby locations
nearby = list(db.locations.find({
    "coordinates": {
        "$near": {
            "$geometry": {"type": "Point", "coordinates": [-73.99, 40.75]},
            "$maxDistance": 1000  # meters
        }
    }
}))
```

## Schema Design Best Practices

### 1. Document Structure
```python
# Good: Embedded documents for related data
user_document = {
    "_id": ObjectId(),
    "name": "John Doe",
    "email": "john@example.com",
    "profile": {
        "avatar_url": "https://...",
        "bio": "Software developer",
        "social_links": {
            "twitter": "@johndoe",
            "linkedin": "johndoe"
        }
    },
    "preferences": {
        "theme": "dark",
        "notifications": True
    },
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}
```

### 2. Reference vs Embed
```python
# Embed: When data is frequently accessed together
blog_post = {
    "title": "My Post",
    "content": "...",
    "author": {  # Embedded author info
        "name": "John Doe",
        "email": "john@example.com"
    },
    "comments": [  # Embedded comments (if not too many)
        {
            "author": "Jane",
            "text": "Great post!",
            "created_at": datetime.utcnow()
        }
    ]
}

# Reference: When data is large or updated independently
order = {
    "order_number": "ORD-123",
    "customer_id": ObjectId("..."),  # Reference to customer
    "items": [
        {
            "product_id": ObjectId("..."),  # Reference to product
            "quantity": 2,
            "price": 29.99
        }
    ]
}
```

### 3. Indexing Strategy
```python
from database import db

# Single field index
db.users.create_index("email", unique=True)

# Compound index
db.posts.create_index([("author_id", 1), ("created_at", -1)])

# Text index for search
db.posts.create_index([("title", "text"), ("content", "text")])

# TTL index for automatic deletion
db.sessions.create_index("created_at", expireAfterSeconds=3600)
```

## Error Handling

### Connection Errors
```python
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

try:
    result = create_document("users", user_data)
except ConnectionFailure:
    # Handle connection issues
    return {"error": "Database connection failed"}
except Exception as e:
    # Handle other database errors
    return {"error": f"Database error: {str(e)}"}
```

### Validation Errors
```python
from pymongo.errors import DuplicateKeyError

try:
    user_id = create_document("users", {"email": "john@example.com"})
except DuplicateKeyError:
    return {"error": "Email already exists"}
```

## Performance Tips

### 1. Use Indexes
```python
# Always index frequently queried fields
db.users.create_index("email")
db.posts.create_index([("author_id", 1), ("created_at", -1)])
```

### 2. Limit Document Size
```python
# Keep documents under 16MB
# For large arrays, consider separate collections
# Instead of embedding all comments in a post:
post = {"title": "...", "content": "...", "comment_count": 150}
# Store comments separately:
comment = {"post_id": post_id, "author": "...", "text": "..."}
```

### 3. Use Projection
```python
# Only get fields you need
users = list(db.users.find({}, {"name": 1, "email": 1, "_id": 0}))
```

### 4. Batch Operations
```python
# Insert many documents at once
users_data = [{"name": f"User {i}"} for i in range(100)]
db.users.insert_many(users_data)

# Bulk write operations
from pymongo import UpdateOne
operations = [
    UpdateOne({"_id": ObjectId(id)}, {"$set": {"status": "active"}})
    for id in user_ids
]
db.users.bulk_write(operations)
```

## Available Examples

The following files contain database patterns and examples:

- **schema_examples.py** - Common schema patterns and helper functions
- **DATABASE_GUIDE.md** - This comprehensive guide with examples

## Useful Resources

- **schema_examples.py** - Common schema patterns and functions
- **MongoDB Documentation**: https://docs.mongodb.com/
- **PyMongo Documentation**: https://pymongo.readthedocs.io/
- **MongoDB Query Operators**: https://docs.mongodb.com/manual/reference/operator/query/

## Troubleshooting

### Common Issues

1. **Import errors**: Use `from database import db` to access the database
2. **ObjectId errors**: Import with `from bson import ObjectId`
3. **Connection timeout**: Check your internet connection and database availability

### Getting Help

If you encounter issues:
1. Check the error message for specific details
2. Verify your database connection is working
3. Review the schema examples for similar patterns
4. Check MongoDB documentation for specific query syntax