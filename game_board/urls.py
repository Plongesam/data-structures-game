"""
    URL's for the Game Board app.
"""
from django.urls import path
from game_board.api import api
from game_board.api import llist_api
from . import views

urlpatterns = [

    # Views 
    path('', views.game_board, name='game-board'),

    # Game Play API Calls For AVL
    path('api', api.api_overview, name='game-board-api_overview'),
    path('api/start_game/<str:difficulty>/<str:player_ids>/<str:data_structures>', api.start_game, name='game-board-start_game'),
    path('api/board/<str:game_id>', api.board, name='game-board-game_status'),
    path('api/rebalance/<str:game_id>/<str:user_id>/<str:token>', api.rebalance, name='game-board-rebalance'),
    path('api/ai_pick/<str:game_id>/<str:user_id>/<str:token>', api.ai_pick, name='game-board-ai_pick'),
    path('api/action/<str:card>/<str:game_id>/<str:user_id>/<str:token>', api.action, name='game-board-action'),

    #Game Play API Calls For Linked List
    path('llist_api', llist_api.api_overview, name='llist-game-board-api_overview'),
    path('llist_api/start_game/<str:difficulty>/<str:player_ids>/<str:data_structures>', llist_api.start_game, name='llist-game-board-start_game'),
    path('llist_api/board/<str:game_id>', llist_api.board, name='llist-game-board-game_status'),

    path('llist_api/dig_tunnel/<str:game_id>/<str:origin>/<str:destination>', llist_api.dig_tunnel, name='llist-game-board-dig_tunnel'),
    path('llist_api/dig_chamber/<str:game_id>/<str:origin>/<str:move_ant>', llist_api.dig_chamber, name='llist-game-board-dig_chamber'),
    path('llist_api/fill_chamber/<str:game_id>/<str:origin>/<str:to_fill>', llist_api.fill_chamber, name='llist-game-board-fill_chamber'),
    path('llist_api/spawn_ant/<str:game_id>', llist_api.spawn_ant, name='llist-game-board-spawn_ant'),
    path('llist_api/forage/<str:game_id>/<str:difficulty>/<str:dest>', llist_api.forage, name='llist-game-board-forage'),
    path('llist_api/move_food/<str:game_id>/<str:start>/<str:dest>', llist_api.move_food, name='llist-game-board-move_food'),
    path('llist_api/move_ant/<str:game_id>/<str:start>/<str:dest>', llist_api.move_ant, name='llist-game-board-move_ant'),
]
