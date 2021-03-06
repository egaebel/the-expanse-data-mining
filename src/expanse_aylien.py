from aylienapiclient import textapi
from matplotlib.ticker import FixedLocator, FuncFormatter, MultipleLocator
from time import sleep

import json
import os
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import numpy as np
import re
import sys

AYLIEN_APP_ID = None
AYLIEN_APP_KEY = None
AYLIEN_CACHE = "aylien-cache"
AYLIEN_SENTIMENT_CACHE = os.path.join(AYLIEN_CACHE, "sentiment")

FILES_DIR = "../the-expanse/"
FILE_PREFIX = "the-expanse-"
CHAPTER_FILES_DIR = os.path.join(FILES_DIR, "chapters")

CHAPTER_BOUNDARY_INDICATOR = 1.25897

ERROR_THRESHOLD = 50
RATE_LIMIT_PER_MINUTE = 120
RATE_LIMIT_PER_DAY = 3100

class AylienCachingClient():
    def __init__(self, aylien_client):
        self.aylien_client = aylien_client
        self.calls_since_last_sleep = 0
        self.calls_since_instantiation = 0
        self.error_count = 0

    def _create_cache(self, cache_folder):
        try:
            os.mkdir(AYLIEN_CACHE)
        except:
            pass
        try:
            os.mkdir(cache_folder)
        except:
            pass

    def sentiment(self, sentence):
        self._create_cache(AYLIEN_SENTIMENT_CACHE)
        sentence_cache_file_name = str(sentence)\
            .replace(",", "")\
            .replace(";", "")\
            .replace(" ", "-")\
            .replace("/", "--slash--")[:255]
        file_path = os.path.join(
            AYLIEN_SENTIMENT_CACHE, sentence_cache_file_name)
        response = None
        if os.path.exists(file_path):
            with open(file_path, "r") as sentiment_response_file:
                response = json.loads(sentiment_response_file.read())
        else:
            # Rate limiting
            if self.calls_since_instantiation >= RATE_LIMIT_PER_DAY:
                sys.exit()
            if self.calls_since_last_sleep >= RATE_LIMIT_PER_MINUTE:
                print("Sleeping to respect aylien rate limit...")
                sleep(60)
                print("Done sleeping!")
                self.calls_since_last_sleep = 0
            self.calls_since_instantiation += 1
            self.calls_since_last_sleep += 1
            try:
                response = self.aylien_client.Sentiment({'text': sentence})
            except Exception as e:
                self.error_count += 1
                if self.error_count >= ERROR_THRESHOLD:
                    sys.exit()
                response = None
                print("Made request with sentence: %s" % sentence)
                try:
                    print("Exception: %s" % e)
                except Exception as e2:
                    print("Exception while handling exception...")
                    print("Exception: %s" % e2)
            if response is not None:
                with open(file_path, "w") as sentiment_response_file:
                    sentiment_response_file.write(json.dumps(response))

        return response

