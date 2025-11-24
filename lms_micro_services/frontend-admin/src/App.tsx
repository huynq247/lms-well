import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AdminLayout from "@/components/layout/AdminLayout";

// Public Pages
import Index from "./pages/Index";
import CourseDetail from "./pages/CourseDetail";
import Learning from "./pages/Learning";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";

// Auth Pages
import Login from "./pages/Login";

// Admin Pages
import AdminDashboard from "./pages/admin/AdminDashboard";
import UserManagement from "./pages/admin/UserManagement";
import CoursesPage from "./pages/admin/CoursesPage";
import LessonsPage from "./pages/admin/LessonsPage";
import DecksPage from "./pages/admin/DecksPage";
import DeckDetailPage from "./pages/admin/DeckDetailPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Index />} />
            <Route path="/course/:id" element={<CourseDetail />} />
            <Route path="/learning/:id" element={<Learning />} />
            <Route path="/learning" element={<Learning />} />
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            
            {/* Admin Routes - Protected */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute roles={['ADMIN', 'TEACHER']}>
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="dashboard" element={<AdminDashboard />} />
              <Route
                path="users"
                element={
                  <ProtectedRoute roles={['ADMIN']}>
                    <UserManagement />
                  </ProtectedRoute>
                }
              />
              <Route path="courses" element={<CoursesPage />} />
              <Route path="lessons" element={<LessonsPage />} />
              <Route path="decks" element={<DecksPage />} />
              <Route path="decks/:deckId" element={<DeckDetailPage />} />
            </Route>
            
            {/* Catch All */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
