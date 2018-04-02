import os
from mitie import *

FILES_DIR = "../the-expanse/"
CHAPTER_FILES_DIR = os.path.join(FILES_DIR, "chapters")

ner = named_entity_extractor('../MITIE/MITIE-models/english/ner_model.dat')
rel_detector = binary_relation_detector("../MITIE/MITIE-models/english/binary_relations/rel_classifier_people.person.place_of_birth.svm")

def extract_and_count_all_entities(dir=FILES_DIR):
    # Ignore hidden files and files that aren't .txt files
    sorted_valid_file_names = list(filter(
        lambda x: x.find(".txt") != -1 and x.find(".") != 0,
        sorted(os.listdir(dir))))
    books_to_entities_to_counts = dict()
    print("Processing entities for files: %s" % "\n".join(sorted_valid_file_names))
    for txt_file_name in sorted_valid_file_names:
        print("Processing file name: %s" % txt_file_name)
        with open(os.path.join(dir, txt_file_name), "r") as txt_file:
            full_book = txt_file.read()
            full_book = full_book.replace("_", "")
            sentences = full_book.split(".")
            print("Extracting entities...")
            sentence_entity_tuples = list(
                map(
                    lambda x: 
                        (x, tokenize(x), ner.extract_entities(tokenize(x))), 
                    sentences))
            print("Extracted entities!")

            print("Pulling out entities from sentences and aggregating...")
            entities_to_counts = dict()
            for sentence_entity_tuple in sentence_entity_tuples:
                sentence = sentence_entity_tuple[0]
                tokenized_sentence = sentence_entity_tuple[1]
                entities = sentence_entity_tuple[2]
                for entity in entities:
                    start = int(entity[0][0])
                    end = int(entity[0][0] + len(entity[0]))
                    entity_text = tokenized_sentence[start:end]
                    entity_type = entity[1]
                    entity_score = entity[2]
                    entity_id = str(entity_text) + "--" + str(entity_type)
                    entity_count = entities_to_counts.get(entity_id, 0)
                    entities_to_counts[entity_id] = entity_count + 1
            books_to_entities_to_counts[txt_file_name] = entities_to_counts


            print("Pulled out entities from sentences and aggregated!")
            entities_to_counts = dict()
    print("Processed all files!")

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
            for sentence in sentences:
                sentence_token = tokenize(sentence)
                entities = ner.extract_entities(sentence_token)
                neighboring_entities = [(entities[i][0], entities[i + 1][0]) for i in xrange(len(entities) - 1)]
                neighboring_entities += [(r,l) for (l,r) in neighboring_entities]
                for person, place in neighboring_entities:
                    rel = ner.extract_binary_relation(sentence_tokens, person, place)

if __name__ == '__main__':
    extract_and_count_all_entities(dir=CHAPTER_FILES_DIR)