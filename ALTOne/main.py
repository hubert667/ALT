# phrase pair extractor

"""
By Hubert Szostek (10656804) and Sander Nugteren (6042023)
"""

import argparse
from collections import Counter
import sys

def reordering_probabilities(phrase_pair_reordering_freqs):
    """Calculates reordering probabilities based on frequency of jumps
    
    Keywords arguments:
    phrase_pair_reordering_freqs- dictionary with key: phrase pair and value: tuple of 8 values of frequency of jumps
    
    Returns dictionary of reordering probabilities for every phrase phrase. Key: pair phrase, Value: list of 8 probabilities
    """
    phrase_pair_probabilities=dict
    for phrase_pair, freqs in phrase_pair_reordering_freqs:
        sum_of_prob=0;
        probabilities=list
        for i in len(freqs):
            sum_of_prob+=freqs[i]
        for i in len(freqs):
            probabilities.append(freqs[i]/sum_of_prob)
        phrase_pair_probabilities[phrase_pair]=probabilities;
    return phrase_pair_probabilities

def histogram_of_orientation(phrase_pair_reordering_freqs):
    """Calculates histogram of counts of orientations 
    
    Keywords arguments:
    phrase_pair_reordering_freqs- dictionary with key: phrase pair and value: tuple of 8 values of frequency of jumps
    
    Returns 8 tuple of dictionaries which maps from frequency of some kind of jump to number of phrases which
    """
    reordering_histogram={Counter,Counter,Counter,Counter,Counter,Counter,Counter,Counter}
    for phrase_pair, freqs in phrase_pair_reordering_freqs:
        for i in len(freqs):
            number=freqs[i]
            someCounter=reordering_histogram[i]
            someCounter[number]+=1
    return reordering_histogram

def conditional_probabilities(phrase_pair_freqs, 
                              l1_phrase_freqs, l2_phrase_freqs):
    """Calculate  the conditional probability of phrase pairs in both directions.
    
    Keyword arguments:
    phrase_pair_freqs -- counter of phrase pairs
    l1_phrase_freqs -- counter of phrases in language 1
    l2_phraes_freqs -- counter of phrases in lanuage 2
    
    Returns 2 dictionaries mapping a phrase pair to P(l1 | l2) and P(l2 | l1)
    """
    l1_given_l2 = {}
    l2_given_l1 = {}
    for phrase_pair, freq in phrase_pair_freqs.iteritems():
        l1_given_l2[phrase_pair] = float(freq) / l2_phrase_freqs[phrase_pair[1]]
        l2_given_l1[phrase_pair] = float(freq) / l1_phrase_freqs[phrase_pair[0]]

    return l1_given_l2, l2_given_l1

def phrase_probabilities(phrase_freqs):
    """Calculate the probability of a phrase.
    
    Keyword arguments:
    phrase_freqs -- counter of phrases
    
    Returns a dictionary mapping a phrase to its probabilitly
    """
    freq_sum = sum(phrase_freqs.values())
    phrase_probs = {}
    for phrase, freq in phrase_freqs.iteritems():
        phrase_probs[phrase] = float(freq) / freq_sum

    return phrase_probs

def lexical_probabilities(phrase_pair_freqs,l1_word_given_l2,l2_word_given_l1,alignments):
    """Calculate the lexical probability of a phrase given phrase in the second language .
    
    Keyword arguments:
    phrase_pair_freqs -- counter of phrases
    l1_word_given_l2 -- words probabilities
    alignments -- dictionary of words alignments for every phrase
    
    Returns two dictionaries mapping a phrase pair to its probability
    """
    l1_lexical_given_l2= {}
    l2_lexical_given_l1={}
    for phrase_pair, freq in phrase_pair_freqs.iteritems():
        words_l1= phrase_pair[0].split()
        words_l2= phrase_pair[1].split()
        aligns=alignments[phrase_pair]
        result1=1
        for word1 in words_l1:
            sumOf=0
            iterations=0
            for word2 in words_l2:
                pair=word1,word2
                if pair in aligns:
                    sumOf+=l1_word_given_l2[pair]
                    iterations+=1
            if iterations!=0:
                result1*=sumOf/iterations
            else:
                result1=1
        result2=1
        for word2 in words_l2:
            sumOf=0
            iterations=0
            for word1 in words_l1:
                pair=word1,word2
                if pair in aligns:
                    sumOf+=l2_word_given_l1[pair]
                    iterations+=1
            if iterations!=0:
                result2*=sumOf/iterations
            else:
                result2=1
        l1_lexical_given_l2[phrase_pair]=result1    
        l2_lexical_given_l1[phrase_pair]=result2           
        #phrase_probs[phrase_pair] = float(freq) / freq_sum

    return l1_lexical_given_l2,l2_lexical_given_l1
    

