import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import contentService from '@/services/content';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Layers,
  Search,
  GraduationCap,
  Play,
  Loader2,
  Brain,
} from 'lucide-react';

export default function DecksPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  // Fetch decks (backend filters by student assignments or public decks)
  const { data: decks, isLoading } = useQuery({
    queryKey: ['decks', user?.id],
    queryFn: contentService.getDecks,
    enabled: !!user,
  });

  // Filter decks by search term
  const filteredDecks = (decks || []).filter(deck =>
    deck.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    deck.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewDeck = (deckId: string) => {
    navigate(`/student/decks/${deckId}`);
  };

  const handleStudyDeck = (deckId: string) => {
    navigate(`/student/decks/${deckId}/study`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Brain className="h-8 w-8 text-indigo-600" />
          Flashcard Decks
        </h1>
        <p className="text-gray-600 mt-2">
          Study flashcards to reinforce your learning
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search decks..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-indigo-200 bg-indigo-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-indigo-600 rounded-lg">
                <Layers className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-indigo-900">
                  {filteredDecks.length}
                </p>
                <p className="text-sm text-indigo-600">Available Decks</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-purple-200 bg-purple-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-600 rounded-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-900">
                  {filteredDecks.reduce((sum, d) => sum + (d.total_flashcards || 0), 0)}
                </p>
                <p className="text-sm text-purple-600">Total Flashcards</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-600 rounded-lg">
                <Play className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-900">
                  {filteredDecks.filter(d => d.is_published).length}
                </p>
                <p className="text-sm text-blue-600">Active Decks</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Decks Grid */}
      {filteredDecks.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <Layers className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No flashcard decks found
            </h3>
            <p className="text-gray-600">
              {searchTerm
                ? 'Try adjusting your search terms'
                : 'No flashcard decks are available yet. Check back later or contact your teacher.'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDecks.map((deck) => (
            <Card
              key={deck.id}
              className="hover:shadow-lg transition-all duration-200 border-gray-200 hover:border-indigo-300"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg line-clamp-2">
                      {deck.title}
                    </CardTitle>
                    <CardDescription className="mt-2 line-clamp-2">
                      {deck.description || 'No description available'}
                    </CardDescription>
                  </div>
                  {deck.is_published && (
                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                      Active
                    </Badge>
                  )}
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 flex items-center gap-1">
                      <Layers className="h-4 w-4 text-indigo-600" />
                      Flashcards
                    </span>
                    <span className="font-semibold text-indigo-600">
                      {deck.total_flashcards || 0} cards
                    </span>
                  </div>

                  {deck.difficulty && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Difficulty</span>
                      <Badge
                        variant={
                          deck.difficulty === 'easy'
                            ? 'default'
                            : deck.difficulty === 'hard'
                            ? 'destructive'
                            : 'secondary'
                        }
                      >
                        {deck.difficulty}
                      </Badge>
                    </div>
                  )}

                  {deck.instructor_name && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <GraduationCap className="h-4 w-4 text-indigo-600" />
                      <span>{deck.instructor_name}</span>
                    </div>
                  )}

                  {/* Progress (if available) */}
                  {deck.progress !== undefined && (
                    <div className="pt-2">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-semibold text-indigo-600">
                          {Math.round(deck.progress)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${deck.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>

              <CardFooter className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => handleViewDeck(deck.id)}
                  className="flex-1"
                >
                  <Layers className="h-4 w-4 mr-2" />
                  View Cards
                </Button>
                <Button
                  onClick={() => handleStudyDeck(deck.id)}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700"
                  disabled={!deck.total_flashcards || deck.total_flashcards === 0}
                >
                  <Play className="h-4 w-4 mr-2" />
                  Study
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
