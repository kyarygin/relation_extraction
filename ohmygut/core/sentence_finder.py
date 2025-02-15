import spacy

from ohmygut.core.constants import SENTENCE_LENGTH_THRESHOLD, logger
from ohmygut.core.sentence import Sentence
from ohmygut.core.tools import remove_entity_overlapping


class SentenceFinder(object):
    def __init__(self, catalog_list, sentence_parser, sentence_analyzer, tags_to_search, tags_optional_to_search,
                 tags_to_exclude=None):
        super().__init__()
        if tags_to_exclude is None:
            tags_to_exclude = []
        self.tags_to_exclude = tags_to_exclude
        self.catalog_list = catalog_list
        self.tags_optional = set(tags_optional_to_search)
        self.tags = set(tags_to_search)
        self.sentence_analyzer = sentence_analyzer
        self.sentence_parser = sentence_parser
        self.nlp = spacy.load('en')

        logger.info(
            "search will start with catalogs: %s\nand tags req: %s\ntags opt: %s\ntags excl: %s" % (catalog_list,
                                                                                                    tags_to_search,
                                                                                                    tags_optional_to_search,
                                                                                                    tags_to_exclude))

    def get_sentence(self, sentence_text, article):
        if not self.check_if_title(article.title):
            return None

        if len(sentence_text) > SENTENCE_LENGTH_THRESHOLD:
            return None

        entities_collections = []
        for catalog in self.catalog_list:
            found_entities = catalog.find(sentence_text)
            entities_collections.append(found_entities)

        tags_in_sentence = set([collection.tag for collection in entities_collections if len(collection.entities) > 0])

        if not self.check_if_tags(tags_in_sentence):
            return None

        tokens = self.nlp(sentence_text)
        tokens_words = [token.orth_ for token in tokens]

        # todo: check - if we found bacteria both in gut_catalog and all_bacteria_catalog - which we would keep?
        logger.info("entities before remove overlapping: %s" % str(entities_collections))
        entities_collections = remove_entity_overlapping(entities_collections, tokens_words)
        logger.info("entities after remove overlapping: %s" % str(entities_collections))

        # separate all several-words-names by underscope (_)
        for collection in entities_collections:
            for entity in collection.entities:
                dashed_name = entity.name.replace(' ', '_')
                sentence_text = sentence_text.replace(entity.name, dashed_name)
                entity.name = dashed_name

        # remove bad entities
        for collection in entities_collections:
            bad_entities = [x for x in collection.entities
                            if any(y in self.tags_to_exclude for y in x.additional_tags) or
                            x.tag in self.tags_to_exclude]
            for entity in bad_entities:
                collection.entities.remove(entity)

        entities_collections = [collection for collection in entities_collections if len(collection.entities) > 0]
        tags_in_sentence = set([collection.tag for collection in entities_collections if len(collection.entities) > 0])

        logger.info("entities after excluding: %s" % str(entities_collections))
        if not self.check_if_tags(tags_in_sentence):
            return None

        tokens = self.nlp(sentence_text)

        # entities list for parser
        all_entities_list = []
        for collection in entities_collections:
            all_entities_list.extend(collection.entities)

        parser_output = self.sentence_parser.parse_sentence(sentence_text, all_entities_list, tokens)

        paths = self.sentence_analyzer.analyze_sentence(parser_output, tags_in_sentence)

        sentence = Sentence(text=sentence_text,
                            article=article,
                            entities_collections=entities_collections,
                            parser_output=parser_output,
                            shortest_paths=paths)

        return sentence

    def check_if_tags(self, tags_in_sentence):
        if not self.tags.issubset(tags_in_sentence):
            return False
        if len(self.tags_optional) != 0 and not any(
                        tag_optional in tags_in_sentence for tag_optional in self.tags_optional):
            return False
        return True

    def check_if_title(self, article_title):
        if "horse" in article_title or \
                        "pig" in article_title or \
                        "livestock" in article_title or \
                        "calve" in article_title or \
                        "cattle" in article_title or \
                        "Horse" in article_title or \
                        "Pig" in article_title or \
                        "Livestock" in article_title or \
                        "Calve" in article_title or \
                        "Cattle" in article_title:
            return False
        return True
