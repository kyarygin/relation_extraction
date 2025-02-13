import os
import unittest

from ohmygut.core.catalog.catalog import Entity, EntityCollection
from ohmygut.core.catalog.dbpedia_food_catalog import DbpediaFoodCatalog
from ohmygut.core.catalog.usda_food_catalog import FOOD_TAG
from ohmygut.test.helper import test_resource_dir


class TestCase(unittest.TestCase):
    def test_dbpedia_food_catalog(self):
        target = DbpediaFoodCatalog(os.path.join(test_resource_dir, "test_dbpedia_food_data.csv"))
        target.initialize()
        test_sentence = "Acid is whether good or bad"
        expected = EntityCollection([Entity("Acid", "nogroup", FOOD_TAG)], FOOD_TAG)
        actual = target.find(test_sentence)

        self.assertCountEqual(expected.entities, actual.entities)


if __name__ == '__main__':
    unittest.main()
