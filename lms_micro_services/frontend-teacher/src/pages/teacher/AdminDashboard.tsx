import { useAuth } from '@/contexts/AuthContext';
import { useQuery } from '@tanstack/react-query';
import contentService from '@/services/content';
import userService from '@/services/user';
import assignmentService from '@/services/assignment';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, BookOpen, GraduationCap, FileText, TrendingUp } from 'lucide-react';

export default function AdminDashboard() {
  const { user } = useAuth();

  // Fetch statistics
  const { data: usersData } = useQuery({
    queryKey: ['users'],
    queryFn: userService.getUsers,
  });

  const { data: coursesData } = useQuery({
    queryKey: ['courses'],
    queryFn: contentService.getCourses,
  });

  const { data: assignmentsData } = useQuery({
    queryKey: ['assignments'],
    queryFn: assignmentService.getAssignments,
  });

  const users = usersData?.users || [];
  const courses = coursesData?.courses || [];
  const assignments = assignmentsData || [];

  const totalUsers = users.length;
  const activeStudents = users.filter((u) => u.role === 'STUDENT' && u.is_active).length;
  const totalCourses = courses.length;
  const activeCourses = courses.filter((c) => c.is_active).length;
  const totalAssignments = assignments.length;

  const stats = [
    {
      title: 'Total Users',
      value: totalUsers,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Total Courses',
      value: totalCourses,
      icon: BookOpen,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Active Students',
      value: activeStudents,
      icon: GraduationCap,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Assignments',
      value: totalAssignments,
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  // Recent courses
  const recentCourses = courses
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back, {user?.name || user?.username}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-3xl font-bold mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.bgColor} p-3 rounded-full`}>
                    <Icon className={`${stat.color} w-6 h-6`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Courses */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              Recent Courses
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentCourses.length > 0 ? (
              <div className="space-y-4">
                {recentCourses.map((course) => (
                  <div key={course.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{course.title}</h4>
                      <p className="text-sm text-gray-500 line-clamp-1">{course.description}</p>
                    </div>
                    <Badge variant={course.is_active ? 'default' : 'secondary'}>
                      {course.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No courses yet</p>
            )}
          </CardContent>
        </Card>

        {/* System Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              System Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-green-50 p-2 rounded">
                    <BookOpen className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Active Courses</p>
                    <p className="text-xs text-gray-500">Currently published</p>
                  </div>
                </div>
                <span className="text-2xl font-bold">{activeCourses}</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-50 p-2 rounded">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Teachers</p>
                    <p className="text-xs text-gray-500">Registered instructors</p>
                  </div>
                </div>
                <span className="text-2xl font-bold">
                  {users.filter((u) => u.role === 'TEACHER').length}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-purple-50 p-2 rounded">
                    <GraduationCap className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Students</p>
                    <p className="text-xs text-gray-500">Total enrolled</p>
                  </div>
                </div>
                <span className="text-2xl font-bold">
                  {users.filter((u) => u.role === 'STUDENT').length}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-orange-50 p-2 rounded">
                    <FileText className="w-5 h-5 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Assignments</p>
                    <p className="text-xs text-gray-500">Total created</p>
                  </div>
                </div>
                <span className="text-2xl font-bold">{totalAssignments}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
