import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import GaussianNB

TEST_SIZE = 0.4
MONTHS = {"Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5, "Jul": 6,
          "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11}


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        0- Administrative, an integer
        1- Administrative_Duration, a floating point number
        2- Informational, an integer
        3- Informational_Duration, a floating point number
        4- ProductRelated, an integer
        5- ProductRelated_Duration, a floating point number
        6- BounceRates, a floating point number
        7- ExitRates, a floating point number
        8- PageValues, a floating point number
        9- SpecialDay, a floating point number
        10- Month, an index from 0 (January) to 11 (December)
        11- OperatingSystems, an integer
        12- Browser, an integer
        13- Region, an integer
        14- TrafficType, an integer
        15- VisitorType, an integer 0 (not returning) or 1 (returning)
        16- Weekend, an integer 0 (if false) or 1 (if true)
        17- Label

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    with open("shopping.csv") as f:
        reader = csv.reader(f)
        next(reader)

        evidence = []
        label = []
        for row in reader:
            this_evidence = []
            for i in range(0, len(row)):
                # LABELS
                if(i == 17):
                    if(row[i] == "FALSE"):
                        label.append(0)
                    else:
                        label.append(1)
                # INTEGERS
                elif(i == 0 or i == 2 or i == 4 or 10 < i < 17):
                    if(i == 15):
                        if(row[i] == "Returning_Visitor"):
                            this_evidence.append(1)
                        else:
                            this_evidence.append(0)
                    elif(i == 16):
                        if(row[i] == "False"):
                            this_evidence.append(0)
                        else:
                            this_evidence.append(1)
                    else:
                        this_evidence.append(int(row[i]))

                # MONTH
                elif i == 10:
                    this_evidence.append(MONTHS[row[i]])
                    # Float
                else:
                    this_evidence.append(float(row[i]))
            evidence.append(this_evidence)

        return (evidence, label)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # model = Perceptron()
    # model = KNeighborsClassifier(n_neighbors=1)
    model = GaussianNB()
    return model.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_positive = 0
    total_positive = 0
    true_negative = 0
    total_negative = 0
    for i in range(0, len(labels)):
        if(labels[i] == 1):
            total_positive += 1
            if(predictions[i] == 1):
                true_positive += 1
        else:
            total_negative += 1
            if(predictions[i] == 0):
                true_negative += 1

    sensitivity = float(true_positive) / float(total_positive)
    specificity = float(true_negative) / float(total_negative)

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
