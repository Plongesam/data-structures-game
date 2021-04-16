"""
This script is a simple test that tests the ant actions menu.

To run this test, make the below changes first:
    1- Safari --> Allow Remote Automation
    2- Change the remote url variable to local in LListGameboard.js
    3- npm run build

How to run:
    1) Run Django: python manage.py runserver
    2) Run the test: python -m unittest test_ant_actions.py
"""
import unittest
import requests
from selenium import webdriver 
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        """setup the test"""
        # Web browser instance
        self.driver = webdriver.Safari()
#       self.driver.get("http://127.0.0.1:8000/game_board/llist_api")
        self.driver.get("http://127.0.0.1:3000/game_board/llist_api")


    def test_actions_menu(self):

        """
        choose each option in the first action drop down menu and check
        that each following action drop down displays the correct options
        """
        # dig chamber
        actions = Select(self.driver.find_element_by_name('action'))
        actions.select_by_visible_text('Dig Chamber')
        selected_action = actions.first_selected_option

        actions2 = Select(self.driver.find_element_by_name('action2'))
        actions2.select_by_visible_text('Choose Tunnel...')
        selected_action2 = actions2.first_selected_option

        self.assertEqual(selected_action.text, 'Dig Chamber')
        self.assertEqual(selected_action2.text, 'Choose Tunnel...')
        sleep(1)

        # dig tunnel
        actions = Select(self.driver.find_element_by_name('action'))
        actions.select_by_visible_text('Dig Tunnel')
        selected_action = actions.first_selected_option

        actions2 = Select(self.driver.find_element_by_name('action2'))
        actions2.select_by_visible_text('Choose chamber...')
        selected_action2 = actions2.first_selected_option

        self.assertEqual(selected_action.text, 'Dig Tunnel')
        self.assertEqual(selected_action2.text, 'Choose chamber...')
        sleep(1)

        # Forage
        actions = Select(self.driver.find_element_by_name('action'))
        actions.select_by_visible_text('Forage')
        selected_action = actions.first_selected_option

        actions2 = Select(self.driver.find_element_by_name('action2'))
        actions2.select_by_visible_text('Choose ant...')
        selected_action2 = actions2.first_selected_option

        self.assertEqual(selected_action.text, 'Forage')
        self.assertEqual(selected_action2.text, 'Choose ant...')
        sleep(1)

        # Move
        actions = Select(self.driver.find_element_by_name('action'))
        actions.select_by_visible_text('Move')
        selected_action = actions.first_selected_option

        actions2 = Select(self.driver.find_element_by_name('action2'))
        actions2.select_by_visible_text('Choose ant...')
        selected_action2 = actions2.first_selected_option

        actions3 = Select(self.driver.find_element_by_name('move_to_chamber'))
        actions3.select_by_visible_text('Choose Chamber...')
        selected_action3 = actions3.first_selected_option

        self.assertEqual(selected_action.text, 'Move')
        self.assertEqual(selected_action2.text, 'Choose ant...')
        self.assertEqual(selected_action3.text, 'Choose Chamber...')
        sleep(1)

        # dig tunnel
        actions = Select(self.driver.find_element_by_name('action'))
        actions.select_by_visible_text('Fill Chamber')
        selected_action = actions.first_selected_option

        actions2 = Select(self.driver.find_element_by_name('action2'))
        actions2.select_by_visible_text('Choose chamber...')
        selected_action2 = actions2.first_selected_option

        self.assertEqual(selected_action.text, 'Fill Chamber')
        self.assertEqual(selected_action2.text, 'Choose chamber...')
        sleep(1)
        
    
    
    



    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    unittest.main()