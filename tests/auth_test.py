import unittest
from vk_api import vkauth


class AuthTest(unittest.TestCase):
    def setUp(self) -> None:
        auth = vkauth.VkAuth
        auth.auth()
