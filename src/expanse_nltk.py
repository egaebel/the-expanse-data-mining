from functools import reduce
import os
import nltk
import re

DEBUG_COUNTER = 0

FILES_DIR = "../the-expanse/"

def extract_and_count_all_entities():
    # Ignore hidden files and files that aren't .txt files
    sorted_valid_file_names = list(filter(
        lambda x: x.find(".txt") != -1 and x.find(".") != 0,
        sorted(os.listdir(FILES_DIR))))
    books_to_entities_to_counts = dict()
    print("Processing entities for files: %s" % "\n".join(sorted_valid_file_names))
    for txt_file_name in sorted_valid_file_names:
        print("Processing file name: %s" % txt_file_name)
        with open(os.path.join(FILES_DIR, txt_file_name), "r") as txt_file:
            full_book = txt_file.read()
            full_book = full_book.replace("_", "")
            sentences = full_book.split(".")
            print("Extracting named entities from %d sentences." % len(sentences))
            sentence_tree_tuples = list(map(
                lambda x: 
                    (x, nltk.ne_chunk(
                        nltk.pos_tag(
                            nltk.tokenize.word_tokenize(x)))), 
                sentences))
            print("Extracted entities!")
            
            print("Aggregating entities across sentences.")
            entities_to_counts = dict()
            for sentence_tree_tuple in sentence_tree_tuples:
                sentence = sentence_tree_tuple[0]
                tree = sentence_tree_tuple[1]
                for subtree in tree.subtrees():
                    if subtree.label().lower() == "s":
                        continue
                    entity_label = subtree.label().lower()
                    words = reduce(
                        lambda x, y: x[0].lower() + " " + y[0].lower(),
                        subtree)\
                        if len(subtree) > 1\
                        else subtree[0][0].lower()
                    poss = reduce(
                        lambda x, y: x[1].lower() + "-" + y[1].lower(),
                        subtree)\
                        if len(subtree) > 1\
                        else subtree[0][1].lower()
                    # entity_id = word + "-" + pos + "-" + entity_label
                    entity_id = str(words) + "--" + str(poss)
                    entity_count = entities_to_counts.get(entity_id, 0)
                    entities_to_counts[entity_id] = entity_count + 1
            print("Aggregated entities!")

            books_to_entities_to_counts[txt_file_name] = entities_to_counts

    print("Processed all entities.")

    print("Outputting entities for files: %s" % "\n".join(sorted_valid_file_names))
    for txt_file_name in sorted_valid_file_names:
        entities_to_counts = books_to_entities_to_counts[txt_file_name]
        sorted_entities_to_counts = sorted(
            entities_to_counts.items(), key=lambda x: x[1], reverse=True)
        print("Top Entities for %s:" % txt_file_name)
        print("\n".join(map(lambda x: "%s: %s" % (x[0], x[1]), sorted_entities_to_counts)))
        print("Total of %d unique entities" % len(sorted_entities_to_counts))
        print("===============================================================\n\n")

    return books_to_entities_to_counts

def extract_all_entity_relations():
    IN = re.compile(r'.*\bin\b(?!\b.+ing)')
    # Ignore hidden files and files that aren't .txt files
    sorted_valid_file_names = list(filter(
        lambda x: x.find(".txt") != -1 and x.find(".") != 0,
        sorted(os.listdir(FILES_DIR))))[:1]
    books_to_entities_to_counts = dict()
    print("Processing entities for files: %s" % "\n".join(sorted_valid_file_names))
    for txt_file_name in sorted_valid_file_names:
        print("Processing file name: %s" % txt_file_name)
        with open(os.path.join(FILES_DIR, txt_file_name), "r") as txt_file:
            full_book = txt_file.read()
            full_book = full_book.replace("_", "")
            sentences = full_book.split(".")[:500]
            print("Extracting named entity relations from %d sentences."
                % len(sentences))
            sentence_tree_tuples = list(map(
                lambda x: 
                    (x, nltk.sem.relextract.extract_rels(
                        "PERSON",
                        "LOCATION",
                        nltk.ne_chunk(
                            nltk.pos_tag(
                                nltk.tokenize.word_tokenize(x))),
                        pattern=IN)), 
                sentences))
            print("Extracted entity relations!")
            print("sentence_tree_tuples: %s" % str([x[1] for x in sentence_tree_tuples]))
        """
        print("Aggregating entities across sentences.")
        entities_to_counts = dict()
        for sentence_tree_tuple in sentence_tree_tuples:
            sentence = sentence_tree_tuple[0]
            tree = sentence_tree_tuple[1]
            for subtree in tree.subtrees():
                if subtree.label().lower() == "s":
                    continue
        """

if __name__ == '__main__':
    extract_all_entity_relations()