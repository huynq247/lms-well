import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import TeacherLayout from "@/components/layout/TeacherLayout";

// Auth Pages
import Login from "./pages/Login";

// Teacher Pages
import TeacherDashboard from "./pages/teacher/AdminDashboard";
import CoursesPage from "./pages/teacher/CoursesPage";
import LessonsPage from "./pages/teacher/LessonsPage";
import DecksPage from "./pages/teacher/DecksPage";
import DeckDetailPage from "./pages/teacher/DeckDetailPage";
import AssignmentsPage from "./pages/teacher/AssignmentsPage";
import StudentsPage from "./pages/teacher/StudentsPage";

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
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Navigate to="/teacher/dashboard" replace />} />
            
            {/* Teacher Routes - Protected */}
            <Route
              path="/teacher"
              element={
                <ProtectedRoute roles={['TEACHER']}>
                  <TeacherLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/teacher/dashboard" replace />} />
              <Route path="dashboard" element={<TeacherDashboard />} />
              <Route path="courses" element={<CoursesPage />} />
              <Route path="lessons" element={<LessonsPage />} />
              <Route path="decks" element={<DecksPage />} />
              <Route path="decks/:deckId" element={<DeckDetailPage />} />
              <Route path="students" element={<StudentsPage />} />
              <Route path="assignments" element={<AssignmentsPage />} />
            </Route>
            
            {/* Catch All */}
            <Route path="*" element={<Navigate to="/teacher/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
