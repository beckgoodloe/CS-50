import nltk
import sys
import os
import string
import math

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from operator import itemgetter

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename], False)
        for filename in files
    }
    file_idfs = compute_idfs(file_words)
    while(True):
        # Prompt user for query
        query = set(tokenize(input("Query: "), False))

        # Determine top file matches according to TF-IDF
        filenames = top_files(
            query, file_words, file_idfs, n=FILE_MATCHES)

        # Extract sentences from top files
        sentences = dict()
        for filename in filenames:
            for passage in files[filename].split("\n"):
                for sentence in nltk.sent_tokenize(passage):
                    tokens = tokenize(sentence, False)
                    if tokens:
                        sentences[sentence] = tokens

        # Compute IDF values across sentences
        idfs = compute_idfs(sentences)

        # Determine top sentence matches
        matches = top_sentences(
            query, sentences, idfs, n=SENTENCE_MATCHES)
        for match in matches:
            print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    data = dict()
    for file in os.listdir(directory):
        with open(os.path.join(directory, file)) as f:
            data[file] = f.read()
    return data


def tokenize(document, disp):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    data = word_tokenize(document)
    if(disp):
        print(data)
    final_set = []
    for word in data:
        word = word.lower()
        if(word not in string.punctuation and word not
           in nltk.corpus.stopwords.words("english")):
            final_set.append(word)
    return final_set


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # get a set of all of the words
    all_words = set()
    for file in documents.keys():
        all_words.update(documents[file])

    # calulate idfs
    idfs = dict()
    for word in all_words:
        f = sum(word in documents[filename]
                for filename in documents.keys())
        idf = math.log(len(documents.keys()) / f)
        idfs[word] = idf
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    id_sums = []
    for file in files.keys():
        sum = 0
        for word in query:
            if(word in files[file]):
                sum += idfs[word] * files[file].count(word)
        id_sums.append((file, sum))
    id_sums = sorted(id_sums, key=itemgetter(1), reverse=True)

    top_n = []
    for i in range(0, n):
        name, idf = id_sums[i]
        top_n.append(name)
    return top_n


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    unsorted_dict = []
    for sentence in sentences.keys():
        sum = 0
        words_in = 0
        for word in query:
            if(word in sentences[sentence]):
                sum += idfs[word]
                words_in += sentences[sentence].count(word)
        unsorted_dict.append(
            (sentence, sum, words_in/len(sentences[sentence])))
    sorted_dict = sorted(
        unsorted_dict, key=itemgetter(1, 2), reverse=True)

    top_n = []
    for i in range(0, n):
        sentence, sum, density = sorted_dict[i]
        top_n.append(sentence)
    return top_n


if __name__ == "__main__":
    main()
