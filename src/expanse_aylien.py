from aylienapiclient import textapi
from time import sleep

import os
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import numpy as np
import re

AYLIEN_APP_ID = "7fe8de1d"
AYLIEN_APP_KEY = "ef49f063d5cb17a97f158e43de5f7747"

FILES_DIR = "../the-expanse/"
FILE_PREFIX = "the-expanse-"
CHAPTER_FILES_DIR = os.path.join(FILES_DIR, "chapters")

def extract_sentiment(directory=CHAPTER_FILES_DIR):
    calls_since_last_sleep = 0

    aylien_client = _get_aylien_client()
    # Ignore hidden files and files that aren't .txt files
    sorted_valid_file_names = list(filter(
        lambda x: x.find(".txt") != -1 and x.find(".") != 0,
        sorted(os.listdir(directory))))
    books_to_chapters_to_sentiments = dict()
    book_name = None
    print("Processing entities for files: %s" % "\n".join(sorted_valid_file_names))
    for txt_file_name in sorted_valid_file_names:
        double_dash_index = txt_file_name.find("--")
        book_name = txt_file_name[:double_dash_index]
        chapters_to_sentence_sentiment_tuples = dict()
        sentence_sentiment_tuples = list()
        print("Processing file name: %s" % txt_file_name)
        with open(os.path.join(directory, txt_file_name), "r") as txt_file:
            full_book = txt_file.read()
            full_book = full_book.replace("_", "")
            full_book = full_book.replace("**", "")
            full_book = full_book.replace("\n", " ")
            full_book = re.sub(" +", " ", full_book)
            sentences = full_book.split(".")
            for sentence in sentences:
                sentiment = None
                try:
                    if calls_since_last_sleep >= RATE_LIMIT_PER_MINUTE:
                        sleep(60)
                        calls_since_last_sleep = 0
                    sentiment = aylien_client.Sentiment({'text': sentence})
                    calls_since_last_sleep += 1
                except Exception as e:
                    print("Made request with sentence: %s" % sentence)
                    try:
                        print("Exception: %s" % e)
                    except Exception as e2:
                        print("Exception while handling exception...")
                        print("Exception: %s" % e2)
                print("Sentence sentiment tuple: %s" % str((sentence, sentiment)))
                if sentiment is not None:
                    sentence_sentiment_tuples.append((sentence, sentiment))
        chapters_to_sentence_sentiment_tuples[txt_file_name] = sentence_sentiment_tuples
    books_to_chapters_to_sentiments[book_name] = chapters_to_sentence_sentiment_tuples

    print("Printing sentences from chapters from books with sentiment...")
    for book in sorted(books_to_chapters_to_sentiments.keys()):
        print("Book: %s" % book)
        chapters_to_sentence_sentiment_tuples = books_to_chapters_to_sentiments[book]
        all_book_sentiments = list()
        for chapter in chapters_to_sentence_sentiment_tuples.keys():
            print("Chapter: %s" % chapter)
            sentence_sentiment_tuples = chapters_to_sentence_sentiment_tuples[chapter]
            for sentence_sentiment_tuple in sentence_sentiment_tuples:
                print("Sentence: %s Sentiment: %s"
                    % (sentence_sentiment_tuple[0], 
                        str(sentence_sentiment_tuple[1])))
            sentiment_to_int = {"positive": 1, "neutral": 0, "negative": -1}
            sentiment_ints = list(map(
                lambda x: sentiment_to_int[x[1]["polarity"]],
                sentence_sentiment_tuples))
            sentiment_confidences = list(map(
                lambda x: x[1]["polarity_confidence"],
                sentence_sentiment_tuples))
            sentiment_outputs = [
                sentiment_confidences[i] * sentiment_ints[i]
                for i in range(len(sentence_sentiment_tuples))]
            all_book_sentiments += sentiment_outputs

            ind = np.arange(len(sentence_sentiment_tuples))
        ind = np.arange(len(all_book_sentiments))
        width = 0.2
        fig, ax = plt.subplots()
        rects1 = ax.bar(ind - width, all_book_sentiments, width)
        ax.set_ylabel("Sentiment + confidence")
        ax.set_title("Sentiment with confidence")
        ax.set_xticks(ind)
        plt.show()
        return



def _get_aylien_client(
        aylien_app_id=AYLIEN_APP_ID, aylien_app_key=AYLIEN_APP_KEY):
    return textapi.Client(aylien_app_id, aylien_app_key)

if __name__ == '__main__':
    extract_sentiment()