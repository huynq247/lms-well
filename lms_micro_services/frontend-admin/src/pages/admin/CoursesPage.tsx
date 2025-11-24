import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import contentService, { Course, Lesson } from '@/services/content';
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
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
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
import { Plus, Edit, Trash2, BookOpen, Eye, Calendar, List, Video, FileText } from 'lucide-react';
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
import { useAuth } from '@/contexts/AuthContext';

export default function CoursesPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isViewOpen, setIsViewOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [isManageLessonsOpen, setIsManageLessonsOpen] = useState(false);
  const [isCreateLessonOpen, setIsCreateLessonOpen] = useState(false);
  const [isEditLessonOpen, setIsEditLessonOpen] = useState(false);
  const [isDeleteLessonOpen, setIsDeleteLessonOpen] = useState(false);
  const [isAddExistingLessonOpen, setIsAddExistingLessonOpen] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [selectedLessonToLink, setSelectedLessonToLink] = useState<string>('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    is_published: false,
    is_active: true,
  });
  const [lessonFormData, setLessonFormData] = useState({
    title: '',
    content: '',
    video_url: '',
    order: 1,
    is_published: false,
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { user } = useAuth();

  // Fetch courses
  const { data: coursesData, isLoading, error } = useQuery({
    queryKey: ['courses'],
    queryFn: contentService.getCourses,
  });

  // Create course mutation
  const createMutation = useMutation({
    mutationFn: contentService.createCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setIsCreateOpen(false);
      resetForm();
      toast({
        title: 'Course Created',
        description: 'Course has been created successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create course',
        variant: 'destructive',
      });
    },
  });

  // Update course mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      contentService.updateCourse(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setIsEditOpen(false);
      setSelectedCourse(null);
      toast({
        title: 'Course Updated',
        description: 'Course has been updated successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update course',
        variant: 'destructive',
      });
    },
  });

  // Delete course mutation
  const deleteMutation = useMutation({
    mutationFn: contentService.deleteCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setIsDeleteOpen(false);
      setSelectedCourse(null);
      toast({
        title: 'Course Deleted',
        description: 'Course has been deleted successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete course',
        variant: 'destructive',
      });
    },
  });

  // Fetch lessons for selected course
  const { data: courseLessonsData } = useQuery({
    queryKey: ['course-lessons', selectedCourse?.id],
    queryFn: () => selectedCourse ? contentService.getLessons(selectedCourse.id) : Promise.resolve([]),
    enabled: !!selectedCourse && isManageLessonsOpen,
  });

  // Fetch all lessons for linking
  const { data: allLessonsData } = useQuery({
    queryKey: ['all-lessons'],
    queryFn: () => contentService.getAllLessons({ size: 100 }),
    enabled: isAddExistingLessonOpen,
  });

  // Create lesson mutation
  const createLessonMutation = useMutation({
    mutationFn: ({ courseId, data }: { courseId: string; data: any }) =>
      contentService.createLesson(courseId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-lessons'] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setIsCreateLessonOpen(false);
      resetLessonForm();
      toast({
        title: 'Lesson Created',
        description: 'Lesson has been added to the course successfully',
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
  const updateLessonMutation = useMutation({
    mutationFn: ({ courseId, lessonId, data }: { courseId: string; lessonId: string; data: any }) =>
      contentService.updateLesson(courseId, lessonId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-lessons'] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setIsEditLessonOpen(false);
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
  const deleteLessonMutation = useMutation({
    mutationFn: ({ courseId, lessonId }: { courseId: string; lessonId: string }) =>
      contentService.deleteLesson(courseId, lessonId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-lessons'] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      setIsDeleteLessonOpen(false);
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

  // Link existing lesson to course mutation
  const linkLessonMutation = useMutation({
    mutationFn: ({ oldCourseId, newCourseId, lessonId, data }: { oldCourseId: string; newCourseId: string; lessonId: string; data: any }) =>
      contentService.updateLesson(oldCourseId, lessonId, { ...data, course_id: newCourseId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-lessons'] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      queryClient.invalidateQueries({ queryKey: ['all-lessons'] });
      setIsAddExistingLessonOpen(false);
      setSelectedLessonToLink('');
      toast({
        title: 'Lesson Linked',
        description: 'Existing lesson has been added to the course successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to link lesson',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      is_published: false,
      is_active: true,
    });
  };

  const resetLessonForm = () => {
    setLessonFormData({
      title: '',
      content: '',
      video_url: '',
      order: 1,
      is_published: false,
    });
  };

  const handleCreate = () => {
    createMutation.mutate({
      ...formData,
      instructor_id: user?.id ? Number(user.id) : 2,
    });
  };

  const handleEdit = (course: Course) => {
    setSelectedCourse(course);
    setFormData({
      title: course.title,
      description: course.description,
      is_published: course.is_published || false,
      is_active: course.is_active !== undefined ? course.is_active : true,
    });
    setIsEditOpen(true);
  };

  const handleUpdate = () => {
    if (selectedCourse) {
      updateMutation.mutate({ 
        id: selectedCourse.id, 
        data: formData 
      });
    }
  };

  const handleDeleteClick = (course: Course) => {
    setSelectedCourse(course);
    setIsDeleteOpen(true);
  };

  const handleDelete = () => {
    if (selectedCourse) {
      deleteMutation.mutate(selectedCourse.id);
    }
  };

  const handleViewCourse = (course: Course) => {
    setSelectedCourse(course);
    setIsViewOpen(true);
  };

  const handleManageLessons = (course: Course) => {
    setSelectedCourse(course);
    setIsManageLessonsOpen(true);
  };

  const handleCreateLesson = () => {
    if (selectedCourse) {
      createLessonMutation.mutate({
        courseId: selectedCourse.id,
        data: lessonFormData,
      });
    }
  };

  const handleLinkExistingLesson = () => {
    if (selectedCourse && selectedLessonToLink) {
      const allLessons = allLessonsData?.items || [];
      const lessonToLink = allLessons.find(l => l.id === selectedLessonToLink);
      
      if (lessonToLink) {
        linkLessonMutation.mutate({
          oldCourseId: lessonToLink.course_id || selectedCourse.id,
          newCourseId: selectedCourse.id,
          lessonId: lessonToLink.id,
          data: {
            title: lessonToLink.title,
            content: lessonToLink.content,
            video_url: lessonToLink.video_url,
            order: lessonToLink.order,
            is_published: lessonToLink.is_published,
          },
        });
      }
    }
  };

  const handleEditLesson = (lesson: Lesson) => {
    setSelectedLesson(lesson);
    setLessonFormData({
      title: lesson.title,
      content: lesson.content,
      video_url: lesson.video_url || '',
      order: lesson.order,
      is_published: lesson.is_published || false,
    });
    setIsEditLessonOpen(true);
  };

  const handleUpdateLesson = () => {
    if (selectedCourse && selectedLesson) {
      updateLessonMutation.mutate({
        courseId: selectedCourse.id,
        lessonId: selectedLesson.id,
        data: lessonFormData,
      });
    }
  };

  const handleDeleteLessonClick = (lesson: Lesson) => {
    setSelectedLesson(lesson);
    setIsDeleteLessonOpen(true);
  };

  const handleDeleteLesson = () => {
    if (selectedCourse && selectedLesson) {
      deleteLessonMutation.mutate({
        courseId: selectedCourse.id,
        lessonId: selectedLesson.id,
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600">
        Error loading courses: {(error as Error).message}
      </div>
    );
  }

  const courses = coursesData || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Course Management</h1>
          <p className="text-gray-600 mt-1">Create and manage your courses</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)} className="gap-2">
          <Plus size={20} />
          Create Course
        </Button>
      </div>

      {/* Courses Table */}
      {courses.length > 0 ? (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead className="w-32">Lessons</TableHead>
                  <TableHead className="w-32">Status</TableHead>
                  <TableHead className="w-40">Created</TableHead>
                  <TableHead className="w-48">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {courses.map((course, index) => (
                  <TableRow key={course.id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell className="font-semibold">
                      <div className="flex items-center gap-2">
                        <BookOpen className="h-4 w-4 text-blue-600" />
                        {course.title}
                      </div>
                    </TableCell>
                    <TableCell className="max-w-xs truncate text-gray-600">
                      {course.description}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {course.total_lessons || 0} lessons
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col gap-1">
                        <Badge variant={course.is_active ? 'default' : 'secondary'} className="w-fit">
                          {course.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        <Badge variant={course.is_published ? 'default' : 'outline'} className="w-fit">
                          {course.is_published ? 'Published' : 'Draft'}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {new Date(course.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleManageLessons(course)}
                          title="Manage Lessons"
                        >
                          <List size={14} />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewCourse(course)}
                          title="View Details"
                        >
                          <Eye size={14} />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(course)}
                          title="Edit Course"
                        >
                          <Edit size={14} />
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteClick(course)}
                          title="Delete Course"
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
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No courses yet</h3>
          <p className="text-gray-600 mb-4">Get started by creating your first course</p>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus size={20} className="mr-2" />
            Create Course
          </Button>
        </div>
      )}

      {/* Create Course Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Course</DialogTitle>
            <DialogDescription>
              Add a new course to your learning management system
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Course Title</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                placeholder="Introduction to Programming"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Describe what students will learn in this course..."
                rows={5}
              />
            </div>
            <div className="space-y-3">
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
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_active: checked as boolean })
                  }
                />
                <Label htmlFor="is_active" className="cursor-pointer">
                  Active course
                </Label>
              </div>
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
              {createMutation.isPending ? 'Creating...' : 'Create Course'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Course Dialog */}
      <Dialog open={isViewOpen} onOpenChange={setIsViewOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Course Details</DialogTitle>
            <DialogDescription>
              View course information
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label className="text-gray-600">Course Title</Label>
              <p className="mt-1 text-lg font-semibold">{selectedCourse?.title}</p>
            </div>
            <div>
              <Label className="text-gray-600">Description</Label>
              <p className="mt-1 text-gray-800 whitespace-pre-wrap">{selectedCourse?.description}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-600">Instructor</Label>
                <p className="mt-1 font-medium">{selectedCourse?.instructor_name || `Instructor ${selectedCourse?.instructor_id}`}</p>
              </div>
              <div>
                <Label className="text-gray-600">Total Lessons</Label>
                <p className="mt-1 font-medium">{selectedCourse?.total_lessons || 0} lessons</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-600">Status</Label>
                <div className="mt-1">
                  <Badge variant={selectedCourse?.is_active ? 'default' : 'secondary'}>
                    {selectedCourse?.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </div>
              <div>
                <Label className="text-gray-600">Published</Label>
                <div className="mt-1">
                  <Badge variant={selectedCourse?.is_published ? 'default' : 'secondary'}>
                    {selectedCourse?.is_published ? 'Published' : 'Draft'}
                  </Badge>
                </div>
              </div>
            </div>
            <div>
              <Label className="text-gray-600">Created</Label>
              <p className="mt-1">{selectedCourse?.created_at ? new Date(selectedCourse.created_at).toLocaleString() : 'N/A'}</p>
            </div>
            {selectedCourse?.updated_at && (
              <div>
                <Label className="text-gray-600">Last Updated</Label>
                <p className="mt-1">{new Date(selectedCourse.updated_at).toLocaleString()}</p>
              </div>
            )}
          </div>
          <DialogFooter className="flex justify-between">
            <Button variant="secondary" onClick={() => {
              setIsViewOpen(false);
              handleManageLessons(selectedCourse!);
            }}>
              <List size={16} className="mr-2" />
              Manage Lessons
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => {
                setIsViewOpen(false);
                setSelectedCourse(null);
              }}>
                Close
              </Button>
              <Button onClick={() => {
                setIsViewOpen(false);
                handleEdit(selectedCourse!);
              }}>
                <Edit size={16} className="mr-2" />
                Edit Course
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Course Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Course</DialogTitle>
            <DialogDescription>
              Update course information
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_title">Course Title</Label>
              <Input
                id="edit_title"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
              />
            </div>
            <div>
              <Label htmlFor="edit_description">Description</Label>
              <Textarea
                id="edit_description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={5}
              />
            </div>
            <div className="space-y-3">
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
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="edit_is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_active: checked as boolean })
                  }
                />
                <Label htmlFor="edit_is_active" className="cursor-pointer">
                  Active
                </Label>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsEditOpen(false);
              setSelectedCourse(null);
              resetForm();
            }}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Updating...' : 'Update Course'}
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
              This will permanently delete the course{' '}
              <strong>{selectedCourse?.title}</strong> and all its lessons.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setSelectedCourse(null)}>
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

      {/* Manage Lessons Dialog */}
      <Dialog open={isManageLessonsOpen} onOpenChange={setIsManageLessonsOpen}>
        <DialogContent className="max-w-5xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Manage Lessons - {selectedCourse?.title}</DialogTitle>
            <DialogDescription>
              Add, edit, or remove lessons for this course
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Button onClick={() => setIsCreateLessonOpen(true)} className="gap-2">
                <Plus size={20} />
                Create New Lesson
              </Button>
              <Button 
                onClick={() => setIsAddExistingLessonOpen(true)} 
                variant="outline"
                className="gap-2"
              >
                <List size={20} />
                Add Existing Lesson
              </Button>
            </div>
            
            {courseLessonsData && courseLessonsData.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Order</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Video</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-32">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {courseLessonsData.map((lesson) => (
                    <TableRow key={lesson.id}>
                      <TableCell className="font-medium">{lesson.order}</TableCell>
                      <TableCell>{lesson.title}</TableCell>
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
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditLesson(lesson)}
                          >
                            <Edit size={14} />
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeleteLessonClick(lesson)}
                          >
                            <Trash2 size={14} />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-12 border rounded-lg">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No lessons yet</h3>
                <p className="text-gray-600 mb-4">Get started by adding your first lesson</p>
                <Button onClick={() => setIsCreateLessonOpen(true)}>
                  <Plus size={20} className="mr-2" />
                  Add Lesson
                </Button>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsManageLessonsOpen(false);
              setSelectedCourse(null);
            }}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Lesson Dialog */}
      <Dialog open={isCreateLessonOpen} onOpenChange={setIsCreateLessonOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Add Lesson to {selectedCourse?.title}</DialogTitle>
            <DialogDescription>
              Create a new lesson for this course
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="lesson_title">Lesson Title</Label>
                <Input
                  id="lesson_title"
                  value={lessonFormData.title}
                  onChange={(e) =>
                    setLessonFormData({ ...lessonFormData, title: e.target.value })
                  }
                  placeholder="Introduction to Variables"
                />
              </div>
              <div>
                <Label htmlFor="lesson_order">Order</Label>
                <Input
                  id="lesson_order"
                  type="number"
                  value={lessonFormData.order}
                  onChange={(e) =>
                    setLessonFormData({ ...lessonFormData, order: parseInt(e.target.value) || 1 })
                  }
                  placeholder="1"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="lesson_content">Content</Label>
              <Textarea
                id="lesson_content"
                value={lessonFormData.content}
                onChange={(e) =>
                  setLessonFormData({ ...lessonFormData, content: e.target.value })
                }
                placeholder="Enter the lesson content..."
                rows={8}
              />
            </div>
            <div>
              <Label htmlFor="lesson_video_url">Video URL (optional)</Label>
              <Input
                id="lesson_video_url"
                value={lessonFormData.video_url}
                onChange={(e) =>
                  setLessonFormData({ ...lessonFormData, video_url: e.target.value })
                }
                placeholder="https://youtube.com/watch?v=..."
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="lesson_is_published"
                checked={lessonFormData.is_published}
                onCheckedChange={(checked) =>
                  setLessonFormData({ ...lessonFormData, is_published: checked as boolean })
                }
              />
              <Label htmlFor="lesson_is_published" className="cursor-pointer">
                Publish immediately
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsCreateLessonOpen(false);
              resetLessonForm();
            }}>
              Cancel
            </Button>
            <Button onClick={handleCreateLesson} disabled={createLessonMutation.isPending}>
              {createLessonMutation.isPending ? 'Creating...' : 'Create Lesson'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Existing Lesson Dialog */}
      <Dialog open={isAddExistingLessonOpen} onOpenChange={setIsAddExistingLessonOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add Existing Lesson to {selectedCourse?.title}</DialogTitle>
            <DialogDescription>
              Select a lesson from your existing lessons to add to this course
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="select_existing_lesson">Select Lesson</Label>
              <Select 
                value={selectedLessonToLink} 
                onValueChange={setSelectedLessonToLink}
              >
                <SelectTrigger className="mt-2">
                  <SelectValue placeholder="Choose a lesson to add" />
                </SelectTrigger>
                <SelectContent>
                  {allLessonsData?.items
                    ?.filter(lesson => {
                      // Filter out lessons already in this course
                      const currentLessonIds = courseLessonsData?.map(l => l.id) || [];
                      return !currentLessonIds.includes(lesson.id);
                    })
                    .map((lesson) => (
                      <SelectItem key={lesson.id} value={lesson.id}>
                        <div className="flex items-center gap-2">
                          <span>{lesson.title}</span>
                          {lesson.video_url && (
                            <Badge variant="secondary" className="text-xs">
                              <Video size={12} className="mr-1" />
                              Video
                            </Badge>
                          )}
                        </div>
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              {allLessonsData?.items && (
                <p className="text-sm text-gray-500 mt-2">
                  {allLessonsData.items.filter(lesson => {
                    const currentLessonIds = courseLessonsData?.map(l => l.id) || [];
                    return !currentLessonIds.includes(lesson.id);
                  }).length} lessons available
                </p>
              )}
            </div>
            {selectedLessonToLink && allLessonsData?.items && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <Label className="text-sm font-semibold">Lesson Preview</Label>
                {(() => {
                  const lesson = allLessonsData.items.find(l => l.id === selectedLessonToLink);
                  return lesson ? (
                    <div className="mt-2 space-y-2">
                      <p className="font-medium">{lesson.title}</p>
                      <p className="text-sm text-gray-600 line-clamp-2">{lesson.content}</p>
                      <div className="flex gap-2">
                        <Badge variant="outline">Order: {lesson.order}</Badge>
                        {lesson.is_published && <Badge>Published</Badge>}
                        {lesson.video_url && (
                          <Badge variant="secondary">
                            <Video size={12} className="mr-1" />
                            Has Video
                          </Badge>
                        )}
                      </div>
                    </div>
                  ) : null;
                })()}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsAddExistingLessonOpen(false);
              setSelectedLessonToLink('');
            }}>
              Cancel
            </Button>
            <Button 
              onClick={handleLinkExistingLesson} 
              disabled={!selectedLessonToLink || linkLessonMutation.isPending}
            >
              {linkLessonMutation.isPending ? 'Adding...' : 'Add to Course'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Lesson Dialog */}
      <Dialog open={isEditLessonOpen} onOpenChange={setIsEditLessonOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Edit Lesson</DialogTitle>
            <DialogDescription>
              Update lesson information
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_lesson_title">Lesson Title</Label>
                <Input
                  id="edit_lesson_title"
                  value={lessonFormData.title}
                  onChange={(e) =>
                    setLessonFormData({ ...lessonFormData, title: e.target.value })
                  }
                />
              </div>
              <div>
                <Label htmlFor="edit_lesson_order">Order</Label>
                <Input
                  id="edit_lesson_order"
                  type="number"
                  value={lessonFormData.order}
                  onChange={(e) =>
                    setLessonFormData({ ...lessonFormData, order: parseInt(e.target.value) || 1 })
                  }
                />
              </div>
            </div>
            <div>
              <Label htmlFor="edit_lesson_content">Content</Label>
              <Textarea
                id="edit_lesson_content"
                value={lessonFormData.content}
                onChange={(e) =>
                  setLessonFormData({ ...lessonFormData, content: e.target.value })
                }
                rows={8}
              />
            </div>
            <div>
              <Label htmlFor="edit_lesson_video_url">Video URL (optional)</Label>
              <Input
                id="edit_lesson_video_url"
                value={lessonFormData.video_url}
                onChange={(e) =>
                  setLessonFormData({ ...lessonFormData, video_url: e.target.value })
                }
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="edit_lesson_is_published"
                checked={lessonFormData.is_published}
                onCheckedChange={(checked) =>
                  setLessonFormData({ ...lessonFormData, is_published: checked as boolean })
                }
              />
              <Label htmlFor="edit_lesson_is_published" className="cursor-pointer">
                Published
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsEditLessonOpen(false);
              setSelectedLesson(null);
              resetLessonForm();
            }}>
              Cancel
            </Button>
            <Button onClick={handleUpdateLesson} disabled={updateLessonMutation.isPending}>
              {updateLessonMutation.isPending ? 'Updating...' : 'Update Lesson'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Lesson Confirmation Dialog */}
      <AlertDialog open={isDeleteLessonOpen} onOpenChange={setIsDeleteLessonOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Lesson?</AlertDialogTitle>
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
              onClick={handleDeleteLesson}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteLessonMutation.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
