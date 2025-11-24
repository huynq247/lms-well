import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import contentService, { Lesson } from '@/services/content';
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
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { Plus, Edit, Trash2, FileText, Video } from 'lucide-react';
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

export default function LessonsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [selectedCourseId, setSelectedCourseId] = useState<string>('');
  const [formData, setFormData] = useState({
    course_id: '',
    title: '',
    content: '',
    video_url: '',
    order: 1,
    is_published: false,
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Fetch courses for dropdown
  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: contentService.getCourses,
  });

  // Fetch all lessons with optional course filter
  const { data: allLessonsData, isLoading } = useQuery({
    queryKey: ['all-lessons', selectedCourseId],
    queryFn: () => contentService.getAllLessons({
      course_id: selectedCourseId || undefined,
      size: 100
    }),
  });

  // Create lesson mutation
  const createMutation = useMutation({
    mutationFn: ({ courseId, data }: { courseId: string; data: any }) =>
      contentService.createLesson(courseId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-lessons'] });
      setIsCreateOpen(false);
      resetForm();
      toast({
        title: 'Lesson Created',
        description: 'Lesson has been created successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create lesson',
        variant: 'destructive',
      });
    },
  });

  // Update lesson mutation
  const updateMutation = useMutation({
    mutationFn: ({ courseId, lessonId, data }: { courseId: string; lessonId: string; data: any }) =>
      contentService.updateLesson(courseId, lessonId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-lessons'] });
      setIsEditOpen(false);
      setSelectedLesson(null);
      toast({
        title: 'Lesson Updated',
        description: 'Lesson has been updated successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update lesson',
        variant: 'destructive',
      });
    },
  });

  // Delete lesson mutation
  const deleteMutation = useMutation({
    mutationFn: ({ courseId, lessonId }: { courseId: string; lessonId: string }) =>
      contentService.deleteLesson(courseId, lessonId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-lessons'] });
      setIsDeleteOpen(false);
      setSelectedLesson(null);
      toast({
        title: 'Lesson Deleted',
        description: 'Lesson has been deleted successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete lesson',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      course_id: selectedCourseId || '',
      title: '',
      content: '',
      video_url: '',
      order: 1,
      is_published: false,
    });
  };

  const handleCreate = () => {
    if (!formData.course_id) {
      toast({
        title: 'Error',
        description: 'Please select a course for this lesson',
        variant: 'destructive',
      });
      return;
    }
    createMutation.mutate({
      courseId: formData.course_id,
      data: formData,
    });
  };

  const handleEdit = (lesson: Lesson) => {
    setSelectedLesson(lesson);
    setFormData({
      course_id: lesson.course_id || '',
      title: lesson.title,
      content: lesson.content,
      video_url: lesson.video_url || '',
      order: lesson.order,
      is_published: lesson.is_published || false,
    });
    setIsEditOpen(true);
  };

  const handleUpdate = () => {
    if (selectedLesson && formData.course_id) {
      updateMutation.mutate({
        courseId: formData.course_id,
        lessonId: selectedLesson.id,
        data: formData,
      });
    }
  };

  const handleDeleteClick = (lesson: Lesson) => {
    setSelectedLesson(lesson);
    setIsDeleteOpen(true);
  };

  const handleDelete = () => {
    if (selectedLesson && selectedLesson.course_id) {
      deleteMutation.mutate({
        courseId: selectedLesson.course_id,
        lessonId: selectedLesson.id,
      });
    }
  };

  const courses = coursesData || [];
  const lessons = allLessonsData?.items || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Lesson Management</h1>
          <p className="text-gray-600 mt-1">Create and manage course lessons</p>
        </div>
        <Button 
          onClick={() => setIsCreateOpen(true)} 
          className="gap-2"
        >
          <Plus size={20} />
          Create Lesson
        </Button>
      </div>

      {/* Course Selector */}
      <div className="bg-white p-4 rounded-lg shadow">
        <Label htmlFor="course-select">Filter by Course (Optional)</Label>
        <Select value={selectedCourseId || 'all'} onValueChange={(value) => setSelectedCourseId(value === 'all' ? '' : value)}>
          <SelectTrigger className="mt-2">
            <SelectValue placeholder="All lessons (or select a course to filter)" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Lessons</SelectItem>
            {courses.map((course) => (
              <SelectItem key={course.id} value={course.id}>
                {course.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Lessons Table */}
      <div className="bg-white rounded-lg shadow">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
          </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Order</TableHead>
                    <TableHead>Title</TableHead>
                    {!selectedCourseId && <TableHead>Course</TableHead>}
                    <TableHead>Content Preview</TableHead>
                    <TableHead>Video</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lessons.map((lesson) => {
                    const lessonCourse = courses.find(c => c.id === lesson.course_id);
                    return (
                    <TableRow key={lesson.id}>
                      <TableCell className="font-medium">{lesson.order}</TableCell>
                      <TableCell className="font-medium">{lesson.title}</TableCell>
                      {!selectedCourseId && (
                        <TableCell className="text-gray-600">
                          {lessonCourse?.title || 'Unknown Course'}
                        </TableCell>
                      )}
                      <TableCell className="max-w-xs truncate text-gray-600">
                        {lesson.content.substring(0, 100)}...
                      </TableCell>
                      <TableCell>
                        {lesson.video_url ? (
                          <Badge variant="default" className="gap-1">
                            <Video size={14} />
                            Video
                          </Badge>
                        ) : (
                          <Badge variant="secondary">No video</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={lesson.is_published ? 'default' : 'secondary'}>
                          {lesson.is_published ? 'Published' : 'Draft'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(lesson)}
                          >
                            <Edit size={16} />
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeleteClick(lesson)}
                          >
                            <Trash2 size={16} />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                  })}
                </TableBody>
              </Table>

              {lessons.length === 0 && (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No lessons found</h3>
                  <p className="text-gray-600 mb-4">
                    {selectedCourseId 
                      ? 'This course has no lessons yet. Create one to get started.' 
                      : 'No lessons available. Select a course and create lessons.'}
                  </p>
                  {selectedCourseId && (
                    <Button onClick={() => setIsCreateOpen(true)}>
                      <Plus size={20} className="mr-2" />
                      Create Lesson
                    </Button>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )

      {/* Create Lesson Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Create New Lesson</DialogTitle>
            <DialogDescription>
              Add a new lesson to a course
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="course_select">Select Course *</Label>
              <Select 
                value={formData.course_id} 
                onValueChange={(value) => setFormData({ ...formData, course_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Choose a course for this lesson" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id}>
                      {course.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="title">Lesson Title</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  placeholder="Introduction to Variables"
                />
              </div>
              <div>
                <Label htmlFor="order">Order</Label>
                <Input
                  id="order"
                  type="number"
                  value={formData.order}
                  onChange={(e) =>
                    setFormData({ ...formData, order: parseInt(e.target.value) || 1 })
                  }
                  placeholder="1"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="content">Content</Label>
              <Textarea
                id="content"
                value={formData.content}
                onChange={(e) =>
                  setFormData({ ...formData, content: e.target.value })
                }
                placeholder="Enter the lesson content..."
                rows={8}
              />
            </div>
            <div>
              <Label htmlFor="video_url">Video URL (optional)</Label>
              <Input
                id="video_url"
                value={formData.video_url}
                onChange={(e) =>
                  setFormData({ ...formData, video_url: e.target.value })
                }
                placeholder="https://youtube.com/watch?v=..."
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="is_published"
                checked={formData.is_published}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, is_published: checked as boolean })
                }
              />
              <Label htmlFor="is_published" className="cursor-pointer">
                Publish immediately
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsCreateOpen(false);
              resetForm();
            }}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Lesson'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Lesson Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Edit Lesson</DialogTitle>
            <DialogDescription>
              Update lesson information
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_course_select">Course *</Label>
              <Select 
                value={formData.course_id} 
                onValueChange={(value) => setFormData({ ...formData, course_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Choose a course" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id}>
                      {course.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_title">Lesson Title</Label>
                <Input
                  id="edit_title"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                />
              </div>
              <div>
                <Label htmlFor="edit_order">Order</Label>
                <Input
                  id="edit_order"
                  type="number"
                  value={formData.order}
                  onChange={(e) =>
                    setFormData({ ...formData, order: parseInt(e.target.value) || 1 })
                  }
                />
              </div>
            </div>
            <div>
              <Label htmlFor="edit_content">Content</Label>
              <Textarea
                id="edit_content"
                value={formData.content}
                onChange={(e) =>
                  setFormData({ ...formData, content: e.target.value })
                }
                rows={8}
              />
            </div>
            <div>
              <Label htmlFor="edit_video_url">Video URL (optional)</Label>
              <Input
                id="edit_video_url"
                value={formData.video_url}
                onChange={(e) =>
                  setFormData({ ...formData, video_url: e.target.value })
                }
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="edit_is_published"
                checked={formData.is_published}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, is_published: checked as boolean })
                }
              />
              <Label htmlFor="edit_is_published" className="cursor-pointer">
                Published
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsEditOpen(false);
              setSelectedLesson(null);
              resetForm();
            }}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Updating...' : 'Update Lesson'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the lesson{' '}
              <strong>{selectedLesson?.title}</strong>.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setSelectedLesson(null)}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
