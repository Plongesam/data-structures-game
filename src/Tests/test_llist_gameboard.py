"""
This script will be a simple test that verifies the gamepage
for the linked list game loads correctly.
There is nothing to test on the llist gameboard page currently 

To run this test, make the below changes first:
    1- Safari --> Allow Remote Automation
    2- Change the remote url variable to local in LListGameboard.js
    3- npm run build

How to run:
    1) Run Django: python manage.py runserver
    2) Run the test: python -m unittest test_llist_gameboard.py
"""
import unittest
from selenium import webdriver 
from time import sleep

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        """setup the test"""
        # Web browser instance
        self.driver = webdriver.Safari()
        self.driver.get("http://127.0.0.1:8000/")
        
        # setup to start linked list game
        # setup player
        player_list = self.driver.find_element_by_name('playerList')
        player_list.click()
        player_list.send_keys("Test")
        # choose difficulty
        difficulty_levels = Select(self.driver.find_element_by_name('level'))
        difficulty_levels.select_by_visible_text('Easy')
        #game mode
        dsGame = Select(driver.find_element_by_name('gameDS'))
        dsGame.select_by_visible_text('Linked List Standard')
        selected_dsGame = dsGame.first_selected_option

        self.assertEqual(selected_dsGame.text, 'Linked List Standard')

        # Start Game
        self.driver.find_element_by_name('start_game').click()

    # let the game load
    sleep(5)

    # check llist gamepage is loaded: check state variables are correct
    def test_llist_gamepage_loads(self) :
        self.driver.assertEqual

    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    unittest.main()
    