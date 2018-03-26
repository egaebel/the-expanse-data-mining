import os
import nltk

FILES_DIR = "../the-expanse/"

# Ignore hidden files and files that aren't .txt files
sorted_valid_file_names = filter(
    lambda x: x.find(".txt") != -1 and x.find(".") != 0,
    sorted(os.listdir(FILES_DIR)))
books_to_entities_to_counts = dict()
for txt_file_name in sorted_valid_file_names:
    with open(os.path.join(FILES_DIR, txt_file_name), "r") as txt_file:
        full_book = txt_file.read()
        sentences = full_book.split(".")
        sentence_tree = list(map(
            lambda x: 
                (x, nltk.ne_chunk(
                    nltk.pos_tag(
                        nltk.tokenize.word_tokenize(x)))), 
            sentences))

        entities_to_counts = dict()
        for subtree in sentence_tree.subtrees():
            if subtree.label().lower() == "s":
                continue
            entity_label = subtree.label().lower()
            word = subtree[0][0]
            pos = subtree[0][1]
            entity_id = word + "-" + pos + "-" + entity_label
            entity_count = entities_to_counts.get(entity_id, 0)
            entities_to_counts[entity_id] = entity_count + 1

        books_to_entities_to_counts[txt_file_name] = entities_to_counts

for txt_file_name in sorted_valid_file_names:
    entities_to_counts = books_to_entities_to_counts[txt_file_name]
    sorted_entities_to_counts = sorted(
        entities_to_counts.items(), key=lambda x: x[1], reverse=True)
    print("Top Entities for %s:" % txt_file_name)
    print("\n".join(map(lambda x: "%s: %s" % (x[0], x[1]), sorted_entities_to_counts)))
    print("Total of %d unique entities" % len(sorted_entities_to_counts))
    print("===============================================================\n\n")
