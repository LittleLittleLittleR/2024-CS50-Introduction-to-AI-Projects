import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


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
        - 0. Administrative, an integer
        - 1. Administrative_Duration, a floating point number
        - 2. Informational, an integer
        - 3. Informational_Duration, a floating point number
        - 4. ProductRelated, an integer
        - 5. ProductRelated_Duration, a floating point number
        - 6. BounceRates, a floating point number
        - 7. ExitRates, a floating point number
        - 8. PageValues, a floating point number
        - 9. SpecialDay, a floating point number
        - 10. Month, an index from 0 (January) to 11 (December)
        - 11. OperatingSystems, an integer
        - 12. Browser, an integer
        - 13. Region, an integer
        - 14. TrafficType, an integer
        - 15. VisitorType, an integer 0 (not returning) or 1 (returning)
        - 16. Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    months = {"Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5,
              "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11}

    l1 = open(filename).readlines()
    evidences = []
    labels = []

    for row in l1[1:]:
        row = row.strip().split(",")
        templst = []
        templst.append(int(row[0]))
        templst.append(float(row[1]))
        templst.append(int(row[2]))
        templst.append(float(row[3]))
        templst.append(int(row[4]))
        templst.append(float(row[5]))
        templst.append(float(row[6]))
        templst.append(float(row[7]))
        templst.append(float(row[8]))
        templst.append(float(row[9]))
        templst.append(months[row[10]])
        templst.append(int(row[11]))
        templst.append(int(row[12]))
        templst.append(int(row[13]))
        templst.append(int(row[14]))
        if row[15] == "Returning_Visitor":
            templst.append(1)
        else:
            templst.append(0)
        if row[16] == "TRUE":
            templst.append(1)
        else:
            templst.append(0)

        evidences.append(templst)

        if row[17] == "TRUE":
            labels.append(1)
        else:
            labels.append(0)

    output = (evidences, labels)
    return output


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    sens = 0
    spec = 0
    positive = 0
    negative = 0

    for i in range(len(labels)):
        if labels[i] == 1:
            positive += 1
            if labels[i] == predictions[i]:
                sens += 1
        else:
            negative += 1
            if labels[i] == predictions[i]:
                spec += 1

    return sens/positive, spec/negative


if __name__ == "__main__":
    main()