def joint_probabilities(l1_given_l2, l2_phrase_probs):
    """Calculate the joint probability of a phrase pair:
    P(l1, l2) = P(l1 | l2) * P(l2)
    
    Keyword arguments:
    l1_given_l2 -- dictionary mapping a phrase pair (l1,l2) to its
                   conditional probability P(l1 | l2)
    l2_phrase_probs -- dictionary mapping a phraes to its probability
    
    Return a dictionary that maps a phrase pair to its joint probability
    """
    joint_probs = {}
    for phrase, prob in l1_given_l2.iteritems():
        joint_probs[phrase] = prob * l2_phrase_probs[phrase[1]]

    return joint_probs

def add_phrase_alignment(collection, phrase, max_length,
                         l1_length, l2_length):
    """Add a phrase alignment to a collection if:
    - its length is smaller or equal to the max length
    - the alignment is a contituent of the sentences
    
    Keyword arguments:
    collection -- a list or set
    phrase -- a 4-tuple (min1,min2,max1,max2) denoting the range of
              the constituents in language 1 and 2
    max_length -- the maximum length of a phrase in the phrase alignment
    l1_length -- the length of the sentence in language 1
    l2_length -- the length of teh sentence in language 2
    """
    if phrase and phrase[2] - phrase[0]+1 <= max_length \
              and phrase[3] - phrase[1]+1 <= max_length \
              and phrase[0] >= 0 and phrase[1] >= 0     \
              and phrase[2] < l1_length and phrase[3] < l2_length:
        if isinstance(collection, list):
            collection.append(phrase)
        elif isinstance(collection, set):
            collection.add(phrase)
        else:
            return NotImplemented

def extract_phrase_pair_freqs(alignments_file, language1_file,
                              language2_file, 
                              max_length = float('inf')):
    """Extract and count the frequency of all phrase pairs given an
    alignment between sentences.
    
    Keyword arguments:
    alignments_file -- file that contains the alignments
    language1_file -- file containing sentences from language 1
    language2_file -- file containing sentences from language 2
    max_length -- maximum length of phrase pairs
    
    Returns counter of phrase-pairs, counter of phrases in language1
            and counter of phrases in language2
    """
    alignments_for_phrases=dict()
    phrase_pair_freqs = Counter()
    l1_phrase_freqs = Counter()
    l2_phrase_freqs = Counter()
    words_pair_freqs = Counter()
    l1_words_freqs = Counter()
    l2_words_freqs = Counter()
    num_lines = number_of_lines(alignments_file)
    alignments = open(alignments_file, 'r')
    language1 = open(language1_file, 'r')
    language2 = open(language2_file, 'r')
    
    for i, str_align in enumerate(alignments):
        if num_lines>100:
            if  i % (num_lines/100) is 0:
                sys.stdout.write('\r%d%%' % (i*100/num_lines,))
                sys.stdout.flush()
        l1 = language1.next()
        l2 = language2.next()
        #print str_align, l1, l2
        align = str_to_alignments(str_align)
        alignCopy = str_to_alignments(str_align)
        words_aligns=create_word_align(align,l1,l2)
        phrase_alignments = extract_alignments(align, len(l1.split()),
                len(l2.split()), max_length)
        
        for phrase_pair in extract_phrase_pairs_gen(phrase_alignments, l1, l2):
            phrase_pair_freqs[phrase_pair] += 1
            l1_phrase_freqs[phrase_pair[0]] += 1
            l2_phrase_freqs[phrase_pair[1]] += 1
            alignments_for_phrases[phrase_pair]=words_aligns;
            
        for words_pair in extract_words_pairs_gen(alignCopy, l1, l2):
            words_pair_freqs[words_pair] += 1
            l1_words_freqs[words_pair[0]] += 1
            l2_words_freqs[words_pair[1]] += 1

    alignments.close()
    language1.close()
    language2.close()
    sys.stdout.write('\n')
    return phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs,alignments_for_phrases, words_pair_freqs, l1_words_freqs, l2_words_freqs

