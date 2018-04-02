import epub
import functools
import html2text
import os
import re

FILES_DIR = "../the-expanse/"
CHAPTER_FILES_DIR = os.path.join(FILES_DIR, "chapters")
VALID_CHAPTER_FORMATS = [
    "Prologue: .+",
    "Chapter [^ ]+: .+",
    "Interlude: .+",
    "Epilogue: .+"]

class Chapter():
    def __init__(self, book_title, chapter_order, chapter_label, content):
        self.book_title = book_title
        self.chapter_order = chapter_order
        self.chapter_label = chapter_label
        self.content = content

character_to_chapter = dict()

html_to_text = html2text.HTML2Text()
html_to_text.ignore_links = True

expanse_epub_files = sorted(os.listdir(FILES_DIR))
print("Files:\n%s" % "\n".join(expanse_epub_files))
for epub_file_name in expanse_epub_files:
    # Ignore hidden files
    if epub_file_name[0] == '.':
        continue
    # Ignore files that don't have the epub extension
    if os.path.splitext(epub_file_name)[1] != ".epub":
        continue
    # ebook = epub.open_epub("the-expanse/the-expanse-1-leviathan-wakes.epub")
    print("Opening file: %s" % epub_file_name)
    ebook = epub.open_epub(os.path.join(FILES_DIR, epub_file_name))
    book_title = ebook.toc.title
    print("Starting on book: %s" % book_title)

    play_order = [nav_point.play_order for nav_point in ebook.toc.nav_map.nav_point]
    labels = [nav_point.labels[0][0] for nav_point in ebook.toc.nav_map.nav_point]
    source_references = [nav_point.src for nav_point in ebook.toc.nav_map.nav_point]

    chapter_label_source_tuples = list(zip(play_order, labels, source_references))

    """
    print("Full set of references:")
    print(chapter_label_source_tuples)
    """
    print("\n\n")
    print("Content print")
    full_book_content = list()
    for item in chapter_label_source_tuples:
        chapter_order = item[0]
        chapter_title = item[1]
        matches = [
            True if re.fullmatch(valid_format, chapter_title) is not None 
            else False 
            for valid_format in VALID_CHAPTER_FORMATS]
        has_matches = functools.reduce(lambda x, y: x or y, matches)
        if not has_matches:
            print("Skipping chapter: %s, invalid format." % chapter_title)
            continue

        chapter_character = ""

        chapter_info_string = "Book: %s Chapter: %s titled: %s"\
            % (book_title, chapter_order, chapter_title)
        try:
            chapter_content = ebook.read_item(item[2])
            print(chapter_info_string)
        except Exception as e:
            print("Failed getting chapter: %s %s in book %s, exception: %s"
                % (chapter_order, chapter_title, ebook.toc.title, str(e)))
            ref_fixed = re.sub("#.*", "", item[2])
            try:
                chapter_content = ebook.read_item(ref_fixed)
                print("Success on retry! %s" % chapter_info_string)
            except:
                print("FAILED ON RETRY TOO for book titled: %s with ref: %s."
                    % (book_title, ref_fixed))
        chapter_content = html_to_text.handle(str(chapter_content.decode('utf-8')))
        print("Chapter content: %s" % chapter_content)
        full_book_content.append((chapter_order, chapter_title, chapter_content))
    with open(os.path.join(FILES_DIR, epub_file_name.replace(".epub", ".txt")), "w") as txt_file:
        for chapter_tuple in full_book_content:
            order = chapter_tuple[0]
            title = chapter_tuple[1]
            content = chapter_tuple[2]
            txt_file.write(content)

            chapter_file_name = epub_file_name.replace(".epub", "")
            chapter_file_name += "--" + order.zfill(3) + "--" + title
            chapter_file_name += ".txt"
            with open(os.path.join(CHAPTER_FILES_DIR, chapter_file_name), "w") as chapter_txt_file:
                chapter_txt_file.write(content)
    ebook.close()
    print("==========================================================================\n\n\n")
