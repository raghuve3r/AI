import email
import math
import random
import string


class Result:
    """
    Has the confusion matrix, documents classified correctly and total number of documents tested against.
    Also handles displaying the results on the console.
    """
    def __init__(self, confusion_matrix, correct_classification, total_documents):
        self.confusion_matrix = confusion_matrix
        self.right = correct_classification
        self.total = total_documents

    def __str__(self):

        str_formatter = ["\t"] + self.confusion_matrix.keys()
        str_formatter.append("\n")
        for key in self.confusion_matrix.keys():
            str_formatter.append(key)
            for res in self.confusion_matrix.keys():
                str_formatter.append(str(self.confusion_matrix[key][res]))
                str_formatter.append("\t")
            str_formatter.append("\n")
        str_formatter.append("\nCorrect Classification: %d\n" % self.right)
        str_formatter.append("\nTotal number of documents: %d\n" % self.total)
        str_formatter.append("\nAccuracy: %f\n" % round(((float(self.right) / self.total) * 100), 3))

        return ' '.join(str_formatter)


class Model:
    """
    The model for our topic classification. Holds the word count, topic count, word-topic distribution and doc count.
    """
    def __init__(self, data, topics, word_counter, doc_topic_counter):
        self.data = data
        self.topics = topics
        self.word_count = sum(self.topics.values())
        self.word_counter = word_counter
        self.doc_topic_counter = doc_topic_counter
        self.doc_count = sum(self.doc_topic_counter.values())

    # To ensure our count related properties are not outdated.
    def update_counts(self):
        self.word_count = sum(self.topics.values())
        self.doc_count = sum(self.doc_topic_counter.values())

    # Returns the probability of a word|topic
    def find_prob(self, word, topic):
        # Return a random value if word is unknown.
        if self.is_new_word(word):
            return random.random()
        # A very low value if the word never occurred for a given topic.
        if self.data[topic][word] == 0:
            return 1.0 / self.word_count

        return float(self.data[topic][word]) / self.get_word_count(word)

    # Returns the probability of a topic in our model.
    def find_topic_prob(self, topic):
        return float(self.doc_topic_counter[topic]) / self.doc_count

    def get_word_count(self, word):
        return self.word_counter[word]

    def is_new_word(self, word):
        return self.word_counter[word] == 0

# Stop words to remove during processing the documents.
# Some are taken from the internet and modified to suit our model.
# https://github.com/Alir3z4/python-stop-words

stopWords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'arent', 'as',
             'at', 'because', 'be', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'cant',
             'cannot',
             'couldnt', 'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for',
             'from',
             'further', 'had', 'hadnt', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hell', 'hes', 'her',
             'hers', 'here',
             'heres', 'herself', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id', 'ill', 'im', 'ive', 'if', 'in',
             'into', 'is', 'isnt',
             'it', 'its', 'itself', 'lets', 'more', 'me', 'most', 'mustnt', 'my', 'myself', 'no', 'nor', 'not', 'of',
             'off', 'on', 'once',
             'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shant', 'she',
             'shell', 'shed', 'shes',
             'should', 'shouldnt', 'so', 'some', 'such', 'than', 'that', 'thats', 'the', 'their', 'theirs', 'them',
             'themselves', 'then',
             'there', 'theres', 'they', 'theyd', 'theyll', 'theyre', 'theyve', 'this', 'those', 'though', 'through',
             'to', 'too', 'under',
             'until', 'up', 'very', 'was', 'wasnt', 'we', 'wed', 'well', 'were', 'weve', 'werent', 'what', 'whats',
             'when', 'whens', 'where',
             'wheres', 'which', 'while', 'who', 'whos', 'whom', 'why', 'whys', 'with', 'wont', 'would', 'wouldnt',
             'you', 'youd', 'youll',
             'youre', 'youve', 'your', 'yours', 'yourself', 'yourselves', 'font', 'html', 'table', 'br', 'will',
             'article', 'says', 'can', 'one', 'use', 'writes']


# Returns the topic with the highest probability for the given word. Calculates log addition.
def find_topic(model, words):
    topic_prob = {}
    for cur_topic in model.topics.keys():
        prob = 0.0
        for word in words:
            word_prob = model.find_prob(word, cur_topic)
            prob += math.log(word_prob)

        prob += math.log(model.find_topic_prob(cur_topic))
        topic_prob[cur_topic] = prob

    classified_topic = max(topic_prob, key=topic_prob.get)

    return classified_topic


# Remove punctuation, digits and stop words.
def sanitize_content(content):
    content = content.lower()
    content = content.translate(None, string.punctuation)
    content = content.translate(None, string.digits)
    sanitized_content = [word for word in content.split() if word not in stopWords and len(word) > 2]
    return sanitized_content


# Returns the list of sanitized words from the file.
def get_file_content(file_path):
    f_ptr = open(file_path, "r")
    email_obj = email.message_from_file(f_ptr)
    f_ptr.close()
    content = email_obj.get_payload()
    words = sanitize_content(content)
    return words
