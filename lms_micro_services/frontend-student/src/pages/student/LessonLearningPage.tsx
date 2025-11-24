import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import contentService from '@/services/content';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  ArrowLeft,
  CheckCircle2,
  PlayCircle,
  Video,
  FileText,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export default function LessonLearningPage() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [videoLoaded, setVideoLoaded] = useState(false);

  // Fetch lesson details
  const { data: lesson, isLoading } = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => contentService.getLessonById(lessonId!),
    enabled: !!lessonId,
  });

  // Fetch course to get all lessons for navigation
  const { data: courseLessons } = useQuery({
    queryKey: ['course-lessons', lesson?.course_id],
    queryFn: () => contentService.getLessons(lesson!.course_id),
    enabled: !!lesson?.course_id,
  });

  // Mark lesson as completed mutation
  const markCompletedMutation = useMutation({
    mutationFn: () => contentService.markLessonCompleted(lessonId!),
    onSuccess: () => {
      // Optionally show toast notification
    },
  });

  // Get video embed URL
  const getVideoEmbedUrl = (videoUrl: string) => {
    if (!videoUrl) return null;

    console.log('🎥 Processing video URL:', videoUrl);

    // YouTube URL conversion
    if (videoUrl.includes('youtube.com/watch?v=')) {
      const videoId = videoUrl.split('v=')[1]?.split('&')[0];
      const embedUrl = `https://www.youtube.com/embed/${videoId}`;
      console.log('🎬 YouTube embed URL:', embedUrl);
      return embedUrl;
    }
    
    if (videoUrl.includes('youtu.be/')) {
      const videoId = videoUrl.split('youtu.be/')[1]?.split('?')[0];
      const embedUrl = `https://www.youtube.com/embed/${videoId}`;
      console.log('🎬 YouTube short embed URL:', embedUrl);
      return embedUrl;
    }

    // Vimeo URL conversion
    if (videoUrl.includes('vimeo.com/')) {
      const videoId = videoUrl.split('vimeo.com/')[1]?.split('?')[0];
      const embedUrl = `https://player.vimeo.com/video/${videoId}`;
      console.log('🎬 Vimeo embed URL:', embedUrl);
      return embedUrl;
    }

    // Google Drive URL conversion
    if (videoUrl.includes('drive.google.com')) {
      let fileId = '';
      
      // Handle different Google Drive URL formats
      if (videoUrl.includes('/file/d/')) {
        fileId = videoUrl.split('/file/d/')[1]?.split('/')[0];
      } else if (videoUrl.includes('id=')) {
        fileId = videoUrl.split('id=')[1]?.split('&')[0];
      }
      
      if (fileId) {
        const embedUrl = `https://drive.google.com/file/d/${fileId}/preview`;
        console.log('🎬 Google Drive preview URL:', embedUrl);
        console.log('📝 Note: Ensure file sharing is set to "Anyone with the link"');
        return embedUrl;
      }
    }

    // OneDrive URL conversion
    if (videoUrl.includes('onedrive.live.com') || videoUrl.includes('1drv.ms')) {
      let embedUrl = videoUrl;
      if (videoUrl.includes('view.aspx')) {
        embedUrl = videoUrl.replace('view.aspx', 'embed.aspx');
      } else if (videoUrl.includes('redir?')) {
        embedUrl = videoUrl + '&embed=1';
      }
      console.log('🎬 OneDrive embed URL:', embedUrl);
      return embedUrl;
    }

    // SharePoint URL conversion
    if (videoUrl.includes('sharepoint.com')) {
      const embedUrl = videoUrl.replace('view.aspx', 'embed.aspx');
      console.log('🎬 SharePoint embed URL:', embedUrl);
      return embedUrl;
    }

    // Direct video URL
    if (videoUrl.match(/\.(mp4|webm|ogg)$/i)) {
      console.log('🎬 Direct video URL:', videoUrl);
      return videoUrl;
    }

    // Return as-is for other platforms
    console.log('🎬 Using URL as-is:', videoUrl);
    return videoUrl;
  };

  const handleMarkComplete = () => {
    markCompletedMutation.mutate();
  };

  const handleNavigateLesson = (direction: 'prev' | 'next') => {
    if (!courseLessons || !lesson) return;

    const currentIndex = courseLessons.findIndex(l => l.id === lesson.id);
    const targetIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;

    if (targetIndex >= 0 && targetIndex < courseLessons.length) {
      navigate(`/student/lessons/${courseLessons[targetIndex].id}`);
    }
  };

  const handleBackToCourse = () => {
    if (lesson?.course_id) {
      navigate(`/student/courses/${lesson.course_id}`);
    } else {
      navigate('/student/courses');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="space-y-6">
        <Button variant="outline" onClick={handleBackToCourse} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Course
        </Button>
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Lesson not found
            </h3>
            <p className="text-gray-600">
              This lesson doesn't exist or you don't have access to it.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const videoEmbedUrl = lesson.video_url ? getVideoEmbedUrl(lesson.video_url) : null;
  const currentLessonIndex = courseLessons?.findIndex(l => l.id === lesson.id) ?? -1;
  const totalLessons = courseLessons?.length ?? 0;
  const hasPrevLesson = currentLessonIndex > 0;
  const hasNextLesson = currentLessonIndex >= 0 && currentLessonIndex < totalLessons - 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="outline" onClick={handleBackToCourse} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Course
        </Button>
        
        <div className="flex items-center gap-2">
          {lesson.is_completed && (
            <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
              <CheckCircle2 className="h-3 w-3 mr-1" />
              Completed
            </Badge>
          )}
          {currentLessonIndex >= 0 && (
            <span className="text-sm text-gray-600">
              Lesson {currentLessonIndex + 1} of {totalLessons}
            </span>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {currentLessonIndex >= 0 && totalLessons > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 font-medium">Course Progress</span>
            <span className="font-semibold text-indigo-600">
              {Math.round(((currentLessonIndex + 1) / totalLessons) * 100)}%
            </span>
          </div>
          <Progress 
            value={((currentLessonIndex + 1) / totalLessons) * 100} 
            className="h-2"
          />
        </div>
      )}

      {/* Main Content */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <CardTitle className="text-2xl mb-2">{lesson.title}</CardTitle>
              {lesson.video_url && (
                <Badge variant="secondary" className="gap-1">
                  <Video className="h-3 w-3" />
                  Video Lesson
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Video Player */}
          {videoEmbedUrl && (
            <div className="space-y-2">
              <div className="relative w-full max-w-4xl mx-auto" style={{ paddingTop: '56.25%' }}>
                {!videoLoaded && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
                    <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
                  </div>
                )}
                <iframe
                  className="absolute top-0 left-0 w-full h-full rounded-lg"
                  src={videoEmbedUrl}
                  title={lesson.title}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                  allowFullScreen
                  onLoad={() => setVideoLoaded(true)}
                />
              </div>
              {lesson.video_url && lesson.video_url.includes('drive.google.com') && (
                <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                  <p className="font-medium mb-1">📝 Google Drive Video</p>
                  <p className="mb-2">If the video doesn't play above, try:</p>
                  <ul className="list-disc ml-5 space-y-1">
                    <li>
                      <a 
                        href={videoEmbedUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Open video in new tab
                      </a>
                    </li>
                    <li>Ensure the file sharing is set to "Anyone with the link"</li>
                    <li>The video file format should be MP4, MOV, or WebM</li>
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Lesson Content */}
          {lesson.content && (
            <div className="prose max-w-none">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Lesson Content
              </h3>
              <div className="text-gray-700 whitespace-pre-wrap bg-gray-50 p-6 rounded-lg">
                {lesson.content}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-6 border-t">
            <Button
              variant="outline"
              onClick={() => handleNavigateLesson('prev')}
              disabled={!hasPrevLesson}
              className="gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous Lesson
            </Button>

            {!lesson.is_completed && (
              <Button
                onClick={handleMarkComplete}
                disabled={markCompletedMutation.isPending}
                className="bg-green-600 hover:bg-green-700 gap-2"
              >
                <CheckCircle2 className="h-4 w-4" />
                {markCompletedMutation.isPending ? 'Marking...' : 'Mark as Complete'}
              </Button>
            )}

            <Button
              variant="outline"
              onClick={() => handleNavigateLesson('next')}
              disabled={!hasNextLesson}
              className="gap-2"
            >
              Next Lesson
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Lesson Navigation */}
      {courseLessons && courseLessons.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">All Lessons in This Course</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {courseLessons.map((courseLesson, index) => (
                <button
                  key={courseLesson.id}
                  onClick={() => navigate(`/student/lessons/${courseLesson.id}`)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    courseLesson.id === lesson.id
                      ? 'bg-indigo-100 border-2 border-indigo-500'
                      : courseLesson.is_completed
                      ? 'bg-green-50 border border-green-200 hover:bg-green-100'
                      : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                        courseLesson.is_completed
                          ? 'bg-green-600 text-white'
                          : courseLesson.id === lesson.id
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-300 text-gray-700'
                      }`}
                    >
                      {courseLesson.is_completed ? (
                        <CheckCircle2 className="h-4 w-4" />
                      ) : (
                        index + 1
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{courseLesson.title}</p>
                    </div>
                    {courseLesson.video_url && (
                      <Video className="h-4 w-4 text-gray-500" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
