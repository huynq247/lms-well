import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import assignmentService, { CreateAssignmentRequest } from '@/services/assignment';
import contentService from '@/services/content';
import { userService } from '@/services/user';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Plus, Edit, Trash2, ClipboardList, Calendar, User } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export default function AssignmentsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<any>(null);
  const [formData, setFormData] = useState({
    student_id: '',
    content_type: 'course' as 'course' | 'deck',
    content_id: '',
    title: '',
    description: '',
    instructions: '',
    due_date: '',
    supporting_decks: '',
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { user } = useAuth();

  console.log('🎯 AssignmentsPage rendered, user:', user);

  // Fetch assignments
  const { data: assignmentsData, isLoading, isError, error } = useQuery({
    queryKey: ['assignments', user?.id],
    queryFn: async () => {
      console.log('📋 Fetching assignments for instructor:', user?.id);
      const result = await assignmentService.getAssignments({ instructor_id: Number(user?.id) });
      console.log('✅ Assignments fetched:', result);
      return result;
    },
    enabled: !!user?.id,
    retry: false, // Don't retry on error for debugging
  });

  // Fetch my students
  const { data: studentsData } = useQuery({
    queryKey: ['my-students'],
    queryFn: userService.getMyStudents,
  });

  // Fetch courses
  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: contentService.getCourses,
  });

  // Fetch decks
  const { data: decksData } = useQuery({
    queryKey: ['decks'],
    queryFn: contentService.getDecks,
  });

  const createMutation = useMutation({
    mutationFn: assignmentService.createAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
      setIsCreateOpen(false);
      resetForm();
      toast({
        title: 'Assignment Created',
        description: 'Assignment has been created successfully',
      });
    },
    onError: (error: any) => {
      console.error('❌ Create assignment error:', error);
      console.error('❌ Response data:', error.response?.data);
      console.error('❌ Response data detail:', JSON.stringify(error.response?.data?.detail, null, 2));
      
      let errorMessage = 'Failed to create assignment';
      const errorDetail = error.response?.data?.detail;
      
      if (Array.isArray(errorDetail)) {
        // Pydantic validation errors are arrays
        errorMessage = errorDetail.map((err: any) => 
          `${err.loc?.join('.') || 'Field'}: ${err.msg || err.message || 'Invalid'}`
        ).join(', ');
      } else if (typeof errorDetail === 'string') {
        errorMessage = errorDetail;
      } else if (errorDetail) {
        errorMessage = JSON.stringify(errorDetail);
      }
      
      toast({
        title: 'Error Creating Assignment',
        description: errorMessage,
        variant: 'destructive',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: assignmentService.deleteAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
      setIsDeleteOpen(false);
      setSelectedAssignment(null);
      toast({
        title: 'Assignment Deleted',
        description: 'Assignment has been deleted successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete assignment',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      student_id: '',
      content_type: 'course',
      content_id: '',
      title: '',
      description: '',
      instructions: '',
      due_date: '',
      supporting_decks: '',
    });
  };

  const handleCreate = () => {
    if (!user?.id || !formData.student_id || !formData.content_id || !formData.title) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      });
      return;
    }

    // Get content title
    const content = formData.content_type === 'course'
      ? coursesData?.find((c: any) => c.id === formData.content_id)
      : decksData?.find((d: any) => d.id === formData.content_id);

    const supportingDecks = formData.supporting_decks ? [formData.supporting_decks] : [];
    const supportingDeckTitles = formData.supporting_decks
      ? [decksData?.find((d: any) => d.id === formData.supporting_decks)?.title || '']
      : [];

    // Convert date to datetime format (ISO 8601 with time)
    const dueDateISO = formData.due_date ? `${formData.due_date}T23:59:59` : undefined;

    const assignmentData: CreateAssignmentRequest = {
      instructor_id: Number(user.id),
      student_id: Number(formData.student_id),
      content_type: formData.content_type,
      content_id: formData.content_id,
      content_title: content?.title || 'Unknown',
      title: formData.title,
      description: formData.description || undefined,
      instructions: formData.instructions || undefined,
      due_date: dueDateISO,
      supporting_decks: supportingDecks.length > 0 ? supportingDecks : undefined,
      supporting_deck_titles: supportingDeckTitles.length > 0 ? supportingDeckTitles : undefined,
    };

    console.log('🚀 Submitting assignment data:', assignmentData);
    console.log('🚀 Due date value:', formData.due_date, '→ ISO:', dueDateISO);
    console.log('🚀 Supporting decks:', supportingDecks);
    
    createMutation.mutate(assignmentData);
  };

  const handleDeleteClick = (assignment: any) => {
    setSelectedAssignment(assignment);
    setIsDeleteOpen(true);
  };

  const handleDelete = () => {
    if (selectedAssignment) {
      deleteMutation.mutate(selectedAssignment.id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'default';
      case 'in_progress': return 'secondary';
      case 'pending': return 'outline';
      case 'overdue': return 'destructive';
      default: return 'outline';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
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
        <Button onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    );
  }

  const assignments = assignmentsData?.assignments || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-1">Assign courses and decks to students</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)} className="gap-2">
          <Plus size={20} />
          Create Assignment
        </Button>
      </div>

      {assignments.length > 0 ? (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Student</TableHead>
                  <TableHead>Content</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead className="w-32">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assignments.map((assignment, index) => (
                  <TableRow key={assignment.id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell className="font-semibold">
                      <div className="flex items-center gap-2">
                        <ClipboardList className="h-4 w-4 text-blue-600" />
                        {assignment.title}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-gray-500" />
                        {assignment.student_name || `Student #${assignment.student_id}`}
                      </div>
                    </TableCell>
                    <TableCell>{assignment.content_title}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {assignment.content_type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(assignment.status)}>
                        {assignment.status}
                      </Badge>
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
                              className="bg-blue-600 h-2 rounded-full" 
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
                      <div className="flex gap-2">
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteClick(assignment)}
                          title="Delete Assignment"
                        >
                          <Trash2 size={14} />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : (
        <div className="text-center py-12 border rounded-lg">
          <ClipboardList className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No assignments yet</h3>
          <p className="text-gray-600 mb-4">Create your first assignment to get started</p>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus size={20} className="mr-2" />
            Create Assignment
          </Button>
        </div>
      )}

      {/* Create Assignment Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Assignment</DialogTitle>
            <DialogDescription>
              Assign a course or deck to a student
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="student_id">Student *</Label>
              <Select
                value={formData.student_id}
                onValueChange={(value) => setFormData({ ...formData, student_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a student" />
                </SelectTrigger>
                <SelectContent>
                  {studentsData?.users?.map((student: any) => (
                    <SelectItem key={student.id} value={student.id.toString()}>
                      {student.full_name} ({student.username})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="content_type">Content Type *</Label>
              <Select
                value={formData.content_type}
                onValueChange={(value: 'course' | 'deck') => 
                  setFormData({ ...formData, content_type: value, content_id: '' })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="course">Course</SelectItem>
                  <SelectItem value="deck">Flashcard Deck</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="content_id">
                {formData.content_type === 'course' ? 'Course' : 'Deck'} *
              </Label>
              <Select
                value={formData.content_id}
                onValueChange={(value) => setFormData({ ...formData, content_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder={`Select a ${formData.content_type}`} />
                </SelectTrigger>
                <SelectContent>
                  {formData.content_type === 'course'
                    ? coursesData?.map((course: any) => (
                        <SelectItem key={course.id} value={course.id}>
                          {course.title}
                        </SelectItem>
                      ))
                    : decksData?.map((deck: any) => (
                        <SelectItem key={deck.id} value={deck.id}>
                          {deck.title}
                        </SelectItem>
                      ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="title">Assignment Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter assignment title"
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe the assignment..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="instructions">Instructions</Label>
              <Textarea
                id="instructions"
                value={formData.instructions}
                onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                placeholder="Special instructions for the student..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="due_date">Due Date</Label>
              <Input
                id="due_date"
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              />
            </div>

            {formData.content_type === 'course' && (
              <div>
                <Label htmlFor="supporting_decks">Supporting Flashcard Deck (Optional)</Label>
                <div className="flex gap-2">
                  <Select
                    value={formData.supporting_decks || undefined}
                    onValueChange={(value) => setFormData({ ...formData, supporting_decks: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a supporting deck (optional)" />
                    </SelectTrigger>
                    <SelectContent>
                      {decksData?.map((deck: any) => (
                        <SelectItem key={deck.id} value={deck.id}>
                          {deck.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {formData.supporting_decks && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setFormData({ ...formData, supporting_decks: '' })}
                    >
                      Clear
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setIsCreateOpen(false); resetForm(); }}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Assignment'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Assignment?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the assignment "{selectedAssignment?.title}". This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setSelectedAssignment(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