def extract_phrase_pair_jump_freqs(alignments_file, language1_file,
                              language2_file, phrase_lvl=True, 
                              max_length = float('inf')):
    """Extract and count the frequency of all phrase pairs given an
    alignment between sentences.
    
    Keyword arguments:
    alignments_file -- file that contains the alignments
    language1_file -- file containing sentences from language 1
    language2_file -- file containing sentences from language 2
    max_length -- maximum length of phrase pairs
    
    Returns counter of phrase-pairs, counter of phrases in language1
            and counter of phrases in language2
    """
    num_lines = number_of_lines(alignments_file)
    alignments = open(alignments_file, 'r')
    language1 = open(language1_file, 'r')
    language2 = open(language2_file, 'r')
    corpus_dict = {} 
    
    for i, str_align in enumerate(alignments):
        if num_lines>100:
            if  i % (num_lines/100) is 0:
                sys.stdout.write('\r%d%%' % (i*100/num_lines,))
                sys.stdout.flush()
        l1 = language1.next()
        l2 = language2.next()
        #print str_align, l1, l2
        align = str_to_alignments(str_align)
        alignCopy = str_to_alignments(str_align)
        words_aligns=create_word_align(align,l1,l2)
        phrase_alignments = extract_alignments(align, len(l1.split()),
                len(l2.split()), max_length)
        
        if phrase_lvl:
            sentence_dict = {}
            while phrase_alignments:
                phrase = phrase_alignments.pop()
                if phrase not in sentence_dict:
                    #counts for a particular phrase have the form:
                    #[lrm, lrs, lrdl, lrdr, rlm, rls, rldl, rldr]
                    #phrase_count = 8*[0]
                    sentence_dict[phrase] = 8*[0]
                for a in phrase_alignments:
                    if a not in sentence_dict:
                        sentence_dict[a] = 8*[0]
                    if a[1] is phrase[3]+1:
                        #Left to right jumps
                        if a[0] is phrase[2]+1:
                            #lr_monotone
                            sentence_dict[phrase][0] +=1
                            sentence_dict[a][4] +=1
                        elif a[2] is phrase[0]-1:
                            #lr_swap
                            sentence_dict[phrase][1] +=1
                            sentence_dict[a][5] +=1
                        elif a[0] > phrase[2]:
                            #lr_discontinuous_left
                            sentence_dict[phrase][2] +=1
                            sentence_dict[a][6] +=1
                        elif a[0] < phrase[2]:
                            #lr_discontinuous_right
                            sentence_dict[phrase][3] +=1
                            sentence_dict[a][7] +=1
                    elif phrase[1] is a[3]+1:
                        #right to left jumps
                        if phrase[0] is a[2]+1:
                            #rl_monotone
                            sentence_dict[phrase][4] +=1
                            sentence_dict[a][0] +=1
                        elif phrase[2] is a[0]-1:
                            #rl_swap
                            sentence_dict[phrase][5] +=1
                            sentence_dict[a][1] +=1
                        elif phrase[0] > a[2]:
                            #rl_discontinuous_left (???)
                            sentence_dict[phrase][6] +=1
                            sentence_dict[a][2] +=1
                        elif phrase[0] < a[2]:
                            #rl_discontinuous_right (???)
                            sentence_dict[phrase][7] +=1
                            sentence_dict[a][3] +=1
            for phrase in sentence_dict:
                phrase_tup = extract_phrase_pairs_gen([phrase], l1, l2).next()
                if phrase_tup in corpus_dict:
                    for x in xrange(len(sentence_dict[phrase])):
                        corpus_dict[phrase_tup][x] += sentence_dict[phrase][x]
                else:
                    corpus_dict[phrase_tup] = sentence_dict[phrase]

    alignments.close()
    language1.close()
    language2.close()
    sys.stdout.write('\n')
    return corpus_dict

