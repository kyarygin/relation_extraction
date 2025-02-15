import unittest
from unittest.mock import MagicMock

from ohmygut.core.analyzer import SentenceAnalyzer
from ohmygut.core.article.article import Article
from ohmygut.core.catalog.all_bacteria_catalog import ALL_BACTERIA_TAG
from ohmygut.core.catalog.catalog import Catalog, EntityCollection, Entity
from ohmygut.core.catalog.diseases_catalog import DISEASE_TAG
from ohmygut.core.catalog.gut_bacteria_catalog import BACTERIA_TAG
from ohmygut.core.catalog.nutrients_catalog import NUTRIENT_TAG
from ohmygut.core.catalog.usda_food_catalog import FOOD_TAG
from ohmygut.core.sentence_finder import SentenceFinder
from ohmygut.core.sentence_processing import SentenceParser, SpacySentenceParser


class MockSentenceParser(SentenceParser):
    def parse_sentence(self, sentence, entities, tokens):
        pass


class MockCatalog(Catalog):
    def __init__(self, name, entities_number, additional_tags=None):
        super().__init__()
        if additional_tags is None:
            additional_tags = []
        self.additional_tags = additional_tags
        self.entities_number = entities_number
        self.name = name

    def initialize(self):
        pass

    def find(self, sentence_text):
        pass

    def get_list(self):
        pass