def extract_sentiment(aylien_caching_client, directory=CHAPTER_FILES_DIR):
    # Ignore hidden files and files that aren't .txt files
    sorted_valid_file_names = list(filter(
        lambda x: x.find(".txt") != -1 and x.find(".") != 0,
        sorted(os.listdir(directory))))
    books_to_chapters_to_sentiments = dict()
    chapters_to_sentence_sentiment_tuples = dict()
    book_name = None
    print("Processing sentiment for files: %s" % "\n".join(sorted_valid_file_names))
    for txt_file_name in sorted_valid_file_names:
        double_dash_index = txt_file_name.find("--")
        book_name = txt_file_name[:double_dash_index]
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
                sentence = sentence.strip()
                if not sentence:
                    continue
                sentiment = aylien_caching_client.sentiment(sentence)
                # print("Sentence sentiment tuple: %s" % str((sentence, sentiment)))
                if sentiment is not None:
                    sentence_sentiment_tuples.append((sentence, sentiment))
        chapters_to_sentence_sentiment_tuples[txt_file_name] = sentence_sentiment_tuples
        books_to_chapters_to_sentiments[book_name] = chapters_to_sentence_sentiment_tuples

    print("Printing sentences from chapters from books with sentiment...")
    for book in sorted(books_to_chapters_to_sentiments.keys()):
        print("Book: %s" % book)
        chapters_to_sentence_sentiment_tuples = books_to_chapters_to_sentiments[book]
        all_book_sentiments = list()
        for chapter in sorted(chapters_to_sentence_sentiment_tuples.keys()):
            sentence_sentiment_tuples = chapters_to_sentence_sentiment_tuples[chapter]
            print("Chapter: %s" % chapter)
            print("%d sentences in the chapter." % len(sentence_sentiment_tuples))
            """
            for sentence_sentiment_tuple in sentence_sentiment_tuples:
                
                print("Sentence: %s Sentiment: %s"
                    % (sentence_sentiment_tuple[0], 
                        str(sentence_sentiment_tuple[1])))
            """
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
            chapter_boundary_list = [CHAPTER_BOUNDARY_INDICATOR, -CHAPTER_BOUNDARY_INDICATOR]
            all_book_sentiments += chapter_boundary_list
            all_book_sentiments += sentiment_outputs

            ind = np.arange(len(sentence_sentiment_tuples))
        print("Sentiment for %d sentences in the whole book." % len(all_book_sentiments))
        ind = np.arange(len(all_book_sentiments))
        default_width = 1
        widths = list(map(
            lambda weighted_sentiment: 
                2 * default_width 
                if abs(weighted_sentiment) == CHAPTER_BOUNDARY_INDICATOR
                else default_width,
            all_book_sentiments))
        def sentiment_to_color(weighted_sentiment):
            if weighted_sentiment == CHAPTER_BOUNDARY_INDICATOR\
                    or weighted_sentiment == -CHAPTER_BOUNDARY_INDICATOR:
                return "k"
            elif weighted_sentiment > 0:
                return "g"
            elif weighted_sentiment < 0:
                return "r"
            else:
                return "y"
        colors = list(map(
            sentiment_to_color,
            all_book_sentiments))
        fig, ax = plt.subplots()
        print("Widths: %d" % sum(widths))
        fig.set_figwidth(sum(widths))
        rects1 = ax.bar(ind, all_book_sentiments, width=widths, color=colors)
        ax.set_ylabel("Sentiment + confidence")
        ax.set_title("Sentiment with confidence")
        # ax.set_xticks(ind)
        chapter_boundary_indices = list()
        chapter_boundary_indices_to_chapter_number = dict()
        chapter_number = 1
        for i, weighted_sentiment in zip(
                range(len(all_book_sentiments)), all_book_sentiments):
            if weighted_sentiment == CHAPTER_BOUNDARY_INDICATOR:
                chapter_boundary_indices.append(i)
                chapter_boundary_indices_to_chapter_number[i] = chapter_number
                chapter_number += 1

        ax.xaxis.set_major_locator(FixedLocator(chapter_boundary_indices))
        ax.xaxis.set_major_formatter(
            FuncFormatter(
                lambda chapter_boundary_index, position:
                chapter_boundary_indices_to_chapter_number[chapter_boundary_index]))
        ax.xaxis.set_minor_locator(MultipleLocator(500))
        plt.show()
        # plt.savefig("test.png")
        return


def _load_aylien_credentials():
    global AYLIEN_APP_ID
    global AYLIEN_APP_KEY
    aylien_app_id_text = "AYLIEN_APP_ID ="
    aylien_app_key_text = "AYLIEN_APP_KEY ="
    with open("aylien_credentials.txt", "r") as aylien_cred_file:
        for line in aylien_cred_file:
            print("line: %s" % line)
            if line.find(aylien_app_id_text) != -1:
                AYLIEN_APP_ID = line.replace(aylien_app_id_text, "").strip()
                print("set app id")
            if line.find(aylien_app_key_text) != -1:
                AYLIEN_APP_KEY = line.replace(aylien_app_key_text, "").strip()
                print("set app key")

def _get_aylien_client(
        aylien_app_id=AYLIEN_APP_ID, aylien_app_key=AYLIEN_APP_KEY):
    print("aylien_app_id: %s" % aylien_app_id)
    print("aylien_app_key: %s" % aylien_app_key)
    return textapi.Client(aylien_app_id, aylien_app_key)

if __name__ == '__main__':
    _load_aylien_credentials()
    extract_sentiment(AylienCachingClient(_get_aylien_client(AYLIEN_APP_ID, AYLIEN_APP_KEY)))
