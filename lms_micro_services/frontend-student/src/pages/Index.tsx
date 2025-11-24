import { Layout } from "@/components/Layout";
import { CourseCard } from "@/components/CourseCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const courses = [
  {
    id: "1",
    title: "Complete Web Development Bootcamp 2024",
    instructor: "Dr. Angela Yu",
    rating: 4.7,
    students: 850000,
    duration: "65 hours",
    level: "Beginner",
    price: "$89.99",
    image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=450&fit=crop",
  },
  {
    id: "2",
    title: "Machine Learning A-Z: AI, Python & R",
    instructor: "Kirill Eremenko",
    rating: 4.5,
    students: 720000,
    duration: "44 hours",
    level: "Intermediate",
    price: "$94.99",
    image: "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=450&fit=crop",
  },
  {
    id: "3",
    title: "The Complete JavaScript Course 2024",
    instructor: "Jonas Schmedtmann",
    rating: 4.8,
    students: 650000,
    duration: "69 hours",
    level: "All Levels",
    price: "$84.99",
    image: "https://images.unsplash.com/photo-1593720213428-28a5b9e94613?w=800&h=450&fit=crop",
  },
  {
    id: "4",
    title: "AWS Certified Solutions Architect",
    instructor: "Stephane Maarek",
    rating: 4.6,
    students: 580000,
    duration: "27 hours",
    level: "Intermediate",
    price: "$79.99",
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=450&fit=crop",
  },
  {
    id: "5",
    title: "Python for Data Science and Machine Learning",
    instructor: "Jose Portilla",
    rating: 4.7,
    students: 520000,
    duration: "25 hours",
    level: "Intermediate",
    price: "$89.99",
    image: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&h=450&fit=crop",
  },
  {
    id: "6",
    title: "React - The Complete Guide 2024",
    instructor: "Maximilian Schwarzmüller",
    rating: 4.6,
    students: 480000,
    duration: "49 hours",
    level: "All Levels",
    price: "$94.99",
    image: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=450&fit=crop",
  },
];

const Index = () => {
  return (
    <Layout>
      <div className="p-6">
        {/* Hero Section */}
        <div className="mb-8 bg-gradient-to-r from-primary/10 to-primary/5 rounded-lg p-8">
          <h1 className="text-4xl font-bold mb-2">Learn without limits</h1>
          <p className="text-lg text-muted-foreground">
            Start, switch, or advance your career with thousands of courses from world-class instructors
          </p>
        </div>

        {/* Course Categories */}
        <Tabs defaultValue="all" className="mb-8">
          <TabsList>
            <TabsTrigger value="all">All Courses</TabsTrigger>
            <TabsTrigger value="development">Development</TabsTrigger>
            <TabsTrigger value="design">Design</TabsTrigger>
            <TabsTrigger value="business">Business</TabsTrigger>
            <TabsTrigger value="data">Data Science</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map((course) => (
                <CourseCard key={course.id} {...course} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="development" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.filter((c) => ["1", "3", "6"].includes(c.id)).map((course) => (
                <CourseCard key={course.id} {...course} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="design" className="mt-6">
            <div className="text-center py-12 text-muted-foreground">
              No design courses available yet
            </div>
          </TabsContent>

          <TabsContent value="business" className="mt-6">
            <div className="text-center py-12 text-muted-foreground">
              No business courses available yet
            </div>
          </TabsContent>

          <TabsContent value="data" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.filter((c) => ["2", "5"].includes(c.id)).map((course) => (
                <CourseCard key={course.id} {...course} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Index;
