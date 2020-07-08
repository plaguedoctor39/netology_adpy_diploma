import unittest
from vk_api import vk_search
from db import results


class InputTest(unittest.TestCase):
    def setUp(self) -> None:
        self.searcher = vk_search.VkSearcher()
        self.data = self.searcher.search()
        self.params = [self.searcher.user_info['id'], [11, 0], ['q']]

    def TestInp(self):
        results.post_data(self.params, self.data, self.searcher)
