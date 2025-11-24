import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import contentService from '@/services/content';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  ArrowLeft,
  Play,
  RotateCcw,
  Loader2,
  Layers,
  GraduationCap,
} from 'lucide-react';

export default function DeckDetailPage() {
  const { deckId } = useParams<{ deckId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [flippedCards, setFlippedCards] = useState<Set<string>>(new Set());

  // Fetch deck details
  const { data: deck, isLoading: deckLoading } = useQuery({
    queryKey: ['deck', deckId],
    queryFn: () => contentService.getDeck(deckId!),
    enabled: !!deckId,
  });

  // Fetch flashcards
  const { data: flashcards, isLoading: flashcardsLoading } = useQuery({
    queryKey: ['flashcards', deckId],
    queryFn: () => contentService.getFlashcards(deckId!),
    enabled: !!deckId,
  });

  const cards = flashcards || [];

  const handleFlipCard = (cardId: string) => {
    const newFlipped = new Set(flippedCards);
    if (newFlipped.has(cardId)) {
      newFlipped.delete(cardId);
    } else {
      newFlipped.add(cardId);
    }
    setFlippedCards(newFlipped);
  };

  const handleStartStudy = () => {
    navigate(`/student/decks/${deckId}/study`);
  };

  if (deckLoading || flashcardsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!deck) {
    return (
      <div className="space-y-6">
        <Button
          variant="outline"
          onClick={() => navigate('/student/decks')}
          className="gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Decks
        </Button>
        <Card className="text-center py-12">
          <CardContent>
            <Layers className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Deck not found
            </h3>
            <p className="text-gray-600">
              This deck doesn't exist or you don't have access to it.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={() => navigate('/student/decks')}
          className="gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Decks
        </Button>

        {cards.length > 0 && (
          <Button
            onClick={handleStartStudy}
            className="bg-indigo-600 hover:bg-indigo-700 gap-2"
            size="lg"
          >
            <Play className="h-5 w-5" />
            Start Studying
          </Button>
        )}
      </div>

      {/* Deck Info */}
      <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50 to-white">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-2xl mb-2">{deck.title}</CardTitle>
              <CardDescription className="text-base">
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Layers className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Cards</p>
                <p className="text-lg font-semibold">{cards.length}</p>
              </div>
            </div>
            {deck.difficulty && (
              <div className="flex items-center gap-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <RotateCcw className="h-5 w-5 text-yellow-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Difficulty</p>
                  <Badge className={getDifficultyColor(deck.difficulty)}>
                    {deck.difficulty}
                  </Badge>
                </div>
              </div>
            )}
            {deck.instructor_name && (
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <GraduationCap className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Instructor</p>
                  <p className="text-sm font-semibold">{deck.instructor_name}</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Flashcards */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          All Flashcards ({cards.length})
        </h2>
        
        {cards.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Layers className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No flashcards yet
              </h3>
              <p className="text-gray-600">
                This deck doesn't have any flashcards yet.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cards.map((card, index) => {
              const isFlipped = flippedCards.has(card.id);
              return (
                <div
                  key={card.id}
                  onClick={() => handleFlipCard(card.id)}
                  className="cursor-pointer group perspective-1000"
                >
                  <div
                    className={`relative h-48 transition-transform duration-500 transform-style-3d ${
                      isFlipped ? 'rotate-y-180' : ''
                    }`}
                  >
                    {/* Front of card */}
                    <Card
                      className={`absolute inset-0 backface-hidden border-2 ${
                        isFlipped ? 'invisible' : ''
                      } hover:border-indigo-400 transition-colors`}
                    >
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline">Card {index + 1}</Badge>
                          {card.difficulty && (
                            <Badge className={getDifficultyColor(card.difficulty)}>
                              {card.difficulty}
                            </Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="flex items-center justify-center h-24">
                        <p className="text-center font-medium text-gray-900">
                          {card.front}
                        </p>
                      </CardContent>
                      <div className="absolute bottom-3 left-0 right-0 text-center">
                        <p className="text-xs text-gray-500">Click to flip</p>
                      </div>
                    </Card>

                    {/* Back of card */}
                    <Card
                      className={`absolute inset-0 backface-hidden border-2 rotate-y-180 ${
                        !isFlipped ? 'invisible' : ''
                      } bg-indigo-50 border-indigo-200 hover:border-indigo-400 transition-colors`}
                    >
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <Badge className="bg-indigo-600">Answer</Badge>
                          {card.difficulty && (
                            <Badge className={getDifficultyColor(card.difficulty)}>
                              {card.difficulty}
                            </Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="flex items-center justify-center h-24">
                        <p className="text-center font-medium text-gray-900">
                          {card.back}
                        </p>
                      </CardContent>
                      <div className="absolute bottom-3 left-0 right-0 text-center">
                        <p className="text-xs text-indigo-600">Click to flip back</p>
                      </div>
                    </Card>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Study Button (bottom) */}
      {cards.length > 0 && (
        <div className="flex justify-center pt-6">
          <Button
            onClick={handleStartStudy}
            size="lg"
            className="bg-indigo-600 hover:bg-indigo-700 gap-2"
          >
            <Play className="h-5 w-5" />
            Start Studying ({cards.length} cards)
          </Button>
        </div>
      )}
    </div>
  );
}
