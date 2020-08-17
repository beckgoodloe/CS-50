import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 1000000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks1 = sample_pagerank(corpus, DAMPING, SAMPLES)

    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks1):
        print(f"  {page}: {ranks1[page]:.4f}")

    print("")
    ranks2 = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks2):
        print(f"  {page}: {ranks2[page]:.4f}")

    print("")
    ranks3 = {}
    for item in ranks1:
        ranks3[item] = (ranks1[item] - ranks2[item]) * 100
    print(f"PageRank Difference Between Methods")
    for page in sorted(ranks3):
        print(f"  {page}: {ranks3[page]:.4f}")

    print("")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(
                r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # check to make sure page has outgoing links
    if(len(corpus[page]) == 0):
        model = {}
        for item in corpus.keys():
            model[item] = 1 / len(corpus.keys())
        return model

    model = {}
    for item in corpus.keys():
        random_term = (1 - damping_factor) / len(corpus.keys())
        if(item not in corpus[page]):
            model[item] = random_term
        else:
            model[item] = random_term + \
                (damping_factor / len(corpus[page]))
    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page = random.choice(list(corpus.keys()))
    score_keeper = {}
    for i in range(n):
        page = random_by_probability(
            transition_model(corpus, page, damping_factor))
        if(page in score_keeper.keys()):
            score_keeper[page] += 1
        else:
            score_keeper[page] = 1

    # normalize the items in scorekeeper
    for item in score_keeper.keys():
        score_keeper[item] = score_keeper[item] / n

    return score_keeper


def random_by_probability(corpus):
    random_value = random.random()
    sum = 0
    for item in corpus.keys():
        sum += corpus[item]
        if(random_value <= sum):
            return item


def calculate_new_page_rank(corpus, this_page_rank, d):
    new_page_rank = {}
    N = len(corpus.keys())
    for p in corpus.keys():
        sum = (1 - d) / N
        for i in corpus.keys():
            if(not i == p and p in corpus[i]):
                sum += d * this_page_rank[i] / len(corpus[i])
        new_page_rank[p] = sum
    return new_page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    last_page_rank = {}
    for item in corpus.keys():
        last_page_rank[item] = 1 / len(corpus.keys())

    still_iterating = True
    while(still_iterating):
        still_iterating = False
        this_page_rank = calculate_new_page_rank(
            corpus, last_page_rank, damping_factor)
        # check to see if we made a change larger than threshold
        for item in this_page_rank:
            if(this_page_rank[item] - last_page_rank[item] > .001):
                still_iterating = True
        last_page_rank = this_page_rank

    return last_page_rank


if __name__ == "__main__":
    main()
