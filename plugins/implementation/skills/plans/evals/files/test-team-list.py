import unittest

from app.teams import team_list_path


class TeamListPathTests(unittest.TestCase):
    def test_keeps_active_query(self):
        self.assertEqual(
            team_list_path("blue", "owner=alex"),
            "/api/workspaces/blue/teams?owner=alex",
        )
