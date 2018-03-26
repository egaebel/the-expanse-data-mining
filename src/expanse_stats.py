import os
import re

DATA_DIR = "other-data"
ENGLISH_OTHER_COMMON_WORDS = None
ENGLISH_TOP_ONE_HUNDRED_WORDS = None
OTHER_COMMON_WORDS_FILE_NAME = "other_common_words.txt"
MOST_COMMON_ONE_HUNDRED_WORDS_FILE_NAME = "most_common_one_hundred_words.txt"
FILES_DIR = "../the-expanse/"
PUNCTUATION_REGEX = "[,:;.?!\"-]"

def _load_english_most_common_one_hundred_words(n_words=100):
    global ENGLISH_TOP_ONE_HUNDRED_WORDS
    if ENGLISH_TOP_ONE_HUNDRED_WORDS is None:
        with open(os.path.join(DATA_DIR, MOST_COMMON_ONE_HUNDRED_WORDS_FILE_NAME), "r") as one_hundred_file:
            ENGLISH_TOP_ONE_HUNDRED_WORDS = [line.replace("\n", "").lower() for line in one_hundred_file]
        print("Loaded top %d words: %s\n\n"
            % (n_words, "\n".join(ENGLISH_TOP_ONE_HUNDRED_WORDS[:n_words])))
    return ENGLISH_TOP_ONE_HUNDRED_WORDS[:n_words]

def _load_english_other_common_words_to_ignore():
    global ENGLISH_OTHER_COMMON_WORDS
    if ENGLISH_OTHER_COMMON_WORDS is None:
        with open(os.path.join(DATA_DIR, OTHER_COMMON_WORDS_FILE_NAME), "r") as other_file:
            ENGLISH_OTHER_COMMON_WORDS = [line.replace("\n", "").lower() for line in other_file]
        print("Loaded other common words: %s\n\n" % "\n".join(ENGLISH_OTHER_COMMON_WORDS))
    return ENGLISH_OTHER_COMMON_WORDS

def average_sentence_lengths():
    book_to_average_sentence_length = dict()
    num_sentences = float(0)
    total_length = float(0)
    average_sentence_length = float(0)
    for txt_file_name in os.listdir(FILES_DIR):
        # Ignore hidden files
        if txt_file_name[0] == '.':
            continue
        # Ignore files that don't have the epub extension
        if os.path.splitext(txt_file_name)[1] != ".txt":
            continue
        with open(os.path.join(FILES_DIR, txt_file_name), "r") as txt_file:
            full_book = txt_file.read()
            sentences = full_book.split(".")
            book_num_sentences = len(sentences)
            book_total_length = len(full_book)
            book_average_sentence_length = float(book_total_length) / book_num_sentences
            book_to_average_sentence_length[txt_file_name] = book_average_sentence_length

            num_sentences += book_num_sentences
            total_length += book_total_length
    average_sentence_length = total_length / num_sentences
    print("Average Sentence Lengths:")
    for book_file_name in sorted(book_to_average_sentence_length.keys()):
        book_average_sentence_length = book_to_average_sentence_length[book_file_name]
        print("%s has average sentence length of: %f"
            % (book_file_name, book_average_sentence_length))
    print("Across all books there is an average sentence length of: %f" % average_sentence_length)

    return average_sentence_length, book_to_average_sentence_length

def get_words_to_counts(txt_file_name, files_dir=FILES_DIR):
    with open(os.path.join(files_dir, txt_file_name), "r") as txt_file:
        full_book = txt_file.read()
        full_book
        full_book_no_punctuation = re.sub(PUNCTUATION_REGEX, "", full_book).replace("\u201c", "").replace("\u2013", "")
        full_book_words = full_book_no_punctuation.split(" ")
        words_to_counts = dict()
        for word in full_book_words:
            if word == "":
                continue
            word = word.lower()
            word_count = words_to_counts.get(word, 0)
            words_to_counts[word] = word_count + 1
    return words_to_counts

def _remove_words(words_to_counts, words_to_remove):
    for word in words_to_remove:
        removed_word = words_to_counts.pop(word, None)
    return words_to_counts

def remove_other_common_english_words(words_to_counts):
    other_words = _load_english_other_common_words_to_ignore()
    return _remove_words(words_to_counts, other_words)

def remove_top_n_english_words(words_to_counts, n_words=100):
    assert n_words > 0 and n_words <= 100
    top_words = _load_english_most_common_one_hundred_words(n_words)
    return _remove_words(words_to_counts, top_words)

def get_top_n_words(n_words=20):
    books_to_words_to_counts = dict()
    for txt_file_name in os.listdir(FILES_DIR):
        # Ignore hidden files
        if txt_file_name[0] == '.':
            continue
        # Ignore files that don't have the epub extension
        if os.path.splitext(txt_file_name)[1] != ".txt":
            continue
        book_words_to_counts = get_words_to_counts(txt_file_name)
        books_to_words_to_counts[txt_file_name] = book_words_to_counts

    for book_name in sorted(books_to_words_to_counts.keys()):
        words_to_counts = books_to_words_to_counts[book_name]
        words_to_counts = remove_top_n_english_words(words_to_counts)
        words_to_counts = remove_other_common_english_words(words_to_counts)
        sorted_items = sorted(
            words_to_counts.items(), key=lambda x: x[1], reverse=True)
        print("Book %s top %d words:\n%s"
            % (book_name, n_words, "\n".join(
                map(
                    lambda x: str("%s: %s" % (x[0], x[1])), 
                    sorted_items[:n_words]))))
        print("=========================================================\n\n\n")


if __name__ == '__main__':
    get_top_n_words(50)