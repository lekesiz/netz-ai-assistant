# NETZ AI API Documentation

## Authentication
All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Public Endpoints
- `GET /health` - Health check
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Protected Endpoints
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - User logout
- `PUT /api/auth/profile` - Update profile
- `PUT /api/auth/password` - Change password

### Admin Endpoints (Admin only)
- `GET /api/admin/dashboard` - Complete dashboard data
- `GET /api/admin/dashboard/system` - System metrics
- `GET /api/admin/dashboard/ai` - AI performance
- `GET /api/admin/dashboard/business` - Business metrics
- `GET /api/admin/users` - List all users
- `GET /api/admin/stats` - System statistics

## Rate Limiting
- 60 requests per minute per IP
- Burst allowance of 10 requests
- Admin endpoints have higher limits

## Response Format
All API responses follow this format:
```json
{
  "success": true,
  "message": "Optional message",
  "data": {...},
  "error": "Optional error message"
}
```
