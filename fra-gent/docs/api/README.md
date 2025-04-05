# Fra-Gent API Documentation

This document provides an overview of the Fra-Gent API endpoints and how to use them.

## API Overview

The Fra-Gent API is a RESTful API that provides access to all Fra-Gent functionality, including:

- Agent management
- Workflow management
- Execution control
- Knowledge base management
- User management

## Authentication

All API requests require authentication using JWT tokens.

### Getting a Token

```http
POST /api/auth/token
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

### Using a Token

Include the token in the `Authorization` header of all requests:

```http
GET /api/agents
Authorization: Bearer your_token_here
```

## Agents API

### List Agents

```http
GET /api/agents
```

Response:

```json
{
  "agents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Customer Support Agent",
      "description": "Handles customer inquiries",
      "model": "gpt-4",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z"
    },
    ...
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

### Get Agent

```http
GET /api/agents/{agent_id}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Agent",
  "description": "Handles customer inquiries",
  "model": "gpt-4",
  "system_prompt": "You are a helpful customer support agent...",
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "knowledge_bases": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Product Documentation"
    }
  ],
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z"
}
```

### Create Agent

```http
POST /api/agents
Content-Type: application/json

{
  "name": "Customer Support Agent",
  "description": "Handles customer inquiries",
  "model": "gpt-4",
  "system_prompt": "You are a helpful customer support agent...",
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "knowledge_base_ids": ["550e8400-e29b-41d4-a716-446655440001"]
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Agent",
  "description": "Handles customer inquiries",
  "model": "gpt-4",
  "system_prompt": "You are a helpful customer support agent...",
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "knowledge_bases": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Product Documentation"
    }
  ],
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z"
}
```

### Update Agent

```http
PUT /api/agents/{agent_id}
Content-Type: application/json

{
  "name": "Updated Customer Support Agent",
  "description": "Handles customer inquiries and complaints",
  "system_prompt": "You are a helpful customer support agent...",
  "temperature": 0.5
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Customer Support Agent",
  "description": "Handles customer inquiries and complaints",
  "model": "gpt-4",
  "system_prompt": "You are a helpful customer support agent...",
  "temperature": 0.5,
  "max_tokens": 1000,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "knowledge_bases": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Product Documentation"
    }
  ],
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T13:00:00Z"
}
```

### Delete Agent

```http
DELETE /api/agents/{agent_id}
```

Response:

```json
{
  "success": true,
  "message": "Agent deleted successfully"
}
```

### Execute Agent

```http
POST /api/agents/{agent_id}/execute
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "How do I reset my password?"
    }
  ]
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "How do I reset my password?"
    },
    {
      "role": "assistant",
      "content": "To reset your password, please follow these steps:\n\n1. Go to the login page\n2. Click on 'Forgot Password'\n3. Enter your email address\n4. Check your email for a reset link\n5. Click the link and enter a new password"
    }
  ],
  "created_at": "2023-06-01T14:00:00Z",
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 60,
    "total_tokens": 80
  }
}
```

## Workflows API

### List Workflows

```http
GET /api/workflows
```

Response:

```json
{
  "workflows": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "name": "Customer Onboarding",
      "description": "Process new customer registrations",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z"
    },
    ...
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

### Get Workflow

```http
GET /api/workflows/{workflow_id}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "name": "Customer Onboarding",
  "description": "Process new customer registrations",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440000",
        "position": { "x": 100, "y": 100 }
      },
      {
        "id": "node2",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440001",
        "position": { "x": 400, "y": 100 }
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "type": "data"
      }
    ]
  },
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z"
}
```

### Create Workflow

```http
POST /api/workflows
Content-Type: application/json

{
  "name": "Customer Onboarding",
  "description": "Process new customer registrations",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440000",
        "position": { "x": 100, "y": 100 }
      },
      {
        "id": "node2",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440001",
        "position": { "x": 400, "y": 100 }
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "type": "data"
      }
    ]
  }
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "name": "Customer Onboarding",
  "description": "Process new customer registrations",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440000",
        "position": { "x": 100, "y": 100 }
      },
      {
        "id": "node2",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440001",
        "position": { "x": 400, "y": 100 }
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "type": "data"
      }
    ]
  },
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z"
}
```

### Update Workflow

```http
PUT /api/workflows/{workflow_id}
Content-Type: application/json

