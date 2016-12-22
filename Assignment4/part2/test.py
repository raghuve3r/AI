import os
from collections import Counter, defaultdict

import utils


# Perform testing with the data in the dataset directory using our model.
def test_data(model, dataset_dir):
    confusion_matrix = defaultdict(Counter)
    doc_count = 0
    count_correct_classification = 0
    print("Testing Data...")
    print("Please wait...")
    for topic in os.listdir(dataset_dir):

        if topic.startswith('.'):
            continue
        topic_dir = dataset_dir + "/" + topic

        for test_file in os.listdir(topic_dir):
            doc_count += 1
            file_path = topic_dir + "/" + test_file
            words = utils.get_file_content(file_path)
            # Topic classified using our model.
            classified_topic = utils.find_topic(model, words)

            # Is it the same as our ground truth?
            if classified_topic == topic:
                count_correct_classification += 1

            # Tabulate results into our confusion matrix.
            confusion_matrix[topic][classified_topic] += 1

    # Return the result object.
    return utils.Result(confusion_matrix, count_correct_classification, doc_count)
