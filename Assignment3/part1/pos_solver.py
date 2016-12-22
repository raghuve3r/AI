###################################
# CS B551 Fall 2016, Assignment #3
#
#
# Anup Bharadwaj
# Supreeth Prakash
# Raghuveer Krishnamurthy
#
# (Based on skeleton code by D. Crandall)
#
#
# Put your report here!!

# The train() method skims through the labelled corpus and creates data structures for:
#   tokTags    - This data structure has the count of a given word for a particular tag.
#   tagTags    - This data structure will have the count for a given tag at position k to tags at position k-1.
#   tagTagTags - This data structure will include the count for a given tag following a combination of previous two tags.
#   iv         - This data structure will have the count of all the pos tags appearing at the start of the sentence.
#
# 1) Formulation and abstraction of Simple algorithm:
#       Since the simple model does not count the dependence on the tags assigned to other words, we can model with a simple assumption that the tag which occurs the most
#       will be the tag assigned to it. In other words, Each word in a sentence is assigned a tag, by taking the most commonly occurring tag for the given word.
#
#    Formulation and abstraction for HMM:
#       With the HMM model of Bayes Net, we now have a transition dependence on the POS tags assigned for each word along with the initial probability vector and emission probabilities.
#       By the definition of HMM, - The data stored in tagTags will aid us in calculating the transition probabilities, the data in tokTags will give us the emission probabilities and the IV is a dictionary
#       separately maintained during training.
#
#    Formulation and abstraction of Complex algorithm:
#       In this model, a tag can be dependent on the tags assigned to words at time t-1 and t-2. In order to accommodate that into our problem, we make use of tagtagtags dictionary counter to aid us in the necessary transition of tags.
#       With this information, we try to assign POS tags for words by maximizing the states based on up to previous two states hoping to get better results.
#
#
# 2) During training, the data is analyzed and the information is represented into 4 different data structures as explained above. This readily gives us the counts of a word with a certain tag, or tag at time t given another tag at time t-1
#    or tag given tags at two steps behind. We used counters instead of dictionaries at some places to get an auto 0 if the key was never been found in the training.
#
#   In the simplified model, we simply pick the tag with the highest count for the given word, calculate the probability and return the list of tags and their probabilities.
#
#   In the HMM model, we first calculate the initial probability using the iv data structure. With the initial probability in our hand we calculate the further probabilities by using Viterbi's algorithm and then return a list of tags and their probabilities.
#
#   In the Complex model, we not only calculate the initial probability but we also find the probability of second word using the information from the initial probability. We then modified the Viterbi's algorithm to accommodate the dependency created by previous two states.
#   The resulting list of tags and their probabilities are then returned. We tried to work on an enhanced viterbi sequence which takes care of the tags at two steps behind in time.
#
# 3) Assumptions and simplifications:
#   Going by intuition, we categorize every unknown word as a noun as they have the highest probability of appearing as unknown words from the training corpus. The word count for calculating emissions is set to 1.
#   To further steer towards proper POS tagging of unknown words, we give relative probabilities of the tags w.r.t to how common they occur in the training.
#   We give a small emission probability of 0.00000001 if the entry doesn't exist.
#   In calculating the posterior probability, we assume the HMM model on all three Bayes Nets. The P(w) on the denominator is ignored to maximize the probability values.
#
#
# 4) Results:
# ==> So far scored 2000 sentences with 29442 words.
#                    Words correct:     Sentences correct:
#    0. Ground truth:      100.00%              100.00%
#      1. Simplified:       93.92%               47.45%
#             2. HMM:       94.25%               49.35%
#         3. Complex:       94.08%               48.00%
####



import math
from collections import Counter
from collections import defaultdict


# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
def find_log_prob(count, total):
    return math.log(float(count) / total)


def find_prob(a, b):
    return float(a) / b


