import argparse
import os

from nltk.parse.stanford import StanfordDependencyParser
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import StanfordTokenizer

from ohmygut.core.analyzer import DoNothingSentenceAnalyzer, SentenceAnalyzer
from ohmygut.core.article.file_article_data_source import NxmlFreeArticleDataSource
from ohmygut.core.article.libgen_txt_article_data_source import LibgenTxtArticleDataSource
from ohmygut.core.article.medline_abstracts_article_data_source import MedlineAbstractsArticleDataSource
from ohmygut.core.catalog.all_bacteria_catalog import AllBacteriaCatalog
from ohmygut.core.catalog.dbpedia_food_catalog import DbpediaFoodCatalog
from ohmygut.core.catalog.diseases_catalog import DiseasesCatalog, DISEASE_TAG
from ohmygut.core.catalog.do_nothing_catalog import DoNothingCatalog
from ohmygut.core.catalog.gut_bacteria_catalog import GutBacteriaCatalog, BACTERIA_TAG
from ohmygut.core.catalog.nutrients_catalog import NutrientsCatalogNikogosov, NUTRIENT_TAG
from ohmygut.core.catalog.usda_food_catalog import UsdaFoodCatalog, FOOD_TAG
from ohmygut.core.main import main
from ohmygut.core.sentence_finder import SentenceFinder
from ohmygut.core.pattern_finder import PatternFinder
from ohmygut.core.sentence_processing import SpacySentenceParser, DoNothingParser
from ohmygut.core.write.csv_writer import CsvWriter, get_csv_path
from ohmygut.core.write.log_writer import LogWriter
from ohmygut.core.write.pkl_writer import PklWriter, get_output_dir_path
from ohmygut.paths import stanford_jar_path, stanford_models_jar_path, stanford_lex_parser_path, food_file_path, \
    gut_catalog_file_path, nutrients_file_path, nxml_articles_dir, abstracts_dir, libgen_texts_dir, \
    verb_ontollogy_path, diseases_csv_path, all_catalog_file_path, dbpedia_food_file_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-dss', action='store', help='number of data sources to skip', default=0)
    parser.add_argument('-ss', action='store', help='number of sentences to skip', default=0)

    args = parser.parse_args()
    data_sources_to_skip_number = int(args.dss)
    sentences_to_skip_number = int(args.ss)

    script_dir = os.path.dirname(os.path.realpath(__file__))

    stanford_tokenizer = StanfordTokenizer(
        path_to_jar=stanford_jar_path
    )

    stanford_dependency_parser = StanfordDependencyParser(
        path_to_jar=stanford_jar_path,
        path_to_models_jar=stanford_models_jar_path,
        model_path=stanford_lex_parser_path,
    )

    all_bacteria_catalog = AllBacteriaCatalog(all_catalog_file_path)
    all_bacteria_catalog.initialize()

    gut_bacteria_catalog = GutBacteriaCatalog(gut_catalog_file_path)
    gut_bacteria_catalog.initialize()

    do_nothing_catalog_food = DoNothingCatalog(FOOD_TAG)
    do_nothing_catalog_disease = DoNothingCatalog(DISEASE_TAG)
    do_nothing_catalog_nutrient = DoNothingCatalog(NUTRIENT_TAG)

    # stanford_sentence_parser = StanfordSentenceParser(stanford_dependency_parser, stanford_tokenizer)
    spacy_sentence_parser = SpacySentenceParser()
    do_nothing_parser = DoNothingParser()

    do_nothing_analyzer = DoNothingSentenceAnalyzer()
    analyzer = SentenceAnalyzer()
    sentence_finder = SentenceFinder([], do_nothing_parser, do_nothing_analyzer, all_bacteria_catalog, [BACTERIA_TAG])

    nxml_article_data_source = NxmlFreeArticleDataSource(articles_folder=nxml_articles_dir)
    medline_article_data_source = MedlineAbstractsArticleDataSource(medline_file=abstracts_dir)
    libgen_article_data_source = LibgenTxtArticleDataSource(libgen_folder=libgen_texts_dir)

    with open(verb_ontollogy_path) as f:
        verb_ontology = eval(''.join(f.readlines()))

    lancaster_stemmer = LancasterStemmer()
    pattern_finder = PatternFinder(verb_ontology, lancaster_stemmer)

    article_data_sources = [nxml_article_data_source, libgen_article_data_source, medline_article_data_source]

    output_dir = get_output_dir_path()
    csv_path = get_csv_path()
    csv_writer = CsvWriter(csv_path)
    pkl_writer = PklWriter(output_dir)
    log_writer = LogWriter()

    main(article_data_sources, writers=[csv_writer, log_writer], sentence_finder=sentence_finder,
         data_sources_to_skip=data_sources_to_skip_number, sentences_to_skip=sentences_to_skip_number)