def extract_words_pair_freqs(alignments_file, language1_file,
                              language2_file, 
                              max_length = float('inf')):
    """Extract and count the frequency of all words pairs given an
    alignment between sentences.
    
    Keyword arguments:
    alignments_file -- file that contains the alignments
    language1_file -- file containing sentences from language 1
    language2_file -- file containing sentences from language 2
    max_length -- maximum length of phrase pairs
    
    Returns counter of words-pairs, counter of words in language1
            and counter of words in language2
    """
    words_pair_freqs = dict()
    l1_words_freqs = dict()
    l2_words_freqs = dict()
    num_lines = number_of_lines(alignments_file)
    alignments = open(alignments_file, 'r')
    language1 = open(language1_file, 'r')
    language2 = open(language2_file, 'r')
    
    for i, str_align in enumerate(alignments):
        if num_lines>100:
            if  i % (num_lines/100) is 0:
                sys.stdout.write('\r%d%%' % (i*100/num_lines,))
                sys.stdout.flush()
        l1 = language1.next()
        l2 = language2.next()
        #print str_align, l1, l2
        align = str_to_alignments(str_align)

        for phrase_pair in extract_words_pairs_gen(align, l1, l2):
            if phrase_pair in words_pair_freqs:
                words_pair_freqs[phrase_pair] += 1
            else:
                words_pair_freqs[phrase_pair] = 1
                
            if phrase_pair[0] in l1_words_freqs:
                l1_words_freqs[phrase_pair[0]] += 1
            else:
                l1_words_freqs[phrase_pair[0]] = 1
            
            if phrase_pair[1] in l2_words_freqs:
                l2_words_freqs[phrase_pair[1]] += 1
            else:
                l2_words_freqs[phrase_pair[1]] = 1

    alignments.close()
    language1.close()
    language2.close()
    sys.stdout.write('\n')
    return words_pair_freqs, l1_words_freqs, l2_words_freqs

def create_word_align(align,l1,l2):
    """Given alignments, extract words pairs from 2 sentences and save as tuple
    
    Keyword arguments:
    aligns -- list of words alignments.
    l1 -- sentence in language 1
    l2 -- sentence in language 2
    
    Yield a words pair
    """
    l1_words = l1.strip().split()
    l2_words = l2.strip().split()
    new_aligns=set()
    for k1, k2 in align:
        new_aligns.add((l1_words[k1],l2_words[k2]))
    return  new_aligns;

def extract_words_pairs_gen(aligns, l1, l2):
    """Given alignments, extract words pairs from 2 sentences
    
    Keyword arguments:
    aligns -- list of words alignments.
    l1 -- sentence in language 1
    l2 -- sentence in language 2
    
    Yield a words pair
    """
    l1_words = l1.strip().split()
    l2_words = l2.strip().split()
    for k1, k2 in aligns:
        yield ((l1_words[k1]), 
               (l2_words[k2]))
        
def extract_phrase_pairs_gen(phrase_alignments, l1, l2):
    """Given alignments, extract phrase pairs from 2 sentences
    
    Keyword arguments:
    phrase_alignments -- list of phraes alignments. A phrase alignment
                         is a 4 tuple denoting the range of the constituents
    l1 -- sentence in language 1
    l2 -- sentence in language 2
    
    Yield a 2-tuple containing a phrase pair
    """
    l1_words = l1.strip().split()
    l2_words = l2.strip().split()
    for min1, min2, max1, max2 in phrase_alignments:
        yield (' '.join(l1_words[min1:max1+1]), 
               ' '.join(l2_words[min2:max2+1]))
    
def str_to_alignments(string):
    """Parse an alignment from a string
    
    Keyword arguments:
    string -- contains alignment
    
    Return a set of 2-tuples. First value is index of word in language 1
           second value is index of word in language 2
    """
    string_list = string.strip().split()
    alignments = set()
    
    for a_str in string_list:
        a1_str, a2_str = a_str.split('-')
        alignments.add((int(a1_str), int(a2_str)))

    return alignments

