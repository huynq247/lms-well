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
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  ArrowLeft,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Eye,
  Loader2,
  Trophy,
  Target,
  TrendingUp,
  Shuffle,
  Flame,
  Zap,
  AlertCircle,
  ThumbsUp,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface StudySession {
  deckId: string;
  deckTitle: string;
  totalCards: number;
  currentCardIndex: number;
  showAnswer: boolean;
  studiedCards: Set<string>;
  startTime: Date;
  endTime?: Date;
  isFlipped: boolean;
  shuffled: boolean;
}

export default function StudyFlashcardsPage() {
  const { deckId } = useParams<{ deckId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [session, setSession] = useState<StudySession | null>(null);
  const [currentCard, setCurrentCard] = useState<any>(null);
  const [showCompletionDialog, setShowCompletionDialog] = useState(false);
  const [shuffledCards, setShuffledCards] = useState<any[]>([]);
  const [showReviewDialog, setShowReviewDialog] = useState(false);

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

  // Save study progress mutation
  const saveProgressMutation = useMutation({
    mutationFn: (data: any) => contentService.saveStudyProgress(data),
  });

  // Initialize study session
  useEffect(() => {
    if (deck && cards.length > 0 && !session) {
      const shuffled = [...cards];
      setShuffledCards(shuffled);
      const newSession: StudySession = {
        deckId: deckId!,
        deckTitle: deck.title,
        totalCards: cards.length,
        currentCardIndex: 0,
        showAnswer: false,
        studiedCards: new Set(),
        startTime: new Date(),
        isFlipped: false,
        shuffled: false,
      };
      setSession(newSession);
      setCurrentCard(shuffled[0]);
    }
  }, [deck, cards, deckId, session]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (!session || showCompletionDialog) return;

      switch (event.key) {
        case ' ':
        case 'Enter':
          event.preventDefault();
          handleFlipCard();
          break;
        case 'ArrowRight':
          event.preventDefault();
          handleNext();
          break;
        case 'ArrowLeft':
          event.preventDefault();
          handlePrevious();
          break;
        case 'r':
        case 'R':
          event.preventDefault();
          handleRestart();
          break;
        case 's':
        case 'S':
          event.preventDefault();
          handleShuffle();
          break;
        case 'Escape':
          event.preventDefault();
          handleExit();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [session, showCompletionDialog]);

  const handleFlipCard = () => {
    if (!session) return;
    setSession({ ...session, showAnswer: !session.showAnswer, isFlipped: !session.isFlipped });
  };

  const handleNext = () => {
    if (!session || !currentCard) return;

    const newSession = {
      ...session,
      studiedCards: new Set(session.studiedCards).add(currentCard.id),
      showAnswer: false,
      isFlipped: false,
    };

    if (newSession.currentCardIndex < shuffledCards.length - 1) {
      newSession.currentCardIndex += 1;
      setCurrentCard(shuffledCards[newSession.currentCardIndex]);
      setSession(newSession);
    } else {
      // Session completed
      newSession.endTime = new Date();
      setSession(newSession);
      setShowCompletionDialog(true);
    }
  };

  const handlePrevious = () => {
    if (!session || session.currentCardIndex === 0) return;

    const newSession = {
      ...session,
      currentCardIndex: session.currentCardIndex - 1,
      showAnswer: false,
      isFlipped: false,
    };
    setCurrentCard(shuffledCards[newSession.currentCardIndex]);
    setSession(newSession);
  };

  const handleShuffle = () => {
    if (!session) return;
    const shuffled = [...shuffledCards].sort(() => Math.random() - 0.5);
    setShuffledCards(shuffled);
    setSession({ ...session, currentCardIndex: 0, shuffled: true });
    setCurrentCard(shuffled[0]);
  };

  const handleReviewIncorrect = () => {
    handleRestart();
  };

  const handleRestart = () => {
    if (!deck) return;
    const shuffled = [...cards];
    setShuffledCards(shuffled);
    const newSession: StudySession = {
      deckId: deckId!,
      deckTitle: deck.title,
      totalCards: cards.length,
      currentCardIndex: 0,
      showAnswer: false,
      studiedCards: new Set(),
      startTime: new Date(),
      isFlipped: false,
      shuffled: false,
    };
    setSession(newSession);
    setCurrentCard(shuffled[0]);
    setShowCompletionDialog(false);
  };

  const handleExit = () => {
    navigate(`/student/decks/${deckId}`);
  };

  if (deckLoading || flashcardsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!deck || cards.length === 0) {
    return (
      <div className="space-y-6">
        <Button variant="outline" onClick={handleExit} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Deck
        </Button>
        <Card className="text-center py-12">
          <CardContent>
            <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No flashcards available
            </h3>
            <p className="text-gray-600">
              This deck doesn't have any flashcards to study.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const progressPercentage = session
    ? ((session.currentCardIndex + 1) / session.totalCards) * 100
    : 0;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="outline" onClick={handleExit} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Exit Study
        </Button>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleShuffle} 
            className="gap-2"
            disabled={!session || session.showAnswer}
          >
            <Shuffle className="h-4 w-4" />
            Shuffle
          </Button>
          <Button variant="outline" size="sm" onClick={handleRestart} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Restart
          </Button>
        </div>
      </div>

      {/* Progress Stats */}
      <Card className="border-indigo-200 bg-indigo-50">
        <CardContent className="pt-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-indigo-900">
              {session?.currentCardIndex !== undefined ? session.currentCardIndex + 1 : 0} / {session?.totalCards || 0}
            </p>
            <p className="text-sm text-indigo-600 mt-2">Card Progress</p>
          </div>
        </CardContent>
      </Card>

      {/* Progress Bar */}
      <div className="space-y-2">
        <Progress value={progressPercentage} className="h-3" />
      </div>

      {/* Flashcard with 3D Flip Animation */}
      {currentCard && session && (
        <div className="perspective-1000">
          <div
            className={`relative w-full transition-all duration-700 transform-style-3d cursor-pointer ${
              session.isFlipped ? 'rotate-y-180' : ''
            }`}
            onClick={handleFlipCard}
            style={{ transformStyle: 'preserve-3d' }}
          >
            {/* Front of Card (Question) */}
            <Card 
              className={`border-2 border-indigo-200 backface-hidden ${
                session.isFlipped ? 'invisible' : ''
              }`}
              style={{ backfaceVisibility: 'hidden' }}
            >
              <CardHeader className="border-b bg-gradient-to-r from-indigo-50 to-purple-50">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">
                    {deck.title}
                  </CardTitle>
                  {currentCard.difficulty && (
                    <Badge
                      variant={
                        currentCard.difficulty === 'easy'
                          ? 'default'
                          : currentCard.difficulty === 'hard'
                          ? 'destructive'
                          : 'secondary'
                      }
                    >
                      {currentCard.difficulty}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="p-8">
                <div className="min-h-[300px] flex flex-col items-center justify-center">
                  <div className="text-center w-full">
                    <Eye className="h-12 w-12 text-indigo-400 mx-auto mb-4 opacity-50" />
                    <Badge className="mb-4">Question</Badge>
                    <p className="text-3xl font-semibold text-gray-900 my-8">
                      {currentCard.front}
                    </p>
                    <p className="text-sm text-gray-500 mt-6">
                      Click card or press Space/Enter to reveal answer
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Back of Card (Answer) */}
            <Card 
              className={`absolute inset-0 border-2 border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 backface-hidden rotate-y-180 ${
                !session.isFlipped ? 'invisible' : ''
              }`}
              style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
            >
              <CardHeader className="border-b bg-gradient-to-r from-green-50 to-emerald-50">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">
                    {deck.title}
                  </CardTitle>
                  {currentCard.difficulty && (
                    <Badge
                      variant={
                        currentCard.difficulty === 'easy'
                          ? 'default'
                          : currentCard.difficulty === 'hard'
                          ? 'destructive'
                          : 'secondary'
                      }
                    >
                      {currentCard.difficulty}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="p-8">
                <div className="min-h-[300px] flex flex-col items-center justify-center">
                  <div className="text-center w-full">
                    <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4 opacity-50" />
                    <Badge className="bg-green-600 mb-4">Answer</Badge>
                    <p className="text-3xl font-semibold text-gray-900 my-8">
                      {currentCard.back}
                    </p>
                    <p className="text-sm text-gray-500 mt-2 mb-4">
                      Click card to see question again
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      {currentCard && session && (
        <div className="flex items-center justify-between gap-4">
          <Button
            variant="outline"
            size="lg"
            onClick={handlePrevious}
            disabled={session.currentCardIndex === 0}
            className="flex-1 gap-2"
          >
            <ChevronLeft className="h-5 w-5" />
            Previous
          </Button>
          <Button
            size="lg"
            onClick={handleNext}
            className="flex-1 gap-2 bg-indigo-600 hover:bg-indigo-700"
            disabled={session.currentCardIndex >= session.totalCards - 1 && !session.studiedCards.has(currentCard.id)}
          >
            Next
            <ChevronRight className="h-5 w-5" />
          </Button>
        </div>
      )}

      {/* Completion Dialog */}
      <Dialog open={showCompletionDialog} onOpenChange={setShowCompletionDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-green-100 rounded-full">
                <Trophy className="h-12 w-12 text-green-600" />
              </div>
            </div>
            <DialogTitle className="text-center text-2xl">
              Study Session Complete!
            </DialogTitle>
            <DialogDescription className="text-center">
              Great job! Here's how you did:
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <Card className="border-indigo-200 bg-indigo-50">
              <CardContent className="pt-4">
                <div className="text-center">
                  <CheckCircle2 className="h-12 w-12 text-indigo-600 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-indigo-900 mb-1">
                    {session?.totalCards || 0}
                  </p>
                  <p className="text-sm text-indigo-600">Cards Reviewed</p>
                </div>
              </CardContent>
            </Card>

            <div className="text-center p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border-2 border-green-200">
              <p className="text-lg font-bold text-green-900 mb-1">🎉 Great Work!</p>
              <p className="text-sm text-green-700">You completed the deck!</p>
            </div>
          </div>

          <DialogFooter className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              onClick={handleExit}
            >
              Exit
            </Button>
            <Button
              onClick={handleRestart}
              className="bg-indigo-600 hover:bg-indigo-700 gap-2"
            >
              <RotateCcw className="h-4 w-4" />
              Study Again
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
