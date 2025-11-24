import { Layout } from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { PlayCircle, CheckCircle2, Lock, ChevronRight } from "lucide-react";
import { useParams } from "react-router-dom";
import { useState } from "react";

const Learning = () => {
  const { id } = useParams();
  const [currentLesson, setCurrentLesson] = useState(0);

  const sections = [
    {
      title: "Introduction to Web Development",
      lessons: [
        { title: "Welcome to the Course", duration: "5:30", completed: true },
        { title: "Course Overview", duration: "8:45", completed: true },
        { title: "Setting Up Your Environment", duration: "12:20", completed: false },
      ],
    },
    {
      title: "HTML Fundamentals",
      lessons: [
        { title: "Introduction to HTML", duration: "15:30", completed: false },
        { title: "HTML Elements and Tags", duration: "18:45", completed: false },
        { title: "Forms and Input", duration: "22:10", completed: false },
      ],
    },
    {
      title: "CSS Basics",
      lessons: [
        { title: "Introduction to CSS", duration: "14:20", completed: false },
        { title: "Selectors and Properties", duration: "16:55", completed: false },
        { title: "Layout with Flexbox", duration: "20:30", completed: false },
      ],
    },
  ];

  const totalLessons = sections.reduce((acc, section) => acc + section.lessons.length, 0);
  const completedLessons = sections.reduce(
    (acc, section) => acc + section.lessons.filter((l) => l.completed).length,
    0
  );
  const progress = (completedLessons / totalLessons) * 100;

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-4 h-[calc(100vh-4rem)]">
        {/* Video Player Section */}
        <div className="lg:col-span-3 flex flex-col">
          <div className="aspect-video bg-black flex items-center justify-center">
            <div className="text-center text-white">
              <PlayCircle className="h-20 w-20 mx-auto mb-4 opacity-80" />
              <p className="text-lg">Video Player Placeholder</p>
              <p className="text-sm opacity-70">Course content will load here</p>
            </div>
          </div>

          <div className="p-6 flex-1 overflow-y-auto">
            <h1 className="text-2xl font-bold mb-2">Welcome to the Course</h1>
            <p className="text-muted-foreground mb-4">
              In this introductory lesson, you'll learn what to expect from this course and how to get the most out of
              your learning experience.
            </p>

            <div className="flex gap-4 mb-6">
              <Button>Mark as Complete</Button>
              <Button variant="outline">Next Lesson</Button>
            </div>

            <Separator className="my-6" />

            <div>
              <h2 className="text-xl font-semibold mb-4">Course Notes</h2>
              <Card>
                <CardContent className="p-4">
                  <p className="text-muted-foreground">
                    Add your personal notes here as you progress through the course. This is a great way to remember
                    key concepts and come back to important information later.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Curriculum Sidebar */}
        <div className="border-l bg-card overflow-y-auto">
          <div className="p-4 border-b sticky top-0 bg-card z-10">
            <h2 className="font-semibold mb-2">Course Content</h2>
            <Progress value={progress} className="h-2" />
            <p className="text-sm text-muted-foreground mt-2">
              {completedLessons} of {totalLessons} lessons completed
            </p>
          </div>

          <div className="p-2">
            {sections.map((section, sectionIndex) => (
              <div key={sectionIndex} className="mb-2">
                <div className="px-3 py-2 font-medium text-sm bg-muted rounded-md">
                  Section {sectionIndex + 1}: {section.title}
                </div>
                <div className="mt-1 space-y-1">
                  {section.lessons.map((lesson, lessonIndex) => (
                    <button
                      key={lessonIndex}
                      onClick={() => setCurrentLesson(sectionIndex * 100 + lessonIndex)}
                      className="w-full text-left px-3 py-2 rounded-md hover:bg-accent transition-colors flex items-center gap-2 group"
                    >
                      {lesson.completed ? (
                        <CheckCircle2 className="h-4 w-4 text-success flex-shrink-0" />
                      ) : (
                        <div className="h-4 w-4 rounded-full border-2 border-muted-foreground flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm truncate">{lesson.title}</p>
                        <p className="text-xs text-muted-foreground">{lesson.duration}</p>
                      </div>
                      <ChevronRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Learning;