def phrase_alignment_expansions(phrase_alignments, max_length = float('inf')):
    """For each language find the words that are not covered with the given
    phrase alignment.
    E.g. phrase_alignments = [(0,0), (2,0)]
    returns [1], []
    because index 1 in sentence 1 is not covered.
    
    Keyword arguments:
    phrase_alignments -- list of 2-tuples denoting the alignment between words
    max_length -- maximum length of a phrase alignment
    
    Returns 2 lists of indexes that are not covered
    """
    min1, min2, max1, max2 = phrase_range(phrase_alignments)
    if max1-min1+1 > max_length or max2-min2+1 > max_length:
        return [], []

    range1 = range(min1, max1+1)
    range2 = range(min2, max2+1)
    for a1, a2 in phrase_alignments:
        if a1 in range1:
            range1.remove(a1)
        if a2 in range2:
            range2.remove(a2)

    return range1, range2
    
def phrase_range(phrase_alignments):
    """Calcualte the range of a phrase alignment
    
    Keyword arguments:
    phrase_alignments -- list of 2-tuples denoting the alignment between words
    
    Returns a 4-tuples denoting the range of the phrase alignment
    """
    min1 = min2 = float('inf')
    max1 = max2 = float('-inf')
    for (a1, a2) in phrase_alignments:
        if a1 < min1:
            min1 = a1
        if a1 > max1:
            max1 = a1
        if a2 < min2:
            min2 = a2
        if a2 > max2:
            max2 = a2

    return min1, min2, max1, max2

def extract_alignments(word_alignments, l1_length, l2_length,
                       max_length = float('inf')):
    """Extracts all alignments between 2 sentences given a word alignment
    
    Keyword arguments:
    word_alignemnts -- set of 2-tuples denoting alignment between words in 
                       2 sentences
    l1_length -- length of sentence 1
    l2_length -- length of sentence 2
    max_length -- maximum length of a phrase pair
    
    Returns set of 4-tuples denoting the range of phrase_alignments
    """
    phrase_queue = set()
    #copy to use later for singletons
    word_alignments_orig = set(word_alignments)
    # First form words into phrase pairs
    while len(word_alignments):        
        phrase_alignment_init = word_alignments.pop()
        phrase_alignment = set([phrase_alignment_init])
        phrase_alignment_exp = [[phrase_alignment_init[0]], 
                                [phrase_alignment_init[1]]]
        while phrase_alignment_exp[0] or phrase_alignment_exp[1]:
            added_points = set([(x, y) for (x, y) in word_alignments 
                            if (x in phrase_alignment_exp[0] 
                            or y in phrase_alignment_exp[1])])
            # stop if no alignment can fill the gaps
            if not added_points:
                break

            phrase_alignment |= added_points
            word_alignments -= added_points
            phrase_alignment_exp = phrase_alignment_expansions(phrase_alignment, max_length)

        align_range = phrase_range(phrase_alignment)
        add_phrase_alignment(phrase_queue, align_range, max_length,
                             l1_length, l2_length)

    #Then loop over phrase pairs to join them together into new ones
    phrase_alignment_list = set()
    while len(phrase_queue):
        p1 = phrase_queue.pop()
        new_p3 = set()
        #add singletons
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if x is p1[0]-1])
        if not singleton:
            p3 = p1[0]-1, p1[1], p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length, 
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if x is p1[2]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2]+1, p1[3]
            add_phrase_alignment(new_p3, p3, max_length, 
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if y is p1[1]-1])
        if not singleton:
            p3 = p1[0], p1[1]-1, p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if y is p1[3]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2], p1[3]+1
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)

        for p2 in phrase_queue:
            p3 = None
            if p1[0] is p2[2]+1 and p1[1] is p2[3]+1:
                #p2 above, to the left of p1
                p3 = p2[0], p2[1], p1[2], p1[3]
            elif p1[2] is p2[0]-1 and p1[1] is p2[3]+1:
                #p2 above, to the right of p1
                p3 = p1[0], p2[1], p2[2], p1[3]
            elif p1[0] is p2[2]+1 and p1[3] is p2[1]-1:
                #p2 below, to the left of p1
                p3 = p2[0], p1[1], p1[2], p2[3]
            elif p1[2] is p2[0]-1 and p1[3] is p2[1]-1:
                #p2 below, to the right of p1
                p3 = p1[0], p1[1], p2[2], p2[3]
            # if p3 exists and is smaller or equal to the max length
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)

        phrase_alignment_list.add(p1)
        phrase_queue |= new_p3

    return phrase_alignment_list

