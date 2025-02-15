from time import time

from ohmygut.core.catalog.catalog import Catalog
from ohmygut.core.catalog.catalog import Entity, EntityCollection
from ohmygut.core.catalog.usda_food_catalog import FOOD_TAG
from ohmygut.core.constants import logger
from ohmygut.core.hash_tree import HashTree


class MixedFoodCatalog(Catalog):
    def get_list(self):
        return self.__food

    def __str__(self):
        return "mixed food catalog"

    def __init__(self, mixed_tidy_food_file_path):
        super().__init__()
        self.mixed_tidy_food_file_path = mixed_tidy_food_file_path
        self.__hash_tree = None
        self.__food = None

    def initialize(self):
        t1 = time()
        logger.info('Creating mixed food catalog...')
        with open(self.mixed_tidy_food_file_path) as file:
            food = file.read().splitlines()

        self.__hash_tree = HashTree(food)
        self.__food = food

        t2 = time()
        logger.info('Done creating mixed food catalog. Total time: %.2f sec.' % (t2 - t1))

    def find(self, sentence_text):
        food_names = self.__hash_tree.search(sentence_text)
        entities = EntityCollection([Entity(name, 'nogroup', FOOD_TAG) for name in food_names], FOOD_TAG)
        return entities
