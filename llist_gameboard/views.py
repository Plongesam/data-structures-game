"""
    Game Board app views.
"""
from django.shortcuts import render

def llist_game_board(request):
    """Redirect to the game board view."""

    # Change this to the actual React frontend for game board when ready.
    print("here")
    return render(request, 'index.html')