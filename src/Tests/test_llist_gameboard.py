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
# BEFORE TESTING: for this iteration (4/29/21), 
# in LListGameboard.js : UNCOMMENT and COMMENT the appropriate lines in 
#                        renderChambers() (lines 250 & 251)

import unittest
from selenium import webdriver 
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        """setup the test"""
        # Web browser instance
        self.driver = webdriver.Safari()
        self.driver.get("http://127.0.0.1:8000/")

    def test_homepage(self):
        """setup the test"""
        
        # setup to start linked list game
        # setup player
        player_list = self.driver.find_element_by_name('playerList')
        player_list.click()
        player_list.send_keys("Test")
        # choose difficulty
        difficulty_levels = Select(self.driver.find_element_by_name('level'))
        difficulty_levels.select_by_visible_text('Easy')
        #game mode
        dsGame = Select(self.driver.find_element_by_name('gameDS'))
        dsGame.select_by_visible_text('Linked List Standard')
        selected_dsGame = dsGame.first_selected_option

        self.assertEqual(selected_dsGame.text, 'Linked List Standard')
        sleep(5)
        # Start Game
        self.driver.find_element_by_name('start_game').click()
        sleep(1)


    # check llist gamepage is loaded: check state variables are correct
    #def test_llist_gamepage_loads(self) :
        #self.driver.assertEqual

    # checks that the chambers and tunnels render
    def test_chamber_rendering(self) :
        self.driver.find_element_by_id('chamberButton').click()
        self.driver.find_element_by_id('tunnelButton').click()
        self.driver.find_element_by_name('chamberFoodUI')


    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    unittest.main()
    