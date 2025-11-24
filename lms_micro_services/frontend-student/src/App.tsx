import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import StudentLayout from "@/components/layout/StudentLayout";

// Auth Pages
import Login from "./pages/Login";

// Student Pages
import StudentAssignmentsPage from "./pages/student/AssignmentsPage";
import CoursesPage from "./pages/student/CoursesPage";
import CourseDetailPage from "./pages/student/CourseDetailPage";
import LessonLearningPage from "./pages/student/LessonLearningPage";
import DecksPage from "./pages/student/DecksPage";
import DeckDetailPage from "./pages/student/DeckDetailPage";
import StudyFlashcardsPage from "./pages/student/StudyFlashcardsPage";

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
            <Route path="/" element={<Navigate to="/student/courses" replace />} />
            
            {/* Student Routes - Protected */}
            <Route
              path="/student"
              element={
                <ProtectedRoute roles={['STUDENT']}>
                  <StudentLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/student/courses" replace />} />
              <Route path="assignments" element={<StudentAssignmentsPage />} />
              <Route path="courses" element={<CoursesPage />} />
              <Route path="courses/:courseId" element={<CourseDetailPage />} />
              <Route path="lessons/:lessonId" element={<LessonLearningPage />} />
              <Route path="decks" element={<DecksPage />} />
              <Route path="decks/:deckId" element={<DeckDetailPage />} />
              <Route path="decks/:deckId/study" element={<StudyFlashcardsPage />} />
            </Route>
            
            {/* Catch All */}
            <Route path="*" element={<Navigate to="/student/courses" replace />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
