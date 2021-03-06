"""
This script is a unit test that uses Selenium to verify
the content of the nodes in the graph.
More specifically, it checks the node IDs and their
corresponding node points with what is expected using
the Game Board API.

To run this test, make the below changes first:
    1- Safari --> Allow Remote Automation
    2- Change the remote url variable to local in GameBoard.js
    3- npm run build

How to run:
    1) Run Django: python manage.py runserver
    2) Run the test: python -m unittest test_node_text.py
"""
import json
import unittest
from time import sleep
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


class TestStringMethods(unittest.TestCase):
    """Tests contents of the nodes in front-end."""

    def setUp(self):
        """Setup the test"""
        # Web Browser Instance
        self.driver = webdriver.Safari()
        self.driver.get("http://127.0.0.1:8000/")

        # Setup game players
        player_list = self.driver.find_element_by_name('playerList')
        player_list.click()
        player_list.send_keys(Keys.COMMAND + "a")
        player_list.send_keys(Keys.DELETE)
        player_list.send_keys("ID1,ID2")

        # Choose difficulty
        difficulty_levels = Select(self.driver.find_element_by_name('level'))
        difficulty_levels.select_by_visible_text('Easy')

        # Start Game
        self.driver.find_element_by_name('start_game').click()

        # Let game load
        sleep(5)

        # Collect node points and ids
        node_points = self.driver.find_elements(By.XPATH, '//div[@id="root"]//div[@id="graph"]//div[@class="view-wrapper"]\
        /*[name()="svg"]//*[@class="view"]//*[@class="entities"]//*[name()="g"]//*[@id="graph_node"]//*[@id="node_points_text"]')
        node_ids = self.driver.find_elements(By.XPATH, '//div[@id="root"]//div[@id="graph"]//div[@class="view-wrapper"]\
        /*[name()="svg"]//*[@class="view"]//*[@class="entities"]//*[name()="g"]//*[@id="graph_node"]//*[@id="node_id_text"]')

        self.points = list()
        self.ids = list()

        # Extract each point and node ID from the website as text
        for point in node_points:
            self.points.append(int(point.text.strip()))
        for id_ in node_ids:
            self.ids.append(id_.text.strip())

        # Get cookies
        cookies = self.driver.get_cookies()
        game_id = ""
        for cookie in cookies:
            if cookie['name'] == 'game_id':
                game_id = cookie['value']

        # Pull the expected game from API
        url = 'http://127.0.0.1:8000/game_board/api/board/' + game_id
        response = requests.get(url)
        board = json.loads(response.text)
        self.check = board['graph']['node_points']

        # End the test. Closes the browser.
        self.driver.close()

    def test_node_contents(self):
        """Tests the node contents."""

        # check if all nodes exist
        for node in self.ids:
            self.assertIn(node, list(self.check.keys()))

        # check if point in the node match to what is expected
        for ii, node in enumerate(self.ids):
            self.assertEqual(self.check[node], self.points[ii])
