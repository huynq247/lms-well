# LearnHub-Frontend: Admin Features Implementation Guide

## Current Status

### ✅ Completed
1. **Backend Integration** - API client, config, interceptors
2. **Authentication Service** - Login, logout, user management
3. **Content Service** - Courses and lessons CRUD
4. **User Service** - User management CRUD
5. **Assignment Service** - Assignment management
6. **AuthContext** - React context for authentication state
7. **Basic Pages** - Login, Dashboard skeleton
8. **Docker Setup** - Dockerfile, nginx config, docker-compose entry

### 🔄 To Be Completed

## Admin Features from frontend-admin

The existing `frontend-admin` has these key features that need to be replicated:

### 1. User Management (`/users`)
**Features:**
- List all users (students, teachers, admins)
- Create new users with role selection
- Edit user details
- Delete users
- Filter by role
- Role-based access (Admin only)

**Components Needed:**
- `src/pages/admin/UserManagement.tsx`
- Table with user data
- Create/Edit dialog
- Delete confirmation
- Role badges

### 2. Course Management (`/courses`)
**Features:**
- List all courses
- Create new course
- Edit course details
- Delete course
- View course lessons
- Role-based filtering (teachers see only their courses)

**Components Needed:**
- `src/pages/admin/CoursesPage.tsx`
- `src/pages/admin/CourseDetail.tsx`
- Course cards/table
- Create/Edit dialog
- Lessons list within course

### 3. Lesson Management (`/lessons`)
**Features:**
- List all lessons across courses
- Create lesson (select course)
- Edit lesson content
- Delete lesson
- Reorder lessons
- Add video URLs

**Components Needed:**
- `src/pages/admin/LessonsPage.tsx`
- Lesson table
- Create/Edit dialog with rich text editor
- Video URL input

### 4. Flashcard Deck Management (`/decks`)
**Features:**
- List flashcard decks
- Create deck
- Edit deck
- Add/remove flashcards
- Study mode
- AI flashcard generator

**Components Needed:**
- `src/pages/admin/DecksPage.tsx`
- `src/pages/admin/DeckDetail.tsx`
- `src/pages/admin/FlashcardStudy.tsx`
- AI creator integration

### 5. Dashboard (`/dashboard`)
**Features:**
- Statistics cards (total users, courses, assignments)
- Recent activity
- Quick actions
- Role-based stats display

**Current:** Basic skeleton exists
**Needs:** Connect to real APIs, add charts

### 6. Layout & Navigation
**Features:**
- Sidebar with menu items
- Header with user info and logout
- Responsive design
- Role-based menu filtering

**Components Needed:**
- `src/components/layout/AdminLayout.tsx`
- Sidebar component
- Header component

## Implementation Steps

### Step 1: Create AdminLayout Component

```tsx
// src/components/layout/AdminLayout.tsx
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const AdminLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const menuItems = [
    { title: 'Dashboard', path: '/admin/dashboard', icon: 'Dashboard', roles: ['ADMIN'] },
    { title: 'Users', path: '/admin/users', icon: 'Users', roles: ['ADMIN'] },
    { title: 'Courses', path: '/admin/courses', icon: 'BookOpen', roles: ['ADMIN', 'TEACHER'] },
    { title: 'Lessons', path: '/admin/lessons', icon: 'FileText', roles: ['ADMIN', 'TEACHER'] },
    { title: 'Assignments', path: '/admin/assignments', icon: 'ClipboardCheck', roles: ['ADMIN', 'TEACHER'] },
  ];

  const filteredMenu = menuItems.filter(item => 
    item.roles.includes(user?.role || '')
  );

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white">
        <div className="p-4">
          <h1 className="text-2xl font-bold">LMS Admin</h1>
        </div>
        <nav className="mt-8">
          {filteredMenu.map(item => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className="w-full px-4 py-3 hover:bg-gray-800"
            >
              {item.title}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b px-6 py-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Welcome, {user?.full_name}</h2>
            <button onClick={logout} className="btn-danger">Logout</button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6 bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
};
```

### Step 2: Create Protected Route Component

```tsx
// src/components/auth/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

interface Props {
  children: React.ReactNode;
  roles?: string[];
}

export const ProtectedRoute = ({ children, roles }: Props) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <div>Access Denied</div>;
  }

  return <>{children}</>;
};
```

### Step 3: Update App.tsx with Admin Routes

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import AdminLayout from '@/components/layout/AdminLayout';

