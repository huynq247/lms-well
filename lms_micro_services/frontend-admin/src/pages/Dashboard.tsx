import { Layout } from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookOpen, Clock, Award, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";

const Dashboard = () => {
  const enrolledCourses = [
    {
      id: "1",
      title: "Complete Web Development Bootcamp 2024",
      progress: 35,
      lastAccessed: "2 hours ago",
      image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=200&fit=crop",
    },
    {
      id: "2",
      title: "Machine Learning A-Z",
      progress: 12,
      lastAccessed: "1 day ago",
      image: "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400&h=200&fit=crop",
    },
    {
      id: "3",
      title: "The Complete JavaScript Course 2024",
      progress: 68,
      lastAccessed: "5 hours ago",
      image: "https://images.unsplash.com/photo-1593720213428-28a5b9e94613?w=400&h=200&fit=crop",
    },
  ];

  const stats = [
    { label: "Courses Enrolled", value: "12", icon: BookOpen, color: "text-primary" },
    { label: "Hours Learned", value: "156", icon: Clock, color: "text-warning" },
    { label: "Certificates", value: "3", icon: Award, color: "text-success" },
    { label: "Learning Streak", value: "7 days", icon: TrendingUp, color: "text-destructive" },
  ];

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-bold mb-2">Welcome back, John!</h1>
          <p className="text-muted-foreground">Continue your learning journey</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                  </div>
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* In Progress Courses */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold">Continue Learning</h2>
            <Button variant="outline" asChild>
              <Link to="/">Browse More</Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {enrolledCourses.map((course) => (
              <Card key={course.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-video bg-muted relative overflow-hidden">
                  <img src={course.image} alt={course.title} className="w-full h-full object-cover" />
                  <Badge className="absolute top-2 right-2">{course.progress}% Complete</Badge>
                </div>
                <CardContent className="p-4">
                  <h3 className="font-semibold mb-2 line-clamp-2">{course.title}</h3>
                  <Progress value={course.progress} className="mb-2" />
                  <p className="text-sm text-muted-foreground mb-3">Last accessed {course.lastAccessed}</p>
                  <Button className="w-full" asChild>
                    <Link to={`/learning/${course.id}`}>Continue</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Achievements Section */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Achievements</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-primary/5 border border-primary/20">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Award className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="font-semibold text-sm">First Course Completed</p>
                  <p className="text-xs text-muted-foreground">Earned 2 days ago</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-warning/5 border border-warning/20">
                <div className="h-12 w-12 rounded-full bg-warning/10 flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-warning" />
                </div>
                <div>
                  <p className="font-semibold text-sm">7 Day Streak</p>
                  <p className="text-xs text-muted-foreground">Keep it up!</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-success/5 border border-success/20">
                <div className="h-12 w-12 rounded-full bg-success/10 flex items-center justify-center">
                  <BookOpen className="h-6 w-6 text-success" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Fast Learner</p>
                  <p className="text-xs text-muted-foreground">Completed 10 lessons</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;