class TestCase(unittest.TestCase):
    def test_if_tags(self):
        target = SentenceFinder(catalog_list=None, sentence_parser=None, sentence_analyzer=None,
                                tags_to_search=[BACTERIA_TAG],
                                tags_optional_to_search=[FOOD_TAG, DISEASE_TAG, NUTRIENT_TAG])
        self.assertTrue(target.check_if_tags([BACTERIA_TAG, FOOD_TAG]))
        self.assertTrue(target.check_if_tags([BACTERIA_TAG, DISEASE_TAG]))
        self.assertTrue(target.check_if_tags([BACTERIA_TAG, NUTRIENT_TAG]))
        self.assertFalse(target.check_if_tags([BACTERIA_TAG, ALL_BACTERIA_TAG]))
        self.assertFalse(target.check_if_tags([BACTERIA_TAG]))

        target = SentenceFinder(catalog_list=[], sentence_parser=None, sentence_analyzer=None,
                                tags_to_search=[BACTERIA_TAG], tags_optional_to_search=[])
        self.assertTrue(target.check_if_tags([BACTERIA_TAG, FOOD_TAG]))
        self.assertTrue(target.check_if_tags([BACTERIA_TAG, DISEASE_TAG]))
        self.assertTrue(target.check_if_tags([BACTERIA_TAG, NUTRIENT_TAG]))
        self.assertTrue(target.check_if_tags([BACTERIA_TAG, ALL_BACTERIA_TAG]))
        self.assertTrue(target.check_if_tags([BACTERIA_TAG]))
        self.assertFalse(target.check_if_tags([FOOD_TAG, DISEASE_TAG]))

    def test_get_sentence1(self):
        catalog1 = MockCatalog(1, 2)
        catalog1.find = MagicMock(return_value=EntityCollection([Entity("name01", "code01", "tag1"),
                                                                 Entity("name11", "code11", "tag1")], "tag1"))
        catalog2 = MockCatalog(2, 1)
        catalog2.find = MagicMock(return_value=EntityCollection([Entity("name02", "code02", "tag2")], "tag2"))
        catalog3 = MockCatalog(3, 1)
        catalog3.find = MagicMock(return_value=EntityCollection([Entity("name03", "code03", "tag3")], "tag3"))
        catalog4 = MockCatalog(4, 1, ["tag4add"])
        catalog4.find = MagicMock(return_value=EntityCollection([Entity("name04", "code04", "tag4", ["tag4add"])], "tag4"))
        analyzer = SentenceAnalyzer()
        target = SentenceFinder(catalog_list=[catalog1, catalog2, catalog3, catalog4],
                                sentence_parser=SpacySentenceParser(),
                                sentence_analyzer=analyzer, tags_to_search=["tag1"],
                                tags_optional_to_search=["tag2"], tags_to_exclude=["tag3", "tag4add"])
        text = "The name01 is the same as name11, but not name02, and name03 and name04 as well"
        title = "title"
        journal = "journal"
        actual = target.get_sentence(text, Article(title, "a text", journal, "123"))
        actual_collections = actual.entities_collections
        expected_collections = [EntityCollection([Entity("name01", "code01", "tag1"),
                                                  Entity("name11", "code11", "tag1")], "tag1"),
                                EntityCollection([Entity("name02", "code02", "tag2")], "tag2")]
        self.assertCountEqual(actual_collections, expected_collections)

    def test_get_sentence2(self):
        catalog1 = MockCatalog(1, 2)
        catalog1.find = MagicMock(return_value=EntityCollection([Entity("name01w1", "code01", "tag1"),
                                                                 Entity("name01w1 name01w2", "code11", "tag1", ["tag4add"])], "tag1"))
        catalog2 = MockCatalog(2, 1)
        catalog2.find = MagicMock(return_value=EntityCollection([Entity("name02", "code02", "tag2")], "tag2"))
        catalog3 = MockCatalog(3, 1)
        catalog3.find = MagicMock(return_value=EntityCollection([Entity("name03", "code03", "tag3")], "tag3"))
        catalog4 = MockCatalog(4, 1, ["tag4add"])
        catalog4.find = MagicMock(return_value=EntityCollection([Entity("name04", "code04", "tag4", ["tag4add"])], "tag4"))

        analyzer = SentenceAnalyzer()

        target = SentenceFinder(catalog_list=[catalog1, catalog2, catalog3, catalog4],
                                sentence_parser=SpacySentenceParser(),
                                sentence_analyzer=analyzer, tags_to_search=["tag2"],
                                tags_optional_to_search=["tag1", "tag3"], tags_to_exclude=["tag4add"])
        text = "The name01w1 name01w2 is the same as name11, but not name02, and name03 and name04 as well"
        title = "title"
        journal = "journal"
        actual = target.get_sentence(text, Article(title, "a text", journal, "123"))
        actual_collections = actual.entities_collections
        expected_collections = [EntityCollection([Entity("name02", "code02", "tag2")], "tag2"),
                                EntityCollection([Entity("name03", "code03", "tag3")], "tag3")]
        self.assertCountEqual(actual_collections, expected_collections)

    def test_get_sentence3(self):
        catalog1 = MockCatalog(1, 2)
        catalog1.find = MagicMock(return_value=EntityCollection([Entity("name01w1", "code01", "tag1"),
                                                                 Entity("name01w1 name01w2", "code11", "tag1", ["tag4add"])], "tag1"))
        catalog2 = MockCatalog(2, 1)
        catalog2.find = MagicMock(return_value=EntityCollection([Entity("name02", "code02", "tag2")], "tag2"))
        catalog3 = MockCatalog(3, 1)
        catalog3.find = MagicMock(return_value=EntityCollection([Entity("name03", "code03", "tag3")], "tag3"))
        catalog4 = MockCatalog(4, 1, ["tag4add"])
        catalog4.find = MagicMock(return_value=EntityCollection([Entity("name04", "code04", "tag4", ["tag4add"])], "tag4"))

        analyzer = SentenceAnalyzer()
        # case 2
        target = SentenceFinder(catalog_list=[catalog1, catalog2, catalog3, catalog4],
                                sentence_parser=SpacySentenceParser(),
                                sentence_analyzer=analyzer, tags_to_search=["tag2"],
                                tags_optional_to_search=["tag1"], tags_to_exclude=["tag3", "tag4add"])
        text = "The name01w1 name01w2 is the same as name11, but not name02, and name03 and name04 as well"
        title = "title"
        journal = "journal"
        actual = target.get_sentence(text, Article(title, "a text", journal, "123"))
        expected = None
        self.assertEqual(actual, expected)

    def test_get_sentence_same_coordinates(self):
        catalog1 = MockCatalog(1, 2)
        catalog1.find = MagicMock(return_value=EntityCollection([Entity("name01w1 name01w2", "code01", "tag1"),
                                                                 Entity("name01w1 name01w2", "code11", "tag1", ["tag4add"])], "tag1"))
        catalog2 = MockCatalog(2, 1)
        catalog2.find = MagicMock(return_value=EntityCollection([Entity("name02", "code02", "tag2")], "tag2"))
        catalog3 = MockCatalog(3, 1)
        catalog3.find = MagicMock(return_value=EntityCollection([Entity("name03", "code03", "tag3")], "tag3"))
        catalog4 = MockCatalog(4, 1, ["tag4add"])
        catalog4.find = MagicMock(return_value=EntityCollection([Entity("name04", "code04", "tag4", ["tag4add"])], "tag4"))

        analyzer = SentenceAnalyzer()

        target = SentenceFinder(catalog_list=[catalog1, catalog2, catalog3, catalog4],
                                sentence_parser=SpacySentenceParser(),
                                sentence_analyzer=analyzer, tags_to_search=["tag2"],
                                tags_optional_to_search=["tag1", "tag3"], tags_to_exclude=["tag4add"])
        text = "The name01w1 name01w2 is the same as name11, but not name02, and name03 and name04 as well"
        title = "title"
        journal = "journal"
        actual = target.get_sentence(text, Article(title, "a text", journal, "123"))
        actual_collections = actual.entities_collections
        expected_collections = [EntityCollection([Entity("name01w1_name01w2", "code01", "tag1")], "tag1"),
                                EntityCollection([Entity("name02", "code02", "tag2")], "tag2"),
                                EntityCollection([Entity("name03", "code03", "tag3")], "tag3")]
        self.assertCountEqual(actual_collections, expected_collections)

if __name__ == '__main__':
    unittest.main()