// Pages
import Login from '@/pages/Login';
import AdminDashboard from '@/pages/admin/AdminDashboard';
import UserManagement from '@/pages/admin/UserManagement';
import CoursesPage from '@/pages/admin/CoursesPage';
import LessonsPage from '@/pages/admin/LessonsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />

          {/* Admin Routes */}
          <Route path="/admin" element={
            <ProtectedRoute roles={['ADMIN', 'TEACHER']}>
              <AdminLayout />
            </ProtectedRoute>
          }>
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="users" element={
              <ProtectedRoute roles={['ADMIN']}>
                <UserManagement />
              </ProtectedRoute>
            } />
            <Route path="courses" element={<CoursesPage />} />
            <Route path="lessons" element={<LessonsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/admin/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

### Step 4: Create User Management Page Template

```tsx
// src/pages/admin/UserManagement.tsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import userService from '@/services/user';
import { Button } from '@/components/ui/button';
import { Dialog } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

export default function UserManagement() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: userService.getUsers
  });

  const createMutation = useMutation({
    mutationFn: userService.createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsDialogOpen(false);
    }
  });

  return (
    <div>
      <div className="flex justify-between mb-6">
        <h1 className="text-3xl font-bold">User Management</h1>
        <Button onClick={() => setIsDialogOpen(true)}>Add User</Button>
      </div>

      {/* Users Table */}
      <table className="w-full">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data?.users?.map(user => (
            <tr key={user.id}>
              <td>{user.full_name}</td>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>{user.is_active ? 'Active' : 'Inactive'}</td>
              <td>
                <Button size="sm">Edit</Button>
                <Button size="sm" variant="destructive">Delete</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Create/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        {/* Form content */}
      </Dialog>
    </div>
  );
}
```

## Quick Reference: API Endpoints

All endpoints go through API Gateway at `http://localhost:8000`

### Auth Endpoints
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### User Endpoints
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Course Endpoints
- `GET /courses` - List courses
- `POST /courses` - Create course
- `GET /courses/{id}` - Get course
- `PUT /courses/{id}` - Update course
- `DELETE /courses/{id}` - Delete course

### Lesson Endpoints
- `GET /courses/{course_id}/lessons` - List lessons
- `POST /courses/{course_id}/lessons` - Create lesson
- `GET /courses/{course_id}/lessons/{id}` - Get lesson
- `PUT /courses/{course_id}/lessons/{id}` - Update lesson
- `DELETE /courses/{course_id}/lessons/{id}` - Delete lesson

### Assignment Endpoints
- `GET /api/v1/assignments` - List assignments
- `POST /api/v1/assignments` - Create assignment
- `GET /api/v1/assignments/{id}` - Get assignment
- `PUT /api/v1/assignments/{id}` - Update assignment
- `DELETE /api/v1/assignments/{id}` - Delete assignment

## UI Components Available (Shadcn/UI)

The learnhub-frontend already has these components:
- ✅ Button, Input, Label
- ✅ Card, Dialog, Alert
- ✅ Table, Tabs
- ✅ Select, Checkbox, Radio
- ✅ Toast notifications
- ✅ Form components

## Next Steps to Complete Admin Features

1. **Copy component structure** from `frontend-admin/src/pages/` to learnhub-frontend
2. **Adapt Material-UI** components to Shadcn/UI equivalents
3. **Use existing services** (user.ts, content.ts, assignment.ts)
4. **Implement Layout** with sidebar and header
5. **Add role-based routing** and menu filtering
6. **Test each page** with backend services
7. **Add data tables** with sorting, filtering, pagination
8. **Implement forms** with validation (react-hook-form + zod)

## Advantages of LearnHub-Frontend

- **Faster builds** (Vite vs CRA)
- **Modern UI** (Shadcn/UI components)
- **Better DX** (TypeScript, hot reload)
- **Smaller bundle** size
- **Accessible** components by default
- **Customizable** Tailwind styling

## Current Deployment

- Frontend runs on **port 3005**
- Backend API Gateway on **port 8000**
- All 4 backend services are healthy
- Docker container: `lms-learnhub-frontend`

```bash
# Check status
sudo docker ps | grep learnhub

# View logs
sudo docker logs lms-learnhub-frontend

# Access
http://localhost:3005
```

## Summary

The learnhub-frontend is **integrated with the backend** and has:
- ✅ API services ready
- ✅ Authentication context
- ✅ Login page
- ✅ Basic dashboard
- ✅ Docker deployment

**To make it a full admin portal**, copy the page components from `frontend-admin` and adapt them to use Shadcn/UI components instead of Material-UI. The backend integration is complete, so it's mainly a UI porting task.
