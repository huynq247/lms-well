import { Layout } from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Star, Clock, Users, Globe, Award, PlayCircle } from "lucide-react";
import { useParams, useNavigate } from "react-router-dom";

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Mock data - in real app, fetch based on id
  const course = {
    title: "Complete Web Development Bootcamp 2024",
    instructor: "Dr. Angela Yu",
    rating: 4.7,
    reviews: 285000,
    students: 850000,
    duration: "65 hours",
    level: "Beginner",
    price: "$89.99",
    image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&h=600&fit=crop",
    description:
      "Learn to code and become a full-stack web developer with HTML, CSS, JavaScript, React, Node.js, MongoDB and more!",
    whatYouLearn: [
      "Build 16 web development projects for your portfolio",
      "Learn the latest technologies including JavaScript, React, Node and more",
      "Build fully-fledged websites and web apps for your startup or business",
      "Master frontend and backend development",
    ],
    curriculum: [
      { title: "Introduction to Web Development", lessons: 12, duration: "2h 30m" },
      { title: "HTML 5", lessons: 15, duration: "3h 15m" },
      { title: "CSS 3", lessons: 18, duration: "4h 20m" },
      { title: "JavaScript Fundamentals", lessons: 25, duration: "6h 45m" },
      { title: "React.js", lessons: 20, duration: "5h 30m" },
      { title: "Node.js and Express", lessons: 22, duration: "6h 10m" },
    ],
  };

  return (
    <Layout>
      <div className="bg-card border-b">
        <div className="max-w-7xl mx-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <Badge className="mb-4">{course.level}</Badge>
              <h1 className="text-3xl font-bold mb-4">{course.title}</h1>
              <p className="text-lg text-muted-foreground mb-4">{course.description}</p>
              <div className="flex flex-wrap items-center gap-6 text-sm">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-warning text-warning" />
                  <span className="font-semibold">{course.rating}</span>
                  <span className="text-muted-foreground">({course.reviews.toLocaleString()} reviews)</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  <span>{course.students.toLocaleString()} students</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{course.duration} total</span>
                </div>
                <div className="flex items-center gap-1">
                  <Globe className="h-4 w-4" />
                  <span>English</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mt-4">
                Created by <span className="text-primary font-medium">{course.instructor}</span>
              </p>
            </div>

            <Card className="lg:sticky lg:top-24 h-fit">
              <CardContent className="p-6">
                <div className="aspect-video bg-muted rounded-lg mb-4 relative overflow-hidden">
                  <img src={course.image} alt={course.title} className="w-full h-full object-cover" />
                  <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                    <PlayCircle className="h-16 w-16 text-white" />
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-3xl font-bold">{course.price}</p>
                  </div>
                  <Button 
                    className="w-full" 
                    size="lg"
                    onClick={() => navigate(`/learning/${id}`)}
                  >
                    Enroll Now
                  </Button>
                  <Button variant="outline" className="w-full">
                    Add to Cart
                  </Button>
                  <Separator />
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Duration</span>
                      <span className="font-medium">{course.duration}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Level</span>
                      <span className="font-medium">{course.level}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Certificate</span>
                      <Award className="h-4 w-4" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="curriculum">Curriculum</TabsTrigger>
            <TabsTrigger value="instructor">Instructor</TabsTrigger>
            <TabsTrigger value="reviews">Reviews</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h2 className="text-2xl font-semibold mb-4">What you'll learn</h2>
                <div className="grid md:grid-cols-2 gap-3">
                  {course.whatYouLearn.map((item, index) => (
                    <div key={index} className="flex gap-2">
                      <div className="h-5 w-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-primary text-xs">✓</span>
                      </div>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="curriculum" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h2 className="text-2xl font-semibold mb-4">Course Content</h2>
                <div className="space-y-3">
                  {course.curriculum.map((section, index) => (
                    <Card key={index}>
                      <CardContent className="p-4">
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="font-semibold">{section.title}</h3>
                            <p className="text-sm text-muted-foreground">
                              {section.lessons} lessons • {section.duration}
                            </p>
                          </div>
                          <Button variant="ghost" size="sm">
                            Expand
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="instructor" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h2 className="text-2xl font-semibold mb-4">About the Instructor</h2>
                <div className="flex items-start gap-4">
                  <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center text-2xl font-bold">
                    {course.instructor.charAt(0)}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold">{course.instructor}</h3>
                    <p className="text-muted-foreground mb-4">Lead Instructor, Developer</p>
                    <p>
                      Dr. Angela Yu is a developer with a passion for teaching. She's the lead instructor at the London
                      App Brewery, one of the leading in-person coding bootcamps.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reviews" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h2 className="text-2xl font-semibold mb-4">Student Reviews</h2>
                <div className="text-center py-8 text-muted-foreground">Reviews section coming soon</div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default CourseDetail;
