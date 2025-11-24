import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import contentService, { Flashcard } from '@/services/content';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Plus, Edit, Trash2, ArrowLeft, GraduationCap } from 'lucide-react';
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

export default function DeckDetailPage() {
  const { deckId } = useParams<{ deckId: string }>();
  const navigate = useNavigate();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedCard, setSelectedCard] = useState<Flashcard | null>(null);
  const [formData, setFormData] = useState({
    front: '',
    back: '',
    order: 1,
    difficulty: 'medium',
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: deck } = useQuery({
    queryKey: ['deck', deckId],
    queryFn: () => contentService.getDeck(deckId!),
    enabled: !!deckId,
  });

  const { data: flashcards, isLoading } = useQuery({
    queryKey: ['flashcards', deckId],
    queryFn: () => contentService.getFlashcards(deckId!),
    enabled: !!deckId,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => contentService.createFlashcard(deckId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards', deckId] });
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      setIsCreateOpen(false);
      resetForm();
      toast({ title: 'Flashcard Created', description: 'Flashcard has been created successfully' });
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed to create flashcard', variant: 'destructive' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => contentService.updateFlashcard(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards', deckId] });
      setIsEditOpen(false);
      setSelectedCard(null);
      toast({ title: 'Flashcard Updated', description: 'Flashcard has been updated successfully' });
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed to update flashcard', variant: 'destructive' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: contentService.deleteFlashcard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards', deckId] });
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      setIsDeleteOpen(false);
      setSelectedCard(null);
      toast({ title: 'Flashcard Deleted', description: 'Flashcard has been deleted successfully' });
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed to delete flashcard', variant: 'destructive' });
    },
  });

  const resetForm = () => {
    setFormData({ front: '', back: '', order: (flashcards?.length || 0) + 1, difficulty: 'medium' });
  };

  const handleCreate = () => {
    createMutation.mutate({ ...formData, deck_id: deckId });
  };

  const handleEdit = (card: Flashcard) => {
    setSelectedCard(card);
    setFormData({
      front: card.front,
      back: card.back,
      order: card.order,
      difficulty: card.difficulty || 'medium',
    });
    setIsEditOpen(true);
  };

  const handleUpdate = () => {
    if (selectedCard) {
      updateMutation.mutate({ id: selectedCard.id, data: formData });
    }
  };

  const handleDeleteClick = (card: Flashcard) => {
    setSelectedCard(card);
    setIsDeleteOpen(true);
  };

  const handleDelete = () => {
    if (selectedCard) {
      deleteMutation.mutate(selectedCard.id);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/admin/decks')}>
          <ArrowLeft size={16} className="mr-2" />
          Back to Decks
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-6 w-6 text-purple-600" />
                {deck?.title}
              </CardTitle>
              <p className="text-gray-600 mt-2">{deck?.description}</p>
            </div>
            <Badge>{flashcards?.length || 0} cards</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Button onClick={() => setIsCreateOpen(true)} className="gap-2">
            <Plus size={20} />
            Add Flashcard
          </Button>
        </CardContent>
      </Card>

      {flashcards && flashcards.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-16">Order</TableHead>
              <TableHead>Front</TableHead>
              <TableHead>Back</TableHead>
              <TableHead>Difficulty</TableHead>
              <TableHead className="w-32">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {flashcards.map((card) => (
              <TableRow key={card.id}>
                <TableCell>{card.order}</TableCell>
                <TableCell className="font-medium">{card.front}</TableCell>
                <TableCell className="text-gray-600">{card.back}</TableCell>
                <TableCell>
                  <Badge variant={card.difficulty === 'hard' ? 'destructive' : card.difficulty === 'easy' ? 'default' : 'secondary'}>
                    {card.difficulty || 'Medium'}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleEdit(card)}>
                      <Edit size={14} />
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDeleteClick(card)}>
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
          <GraduationCap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No flashcards yet</h3>
          <p className="text-gray-600 mb-4">Add your first flashcard to this deck</p>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus size={20} className="mr-2" />
            Add Flashcard
          </Button>
        </div>
      )}

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add Flashcard</DialogTitle>
            <DialogDescription>Create a new flashcard for this deck</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="front">Front (Question)</Label>
              <Textarea
                id="front"
                value={formData.front}
                onChange={(e) => setFormData({ ...formData, front: e.target.value })}
                placeholder="Enter the front of the card (question)..."
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="back">Back (Answer)</Label>
              <Textarea
                id="back"
                value={formData.back}
                onChange={(e) => setFormData({ ...formData, back: e.target.value })}
                placeholder="Enter the back of the card (answer)..."
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="order">Order</Label>
                <Input
                  id="order"
                  type="number"
                  value={formData.order}
                  onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 1 })}
                />
              </div>
              <div>
                <Label htmlFor="difficulty">Difficulty</Label>
                <Input
                  id="difficulty"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setIsCreateOpen(false); resetForm(); }}>Cancel</Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Flashcard'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Flashcard</DialogTitle>
            <DialogDescription>Update flashcard information</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_front">Front (Question)</Label>
              <Textarea
                id="edit_front"
                value={formData.front}
                onChange={(e) => setFormData({ ...formData, front: e.target.value })}
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="edit_back">Back (Answer)</Label>
              <Textarea
                id="edit_back"
                value={formData.back}
                onChange={(e) => setFormData({ ...formData, back: e.target.value })}
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_order">Order</Label>
                <Input
                  id="edit_order"
                  type="number"
                  value={formData.order}
                  onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 1 })}
                />
              </div>
              <div>
                <Label htmlFor="edit_difficulty">Difficulty</Label>
                <Input
                  id="edit_difficulty"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setIsEditOpen(false); setSelectedCard(null); resetForm(); }}>Cancel</Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Updating...' : 'Update Flashcard'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Flashcard?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the flashcard. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setSelectedCard(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