def phrase_pairs_to_file(file_name,l1_given_l2, l2_given_l1, l1_lexical_given_l2, l2_lexical_given_l1,l1_phrase_freqs, l2_phrase_freqs, phrase_pair_freqs ):
    """Write phrase pairs and their joint and conditional probabilities to a file
    
    Keyword arguments:
    file_name -- name of file for writing
    phrase_pairs -- list of phrase pairs
    joint_probs -- dictionary mapping phrase pair to its joints probability
    l1_given_l2 -- dictionary mapping phrase pair (l1,l2) to is conditional 
                   probability P(l1 | l2)
    l2_given_l1 -- dictionary mapping phrase pair (l1,l2) to is conditional 
                   probability P(l2 | l1)
    """
    out = open(file_name, 'w')
    for pair in phrase_pair_freqs:
        out.write('%s ||| %s ||| %s %s %s %s ||| %s %s %s)\n' % (pair[0],pair[1], l1_given_l2[pair], l2_given_l1[pair], l1_lexical_given_l2[pair],l2_lexical_given_l1[pair],l1_phrase_freqs[pair[0]], l2_phrase_freqs[pair[1]], phrase_pair_freqs[pair]))

    out.close()

def number_of_lines(file_name):
    """Counts the number of lines in a file
    
    Keywords arguments:
    file_name -- name of file
    
    Returns number of lines
    """
    amount = 0
    doc = open(file_name, 'r')
    for _ in doc:
        amount += 1

    doc.close()
    return amount

def main():
    """Read the following arguments from the cmd line:
    - name of file containing the alignments
    - name of file containing sentence of language 1
    - name of file containing sentence of language 2
    - name of file for writing output
    - maximum length of a phrase pair
    """
    
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--alignments",
        help="File containing alignments")
    arg_parser.add_argument("-l1", "--language1",
        help="File containing sentences of language 1")
    arg_parser.add_argument("-l2", "--language2",
        help="File containing sentences of language 2")
    arg_parser.add_argument("-o", "--output",
        help="Output file")
    
    args = arg_parser.parse_args()
    alignments = args.alignments
    language1 = args.language1
    language2 = args.language2
    output_name=args.output;

    alignments="alignments"
    language1="language1"
    language2="language2"
    output_name="output"
    max_length=7

    freqs = extract_phrase_pair_jump_freqs(alignments, language1, language2, max_length)
    out = open(output_name, 'w')
    for phrase in freqs:
        for f in xrange(len(freqs[phrase])):
            out.write(str(freqs[phrase][f]))
            out.write(',')
        out.write('\n')
    '''
    phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs,words_alignments,words_pair_freqs, l1_words_freqs, l2_words_freqs = freqs
    l1_given_l2, l2_given_l1 = conditional_probabilities(phrase_pair_freqs, 
                              l1_phrase_freqs, l2_phrase_freqs)
    l1_word_given_l2, l2_word_given_l1 = conditional_probabilities(words_pair_freqs, 
                              l1_words_freqs, l2_words_freqs)
    l1_lexical_given_l2,l2_lexical_given_l1= lexical_probabilities(phrase_pair_freqs,l1_word_given_l2,l2_word_given_l1,words_alignments)
    #l2_phrase_probs = phrase_probabilities(l2_phrase_freqs)
    #joint_probs = joint_probabilities(l1_given_l2, l2_phrase_probs)
    phrase_pairs_to_file(output_name,l1_given_l2, l2_given_l1, l1_lexical_given_l2,l2_lexical_given_l1,l1_phrase_freqs, l2_phrase_freqs, phrase_pair_freqs )
    '''
    
if __name__ == '__main__':
    main()