class Solver:
    tokTags = defaultdict(Counter)
    tags = Counter()
    tagTags = defaultdict(Counter)
    tagTagTags = defaultdict()
    tagCount = 0
    iv = Counter()
    round_places = 4

    # Calculate the log of the posterior probability of a given sentence
    #  with a given part-of-speech labeling
    def posterior(self, sentence, label):
        emis = self.emission_probability(sentence[0], label[0])
        if emis == 0:
            emis = 0.000000001

        p = math.log(self.find_tag_prob(label[0]) * emis)
        for i in range(1, len(label)):
            word = sentence[i]
            tag = label[i]
            trans = self.transition_probability(tag, label[i - 1])
            emis = self.emission_probability(word, tag)
            if emis == 0:
                emis = 0.000000001
            if trans == 0:
                trans = 0.000000001
            p += math.log(trans * emis)

        return p

    # Do the training!
    #
    def train(self, data):

        for tup in data:
            words = tup[0]
            pos_tags = tup[1]
            # Store the word/tag count
            self.tagCount += len(pos_tags)
            for i in range(len(words)):
                # token - word count
                self.tokTags[words[i]][pos_tags[i]] += 1
                # store tag count
                self.tags[pos_tags[i]] += 1
            self.iv[pos_tags[0]] += 1
            for j in range(1, len(pos_tags)):
                # tag[j] given tag[j-1]
                self.tagTags[pos_tags[j]][pos_tags[j - 1]] += 1

            # tag[j] given tag[j-1] and tag[j-2]
            for k in range(2, len(pos_tags)):
                tag = pos_tags[k]
                prev_tag = pos_tags[k - 1]
                prev_prev_tag = pos_tags[k - 2]
                if tag not in self.tagTagTags:
                    temp_ctr = Counter()
                    temp_ctr[prev_prev_tag] += 1
                    self.tagTagTags[tag] = {prev_tag: temp_ctr}
                    continue
                elif prev_tag not in self.tagTagTags[tag]:
                    temp_ctr = Counter()
                    temp_ctr[prev_prev_tag] += 1
                    self.tagTagTags[tag][prev_tag] = temp_ctr
                    continue

                self.tagTagTags[tag][prev_tag][prev_prev_tag] += 1

        # Training Done!
        return True

    def get_simplified_tag_prob(self, word):
        if word not in self.tokTags:
            # Tag unknown words as noun with low confidence
            return "noun", 1.0 / 12
        counter = self.tokTags[word]
        max_tag = counter.most_common(1)[0][0]
        word_tag = find_prob(counter[max_tag], sum(counter.values()))

        return max_tag, word_tag

    # Functions for each algorithm.
    #
    def simplified(self, sentence):
        tag_list = []
        prob_list = []
        for word in sentence:
            tag, prob = self.get_simplified_tag_prob(word)
            tag_list.append(tag)
            prob_list.append(round(prob, self.round_places))

        return [[tag_list], [prob_list]]

    # Get the probability based on the count in self.tagTags
    def transition_probability(self, cur_tag, prev_tag):
        count_tag = self.tagTags[cur_tag][prev_tag]
        total_count = sum(self.tagTags[cur_tag].values())
        return float(count_tag) / total_count

    # Helper for viterbi
    def find_max_prob(self, prev_tags, tag):
        prob_array = []
        for p_tag in prev_tags:
            prob = self.transition_probability(tag, p_tag)
            prob_array.append(prob)
        max_prob = max(prob_array)
        return prev_tags[prob_array.index(max_prob)], max_prob

    def get_word_count(self, word):
        if word not in self.tokTags:
            return 1
        return sum(self.tokTags[word].values())

    def get_possible_tags(self, word):
        # Unknown words are labelled 'noun' intuitively
        if word not in self.tokTags:
            return ['noun']  # self.tags.keys()
        return self.tokTags[word].keys()

    def word_tag_count(self, word, tag):
        if word not in self.tokTags:
            # if the word is not known, calculate relative probability of the tags
            return float(self.tags[tag]) / self.tagCount
        return self.tokTags[word][tag]

    def find_tag_prob(self, tag):
        return float(self.tags[tag]) / self.tagCount

    # Calculate emission probability based on self.tokTags
    def emission_probability(self, word, tag):
        wt_count = self.word_tag_count(word, tag)
        wc = self.get_word_count(word)
        word_tag_prob = find_prob(wt_count, wc)
        # tag_prob = self.find_tag_prob(tag)

        return float(word_tag_prob)

    def hmm(self, sentence):
        v = defaultdict(Counter)

        start_word = sentence[0]
        s_prob_count = sum(self.iv.values())

        # Calculate for first word in the sentence based on IV
        possible_tags = self.get_possible_tags(start_word)
        for tag in possible_tags:
            v[0][tag] = self.emission_probability(start_word, tag) * find_prob(self.iv[tag], s_prob_count)

        # Viterbi
        for i in range(1, len(sentence)):
            word = sentence[i]
            possible_tags = self.get_possible_tags(word)
            for tag in possible_tags:
                max_tag, prev_max = self.find_max_prob(v[i - 1].keys(), tag)
                v[i][tag] = self.emission_probability(word, tag) * prev_max

        tag_list = [v[j].most_common(1)[0][0] for j in range(len(sentence))]

        return [[tag_list], []]

    # Helper for the complex model which accounts for two steps behind
    def find_two_tag_max(self, data, index, tag):
        t2 = self.find_max_prob(data[index - 1].keys(), tag)[0]
        t1 = self.find_max_prob(data[index - 2].keys(), t2)[0]

        tag_count = self.tags[tag]
        if t2 not in self.tagTagTags[tag] or t1 not in self.tagTagTags[tag][t2]:
            return float(self.tags[tag]) / self.tagCount  # 0.00000000001
        seq_tag_count = self.tagTagTags[tag][t2][t1]

        return find_prob(float(seq_tag_count), tag_count)

    def complex(self, sentence):
        w = defaultdict(Counter)
        start_word = sentence[0]
        s_prob_count = sum(self.iv.values())
        possible_tags = self.get_possible_tags(start_word)
        # Calculate for the first word based on IV
        for tag in possible_tags:
            w[0][tag] = self.emission_probability(start_word, tag) * find_prob(self.iv[tag], s_prob_count)

        prev_max = w[0].most_common(1)[0]

        if len(sentence) < 2:
            return [[[prev_max[0]]],
                    [[round(self.emission_probability(sentence[0], w[0].most_common(1)[0][0]), self.round_places)]]]

        second_word = sentence[1]
        possible_tags = self.get_possible_tags(second_word)
        for tag in possible_tags:
            # Run a viterbi like model to find the second tag
            prev_tag, prev_prob = self.find_max_prob(w[0].keys(), tag)
            w[1][tag] = self.emission_probability(second_word, tag) * prev_prob

        # Enhanced viterbi to calculate pos for further words
        for i in range(2, len(sentence)):
            word = sentence[i]
            possible_tags = self.get_possible_tags(word)
            for tag in possible_tags:
                w[i][tag] = self.emission_probability(word, tag) * self.find_two_tag_max(w, i, tag)

        tag_list = [w[j].most_common(1)[0][0] for j in range(len(sentence))]
        prob_list = [round(self.emission_probability(sentence[j], w[j].most_common(1)[0][0]), self.round_places) for j
                     in range(len(sentence))]

        return [[tag_list], [prob_list]]

    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself. 
    # It's supposed to return a list with two elements:
    #
    #  - The first element is a list of part-of-speech labelings of the sentence.
    #    Each of these is a list, one part of speech per word of the sentence.
    #
    #  - The second element is a list of probabilities, one per word. This is
    #    only needed for simplified() and complex() and is the marginal probability for each word.
    #
    def solve(self, algo, sentence):
        if algo == "Simplified":
            return self.simplified(sentence)
        elif algo == "HMM":
            return self.hmm(sentence)
        elif algo == "Complex":
            return self.complex(sentence)
        else:
            print "Unknown algo!"
