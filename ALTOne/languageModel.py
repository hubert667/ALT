from collections import Counter
import sys
import math

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

def  calculate_language_model(file_name, max_number_of_words):
    
    ngrams_probabilities=dict()
    ngrams_counts = Counter()
    num_lines = number_of_lines(file_name)
    source_file = open(file_name, 'r')

    for i, line in enumerate(source_file):
        if num_lines>100:
            if  i % (num_lines/100) is 0:
                sys.stdout.write('\r%d%%' % (i*100/num_lines,))
                sys.stdout.flush()
        ngrams=extract_ngrams(line,max_number_of_words)
        
        for ngram in ngrams:
            ngrams_counts[ngram] += 1
            
    one_word_counter=0
    for ngram in ngrams_counts.elements(): 
        if ngram[1]=='':
            one_word_counter+=1
             
    for ngram in ngrams_counts.elements():
        if ngram[1]!='':
            shorter_ngram=(ngram[1],ngram[2],'')
            probability=(float)(ngrams_counts[ngram])/(float)(ngrams_counts[shorter_ngram])
        else:
            probability=(float)(ngrams_counts[ngram])/one_word_counter
        ngrams_probabilities[ngram]=(probability) 
    
    return ngrams_probabilities,ngrams_counts

def extract_ngrams(line,max_number_of_words):

    list_of_sentences=line.split('.')
    list_of_ngrams=[]
    for sentence in list_of_sentences:
        list_of_words=sentence.split()
        list_of_words.insert(0,'<s>')
        list_of_words.append('<s>')
        for i in range(max_number_of_words):
            for k in range(len(list_of_words)-i):
                if i==0:
                    words_tuple=(list_of_words[k],'','')
                if i==1:
                    words_tuple=(list_of_words[k],list_of_words[k+1],'')
                if i==2:
                    words_tuple=(list_of_words[k],list_of_words[k+1],list_of_words[k+2])
                list_of_ngrams.append(words_tuple)   
    return list_of_ngrams

def save_language_model(model,file_name):
    out = open(file_name, 'w')
    for d in model:
        out.write('%s, %s\n' % (d, model[d]))
    out.close()