import sys
import math

def translate(language,l1_given_source,source_given_l1,ngrams_prob,phrase_max_length):
    source_file = open(language, 'r')
    num_lines = number_of_lines(language)
    beam_width=5
    translations=[]
    for i, oneLine in enumerate(source_file):
        if num_lines>100:
            if  i % (num_lines/100) is 0:
                sys.stdout.write('\r%d%%' % (i*100/num_lines,))
                sys.stdout.flush()
        sentences=oneLine.split('.')
        for sentence in sentences:
            graph=Graph(sentence,beam_width,ngrams_prob,l1_given_source,source_given_l1,phrase_max_length)
            translation=graph.calculate_translation()
            translations.append(translation)
    save('translation',translations)       
    return 0

def save(file_name,translations):
    out = open(file_name, 'w')
    for translation in translations:
        out.write('%s\n' % (translation))

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


class Graph:
    """
    IMPORTANT NOTE: We assume that keys for language model and translations models
    (both translation models) are in this order: (source_language,destination_language)
    
    """
    source_phrase = ''
    destination_phrase=''
    l1_given_source={}
    source_given_l1={}
    max_phrase_length=0
    ngrams={}
    beam_width = 0
    nodes = []
    node_map = {} #maps indexes from nodes to their parents (sort of like pointers I guess?)
    node_stacks = [] #a list of stacks of node_id's. If time left, could replace nodes
    equiv_nodes = {} #maps the best node to its equivalents
    expanded = True #This shows if the graph can still be expanded

    def __init__(self, source_phrase, beam_width,language_model,l1_given_source,source_given_l1,max_phrase_length):
        self.l1_given_source=l1_given_source
        self.source_given_l1=source_given_l1
        self.ngrams=language_model
        self.max_phrase_length=max_phrase_length
        self.source_phrase = source_phrase
        self.beam_width = beam_width
        sentence_len = len(source_phrase.split())
        self.node_stacks = [[]]*sentence_len

    def expand_graph(self):
        '''
        This loops through nodes to expand/collapse them
        '''
        #self.expanded = False
        #for n_id in xrange(len(self.nodes)):
        for stack in self.node_stacks:
            for n in stack:
                if not n.collapsed:
                    self.collapse_node(n_id)
                    #self.expanded = True
                if not n.stopped:
                    self.expand_node(n_id)
                    #self.expanded = True

    def expand_node(self, node_id):
        '''
        This method creates new nodes from node
        '''
        #node = self.nodes[node_id]
        #self.nodes[node_id] = node 
        return 0

    def collapse_node(self, node_id):
        '''
        This method finds nodes equivalent to node and makes pointers to them
        Don't know if this should be in here, or maybe at the graph level?
        '''
        node1 = self.node_stacks[node_id[0]][node_id[1]]
        for n2 in xrange(len(self.node_stacks[node_id[0]])):
            n_id = (node_id[0], n2) 
            node2 = self.nodes[n_id[0]][n_id[1]]
            if node1.already_translated == node2.already_translated and\
                node1.current_position_translation == node2.current_position_translation and\
                node1.last_history == node2.last_history:
                if node2 in self.equiv_nodes:
                    if node2.probability >= node1.probability:
                        self.equiv_nodes[n_id].append(node_id)
                    else:
                        equivalents = self.equiv_nodes[n_id].append(n_id)
                        self.equiv_nodes[node_id].append(equivalents)
                        del self.equiv_nodes[n_id]
                else:
                    if node2.probability >= node1.probability:
                        self.equiv_nodes[n_id] = [node_id]
                    else:
                        self.equiv_nodes[node_id] = [n_id]
    
    def calculate_translation(self):
        
        words=self.source_phrase.split()
        coverage_vector=self.create_coverage_vector(len(words))
        start_node=Node('',None,[0,0])
        start_node.last_history=['<s>']
        start_node.source_phrase=self.source_phrase.split()
        start_node.already_translated=coverage_vector
        for i in range(len(words)):
            word=words[i]
            keys=self.l1_given_source.keys()
            translations=[phrase_pair[1] for j, phrase_pair in enumerate(keys) if phrase_pair[0] == word] 
            for local_translation in translations:
                node=Node(local_translation,start_node,[i,i])
                node.calculate_probability(self.ngrams, self.l1_given_source, self.source_given_l1,local_translation)
                self.node_stacks[0].append(node)
        return self.destination_phrase
    
    def create_coverage_vector(self,number):
        array=[]
        for i in range(number):
            array.append(0)
        return array

    def compute_future_cost(i,j):
        source = self.source_phrase.split()[i:j+1]
        if j-i =< self.max_phrase_length:
            possible_phrase_pairs = [phrase_pair for phrase_pair in self.l1_given_source if phrase_pair[0] == source]
            cost = self.l1_given_source[phrase_pair] + self.ngrams[phrase_pair[0]]
            #ngrams = source lm?
        if i is j:
            return -10 + self.
        return -10000

