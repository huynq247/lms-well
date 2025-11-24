import { useQuery } from '@tanstack/react-query';
import assignmentService from '@/services/assignment';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { ClipboardList, Calendar, BookOpen, Play, CheckCircle2 } from 'lucide-react';

export default function StudentAssignmentsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Fetch student's assignments
  const { data: assignmentsData, isLoading, isError, error } = useQuery({
    queryKey: ['my-assignments', user?.id],
    queryFn: async () => {
      console.log('📋 Fetching assignments for student:', user?.id);
      const result = await assignmentService.getAssignments({ student_id: Number(user?.id) });
      console.log('✅ Student assignments fetched:', result);
      return result;
    },
    enabled: !!user?.id,
    retry: 1,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'default';
      case 'in_progress': return 'secondary';
      case 'pending': return 'outline';
      case 'overdue': return 'destructive';
      default: return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'in_progress': return <Play className="h-4 w-4 text-blue-600" />;
      case 'pending': return <ClipboardList className="h-4 w-4 text-gray-600" />;
      case 'overdue': return <Calendar className="h-4 w-4 text-red-600" />;
      default: return <ClipboardList className="h-4 w-4" />;
    }
  };

  const handleStartAssignment = (assignment: any) => {
    if (assignment.content_type === 'course') {
      navigate(`/student/courses/${assignment.content_id}`);
    } else if (assignment.content_type === 'deck') {
      navigate(`/student/decks/${assignment.content_id}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-red-600 mb-4">
          <h3 className="text-lg font-semibold">Error Loading Assignments</h3>
          <p className="text-sm text-gray-600 mt-2">
            {error instanceof Error ? error.message : 'Failed to load assignments'}
          </p>
        </div>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  const assignments = assignmentsData?.assignments || [];
  const pendingCount = assignments.filter((a: any) => a.status === 'pending').length;
  const inProgressCount = assignments.filter((a: any) => a.status === 'in_progress').length;
  const completedCount = assignments.filter((a: any) => a.status === 'completed').length;
  const overdueCount = assignments.filter((a: any) => a.status === 'overdue').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Assignments</h1>
        <p className="text-gray-600 mt-1">Track and complete your assigned work</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <ClipboardList className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Play className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{inProgressCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <Calendar className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overdueCount}</div>
          </CardContent>
        </Card>
      </div>

      {assignments.length > 0 ? (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Assignment</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Instructor</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead className="w-32">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assignments.map((assignment: any, index: number) => (
                  <TableRow key={assignment.id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>
                      <div>
                        <div className="font-semibold">{assignment.title}</div>
                        <div className="text-sm text-gray-600">{assignment.content_title}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {assignment.content_type}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {assignment.instructor_name || `Instructor #${assignment.instructor_id}`}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(assignment.status)}
                        <Badge variant={getStatusColor(assignment.status)}>
                          {assignment.status}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {assignment.due_date ? (
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(assignment.due_date).toLocaleDateString()}
                        </div>
                      ) : (
                        'No deadline'
                      )}
                    </TableCell>
                    <TableCell>
                      {assignment.course_progress_percentage !== undefined ? (
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-indigo-600 h-2 rounded-full" 
                              style={{ width: `${assignment.course_progress_percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-600">
                            {assignment.course_progress_percentage}%
                          </span>
                        </div>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      {assignment.status !== 'completed' && (
                        <Button
                          size="sm"
                          onClick={() => handleStartAssignment(assignment)}
                          className="gap-2"
                        >
                          <BookOpen size={14} />
                          {assignment.status === 'in_progress' ? 'Continue' : 'Start'}
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : (
        <div className="text-center py-12 border rounded-lg bg-white">
          <ClipboardList className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No assignments yet</h3>
          <p className="text-gray-600">Your instructor will assign courses and materials soon</p>
        </div>
      )}
    </div>
  );
}