{
  "name": "Updated Customer Onboarding",
  "description": "Process new customer registrations and setup",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440000",
        "position": { "x": 100, "y": 100 }
      },
      {
        "id": "node2",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440001",
        "position": { "x": 400, "y": 100 }
      },
      {
        "id": "node3",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440002",
        "position": { "x": 700, "y": 100 }
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "type": "data"
      },
      {
        "id": "edge2",
        "source": "node2",
        "target": "node3",
        "type": "data"
      }
    ]
  }
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "name": "Updated Customer Onboarding",
  "description": "Process new customer registrations and setup",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440000",
        "position": { "x": 100, "y": 100 }
      },
      {
        "id": "node2",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440001",
        "position": { "x": 400, "y": 100 }
      },
      {
        "id": "node3",
        "type": "agent",
        "agent_id": "550e8400-e29b-41d4-a716-446655440002",
        "position": { "x": 700, "y": 100 }
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "type": "data"
      },
      {
        "id": "edge2",
        "source": "node2",
        "target": "node3",
        "type": "data"
      }
    ]
  },
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T13:00:00Z"
}
```

### Delete Workflow

```http
DELETE /api/workflows/{workflow_id}
```

Response:

```json
{
  "success": true,
  "message": "Workflow deleted successfully"
}
```

### Execute Workflow

```http
POST /api/workflows/{workflow_id}/execute
Content-Type: application/json

{
  "inputs": {
    "node1": {
      "message": "I'd like to sign up for your service"
    }
  }
}
```

Response:

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440004",
  "workflow_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "running",
  "start_time": "2023-06-01T14:00:00Z"
}
```

### Get Execution Status

```http
GET /api/executions/{execution_id}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "workflow_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "completed",
  "start_time": "2023-06-01T14:00:00Z",
  "end_time": "2023-06-01T14:01:00Z",
  "node_results": {
    "node1": {
      "status": "completed",
      "output": {
        "message": "Thank you for your interest! I'll help you sign up."
      }
    },
    "node2": {
      "status": "completed",
      "output": {
        "message": "I've created your account. Your username is user123."
      }
    },
    "node3": {
      "status": "completed",
      "output": {
        "message": "Welcome email sent to your address."
      }
    }
  },
  "final_output": {
    "message": "Welcome email sent to your address."
  }
}
```

## Knowledge Base API

### List Knowledge Bases

```http
GET /api/knowledge-bases
```

Response:

```json
{
  "knowledge_bases": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "name": "Product Documentation",
      "description": "Documentation for all products",
      "type": "document",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z"
    },
    ...
  ],
  "total": 3,
  "page": 1,
  "page_size": 20
}
```

### Get Knowledge Base

```http
GET /api/knowledge-bases/{knowledge_base_id}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440005",
  "name": "Product Documentation",
  "description": "Documentation for all products",
  "type": "document",
  "document_count": 10,
  "chunk_count": 150,
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z"
}
```

### Create Knowledge Base

```http
POST /api/knowledge-bases
Content-Type: application/json

{
  "name": "Product Documentation",
  "description": "Documentation for all products",
  "type": "document"
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440005",
  "name": "Product Documentation",
  "description": "Documentation for all products",
  "type": "document",
  "document_count": 0,
  "chunk_count": 0,
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z"
}
```

### Upload Document to Knowledge Base

```http
POST /api/knowledge-bases/{knowledge_base_id}/documents
Content-Type: multipart/form-data

file: [binary file data]
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "knowledge_base_id": "550e8400-e29b-41d4-a716-446655440005",
  "filename": "product_manual.pdf",
  "mime_type": "application/pdf",
  "size": 1024000,
  "chunk_count": 15,
  "status": "processing",
  "created_at": "2023-06-01T12:00:00Z"
}
```

### Query Knowledge Base

```http
POST /api/knowledge-bases/{knowledge_base_id}/query
Content-Type: application/json

{
  "query": "How do I reset my password?",
  "limit": 5,
  "threshold": 0.7
}
```

Response:

```json
{
  "results": [
    {
      "content": "To reset your password, go to the login page and click 'Forgot Password'. Enter your email address to receive a reset link.",
      "metadata": {
        "source": "product_manual.pdf",
        "page": 5
      },
      "score": 0.92
    },
    ...
  ]
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with details:

```json
{
  "error": {
    "code": "invalid_input",
    "message": "Invalid input parameters",
    "details": {
      "name": "Name is required"
    }
  }
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. The limits are:

- 100 requests per minute per user
- 1000 requests per hour per user

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1622548800
```

## Pagination

List endpoints support pagination using the following query parameters:

- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)

Pagination information is included in the response:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

## Filtering and Sorting

List endpoints support filtering and sorting using query parameters:

- `sort`: Field to sort by (e.g., `created_at`)
- `order`: Sort order (`asc` or `desc`)
- `filter_field`: Field to filter by (e.g., `name`)
- `filter_value`: Value to filter by (e.g., `Customer`)

Example:

```http
GET /api/agents?sort=created_at&order=desc&filter_field=name&filter_value=Customer
```