class Node:
    max_number_of_words=3 #max number of words in the history for language model
    stupid_backoff_rate=0.4 #rate for stupid backoff
    previous_nodes=[]#links to the previous nodes
    last_history=[] #last n-1 words in history 
    already_translated=[]#  numbers of words which were translated- coverage vector
    current_positions=[] #indexes of words in the source sentence which are currently translated,first number indicates the beginning of the phrase and second indicates the end pf phrase
    source_phrase=[] #the whole source sentence
    current_position_translation='' #currently translated position
    probability=0
    stopped = False #this is to see if we should expand the node or not
    collapsed = False #difference with the prev one is that paths can go through this on the way back

    def __init__(self,_current_position_translation,_previous_node,_current_positions):
        
        if(_previous_node is not None):
            self.last_history=_previous_node.last_history[:]
            self.source_phrase=_previous_node.source_phrase
            self.already_translated=_previous_node.already_translated[:]
            for i in range(_current_positions[0],_current_positions[1]+1):
                self.already_translated[i]=1
        current_words_translations=_current_position_translation.split()
        self.last_history=self.last_history+current_words_translations
        while len(self.last_history)>3:
            del self.last_history[0]          
        self.current_positions=_current_positions
       
        self.previous_node=_previous_node
        self.current_position_translation=_current_position_translation 
        
    

    def calculate_probability(self,language_model,l1_given_source,source_given_l1,translation):
        phrase_pair=(' '.join(self.source_phrase[self.current_positions[0]:self.current_positions[1]+1]),self.current_position_translation)
        
        grade1= math.log10(l1_given_source[phrase_pair])
        grade2=math.log10(source_given_l1[phrase_pair])
        
        translation_array=translation.split()
        local_ngram=self.previous_node.last_history[:]+translation_array
        while (len(local_ngram)>3):
            del local_ngram[0]
        
        result_backoff=self.calculate_stupid_backoff(local_ngram,language_model)
        grade_language_model=math.log10(result_backoff)
        
        phrase_penalty=-1
        
        word_penalty=len(translation_array)
        
        previous_end=self.previous_node.current_positions[1]
        disortion=-1*math.fabs(self.current_positions[0]-previous_end-1)
        
        result=grade1+grade2+grade_language_model+phrase_penalty+word_penalty+disortion;
        self.probability=result+self.previous_node.probability;
        return result
    
    def calculate_stupid_backoff(self,local_ngram_list,language_model):
        
        if len(local_ngram_list)<1:
            return 0 # this should never happen
        
        local_ngram=tuple(local_ngram_list)
        i=len(local_ngram_list)
        if i==1:
            local_ngram=(local_ngram_list[0],'','')
        if i==2:
            local_ngram=(local_ngram_list[0],local_ngram_list[1],'')
        if i==3:
            local_ngram=(local_ngram_list[0],local_ngram_list[1],local_ngram_list[2])
            
        if local_ngram in language_model:
            return language_model[local_ngram]
        else:
            shorten_ngram=local_ngram_list[:]
            del shorten_ngram[0]
            return self.stupid_backoff_rate*self.calculate_stupid_backoff(shorten_ngram,language_model)
            
            
         
        
        
