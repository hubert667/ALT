import sys
import math
import threading
import re

def translate(language,l1_given_source,source_given_l1,ngrams_prob,ngrams_prob_f,phrase_max_length,number_of_threads=1):
    beam_width=5
    source_file = open(language, 'r')
    output_file_name = 'translation_output'
    num_lines = number_of_lines(language)
    thread_list = []
    step_size=num_lines/number_of_threads

    print 'Creating seperate files for each thread'
    for i in xrange(number_of_threads):
        part_file = open('sentences%d'%i, 'w')
        for j in xrange(step_size):
            line = source_file.readline()
            source_file_to_sentences(line, part_file)
        #append whatever sentences are left to the last file
        if i is number_of_threads-1:
            line = True
            while line:
                line = source_file.readline()
                source_file_to_sentences(line, part_file)
        part_file.close()

    print 'Making a thread for each file to translate'
    for i in xrange(number_of_threads):
        input_file = 'sentences%d'%i
        output_file = 'translations%d'%i
        name = 'thread_%d'%i
        thread = Decoder(i, name, input_file, output_file, beam_width,\
                ngrams_prob, ngrams_prob_f, l1_given_source,\
                source_given_l1,phrase_max_length)
        thread.start()
        thread_list.append(thread)

    print 'Wait for all threads to complete'
    for t in thread_list:
        t.join()

    output_file = open(output_file_name, 'w')
    #append the files again
    for t in thread_list:
        part_file = open(t.output_file, 'r')
        output_file.writelines(part_file)
        output_file.write('\n')

def source_file_to_sentences(line, part_file):
    for sentence in re.split('[\.\?]',line):
        sentence.strip()
        if len(sentence):
            part_file.write(sentence + '\n')

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

def calculate_stupid_backoff(local_ngram_list,language_model):
        
        if len(local_ngram_list)<1:
            return 0 # this should never happen
        stupid_backoff_rate=0.4 #rate for stupid backoff
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
            return stupid_backoff_rate*calculate_stupid_backoff(shorten_ngram,language_model)

class Decoder (threading.Thread):

    def __init__(self, threadID, name, input_file, output_file, beam_width,\
            ngrams_prob, ngrams_prob_f, l1_given_source,\
            source_given_l1,phrase_max_length):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.input_file = input_file
        self.output_file = output_file
        self.beam_width = beam_width
        self.ngrams_prob = ngrams_prob
        self.ngrams_prob_f = ngrams_prob_f
        self.l1_given_source = l1_given_source
        self.source_given_l1 = source_given_l1
        self.phrase_max_length = phrase_max_length
    
    def run(self):
        print "Starting " + self.name
        self.translate_part_of_text()
        print "Exiting " + self.name

    def translate_part_of_text(self):       
        self.input_sentences = open(self.input_file, 'r')
        self.output = open(self.output_file, 'w')
        i=0
        step=100
        for sentence in self.input_sentences:
                i=i+1
                '''
                if len(self.input_sentences)>step:
                    if  i % (len(self.input_sentences)/step) is 0:
                        progress[number]=(i*step/len(input_sentences))
                        min_val=min(progress)
                        sys.stdout.write('\r%d%%' % (min_val,))
                        sys.stdout.flush()
                '''
                #sys.stdout.write(str(i)+"out of"+str(len(input_sentences)))
                if len(sentence.split())>=3:
                    graph=Graph(sentence,self.beam_width,self.ngrams_prob,self.ngrams_prob_f,\
                            self.l1_given_source,self.source_given_l1,self.phrase_max_length)
                    translation=graph.calculate_translation()
                    self.output.write(translation + '\n')
        self.input_sentences.close()
        self.output.close()

class Graph:
    """
    IMPORTANT NOTE: We assume that keys for language model and translations models
    (both translation models) are in this order: (source_language,destination_language)
    
    """
    source_phrase = ''
    destination_phrase=''
    l1_given_source={}
    source_given_l1={}
    max_phrase_length=3
    number_of_best_translations=10
    disortion_limit=5
    ngrams={}
    ngrams_f={}
    beam_width = 0
    nodes = []
    node_map = {} #maps indexes from nodes to their parents (sort of like pointers I guess?)
    node_stacks = [] #a list of stacks of node_id's. If time left, could replace nodes
    equiv_nodes = {} #maps the best node to its equivalents
    future_costs = []
    

    def __init__(self, source_phrase, beam_width,language_model,language_model_f,l1_given_source,source_given_l1,max_phrase_length):
        self.l1_given_source=l1_given_source
        self.source_given_l1=source_given_l1
        self.ngrams=language_model
        self.ngrams_f=language_model_f
        self.max_phrase_length=max_phrase_length
        self.source_phrase = source_phrase
        self.beam_width = beam_width
        sentence_len = len(source_phrase.split())
        self.node_stacks = [[]]*(sentence_len+1)
        self.future_costs = []

    def collapse_node(self, node, stack_num):
        '''
        This method finds nodes equivalent to node and makes pointers to them
        Don't know if this should be in here, or maybe at the graph level?
        '''
        #node1 = self.node_stacks[node_id[0]][node_id[1]]
        for n2 in xrange(len(self.node_stacks[stack_num])):
            n_id = (stack_num, n2) 
            node2 = self.node_stacks[n_id[0]][n_id[1]]
            if node.already_translated == node2.already_translated and\
                node.current_position_translation == node2.current_position_translation and\
                node.last_history == node2.last_history:
                if node2 in self.equiv_nodes:
                    if node2.probability >= node.probability:
                        self.equiv_nodes[node2].append(node)
                    else:
                        equivalents = self.equiv_nodes[node2].append(node2)
                        self.equiv_nodes[node].append(equivalents)
                        del self.equiv_nodes[node2]
                else:
                    if node2.probability >= node.probability:
                        self.equiv_nodes[node2] = [node]
                    else:
                        self.equiv_nodes[node] = [node2]
    
    def generate_next_nodes(self,node):
        """
        Generates all possible nodes from given node. 
        Returns dictionary. Keys: 1,2 or 3 (length of source phrase). Values: lists of nodes
        """
        coverage_vec=node.already_translated
        begin=0
        first_not_translated=-1
        end=0
        within=0
        list_of_positions=[]
        j=0
        node.cost = node.probability
        for i in range(len(coverage_vec)):
            j=i
            if i-first_not_translated<self.disortion_limit:
                if within==0 and coverage_vec[i]==0:
                    if first_not_translated==-1:
                        first_not_translated=i
                    begin=i
                    within =1
                elif within==1 and coverage_vec[i]==1:
                    end=i-1
                    within=0
                    node.cost+=self.future_costs[begin][end]
                    positions=self.generate_positions(begin,end)
                    list_of_positions=list_of_positions+positions
            else:
                break
        if within==1:
            positions=self.generate_positions(begin,j)
            node.cost+=self.future_costs[begin][j]
            list_of_positions=list_of_positions+positions
                       
        next_nodes=self.generate_nodes_from_positions(list_of_positions,node)
        return next_nodes
    
    def generate_positions(self,begin,end):
        """
        Generates all possible arrays [x,x2] where x>=begin and x2<end and the maximum legth od 3
        """
        positions=[]
        for length in range(self.max_phrase_length):
            for i in range(begin,end+1):
                if (i+length)<=end:
                    local=[i,i+length]
                    positions.append(local)
        return positions
    
    def generate_nodes_from_positions(self,list_of_positions,node):
        
        nodes={}
        for i in range(self.max_phrase_length):
            nodes[i+1]=[]
        for positions in list_of_positions:
            length=positions[1]-positions[0]+1
            source_phrase=' '.join(node.source_phrase[positions[0]:positions[1]+1])
            keys=self.l1_given_source.keys()
            translations=[phrase_pair[1] for j, phrase_pair in enumerate(keys) if phrase_pair[0] == source_phrase] 
            list_of_translations=[]
            for local_translation in translations:
                new_node=Node(local_translation,node,[positions[0],positions[1]])
                new_node.calculate_probability(self.ngrams, self.l1_given_source, self.source_given_l1)
                list_of_translations.append(new_node)
            list_of_translations=sorted(list_of_translations, key=lambda test: test.probability)
            list_of_translations=list_of_translations[0:self.number_of_best_translations]
            local_nodes=nodes[length]
            local_nodes=local_nodes+list_of_translations
            nodes[length]=local_nodes
        return nodes
    

    def expand_graph(self):
        '''
        This loops through nodes to expand/collapse them
        '''
        #self.expanded = False
        #for n_id in xrange(len(self.nodes)):

    def calculate_translation(self):
        
        self.compute_future_cost()
        words=self.source_phrase.split()
        coverage_vector=self.create_coverage_vector(len(words))
        start_node=Node('',None,[0,0])
        start_node.last_history=['<s>']
        start_node.source_phrase=self.source_phrase.split()
        start_node.already_translated=coverage_vector
        self.node_stacks[0].append(start_node)
        NODE_EXPANSION_LIMIT = 40
        for stack_num in xrange(len(self.node_stacks)):
            #print len(self.node_stacks[stack_num])
            for n in self.node_stacks[stack_num][:NODE_EXPANSION_LIMIT]:
                if not n.collapsed:
                    self.collapse_node(n,stack_num)
                if not n.stopped:
                    new_nodes = self.generate_next_nodes(n)
                    for i in new_nodes:
                        if stack_num+i < len(self.node_stacks):
                            nodes_to_add = sorted(new_nodes[i],key=lambda node: node.cost)
                            self.add_nodes(nodes_to_add, stack_num+i)

        #print len(self.node_stacks[stack_num])
        self.destination_phrase=self.generate_one_best_translation(self.node_stacks[-1][0])
        return self.destination_phrase

    
    def add_nodes(self, nodes_to_add, stack_num):
        STACK_LIMIT = 100
        new_stack = []
        old_stack = list(self.node_stacks[stack_num])
        while old_stack or nodes_to_add:
            if len(new_stack) > STACK_LIMIT:
                self.node_stacks[stack_num] = new_stack
                break
            if not old_stack or not nodes_to_add:
                #one of the lists is empty
                new_stack.extend(old_stack)
                new_stack.extend(nodes_to_add)
                self.node_stacks[stack_num] = new_stack[:STACK_LIMIT]
                break
            if old_stack[0].probability > nodes_to_add[0].probability:
                new_stack.append(old_stack.pop(0))
            else:
                new_stack.append(nodes_to_add.pop(0))


        """
        IMPORTANT NOTE:
        you changed code in this method to "self.node_stacks[0].append(node)" but it is not valid because as you can see this method
        was completely changed by me so please apply this in correct place
        """
        
        
        """
        for i in range(len(words)):
            word=words[i]
            keys=self.l1_given_source.keys()
            translations=[phrase_pair[1] for j, phrase_pair in enumerate(keys) if phrase_pair[0] == word] 
            for local_translation in translations:
                node=Node(local_translation,start_node,[i,i])
                node.calculate_probability(self.ngrams, self.l1_given_source, self.source_given_l1)
                self.nodes.append(node)
        """
    
    def generate_one_best_translation(self,best_node):
        words=[]
        current_node=best_node
        while current_node!=None:
            words.append(current_node.current_position_translation)
            current_node=current_node.previous_node
        words.reverse()
        translation=' '.join(words)
        return translation
    
    def create_coverage_vector(self,number):
        array=[]
        for i in range(number):
            array.append(0)
        return array
    
    def compute_future_cost(self):
        source = self.source_phrase.split()
        self.future_costs = []
        for i in xrange(len(source)):
            self.future_costs.append([])
            for j in xrange(len(source)):
                phrase = source[i:j+1]
                if (j-i) <= self.max_phrase_length:
                    possible_phrase_pairs = [phrase_pair for phrase_pair in\
                            self.l1_given_source if phrase_pair[0] == phrase]
                    if len(possible_phrase_pairs):
                        max_cost = -10000
                        for phrase_pair in possible_phrase_pairs:
                            cost = self.l1_given_source[phrase_pair] +\
                            self.calculate_language_model_probability("", phrase_pair[0], self.ngrams)
                            if cost > max_cost:
                                max_cost = cost
                        self.future_costs[i].append(max_cost)
                    else:
                        self.future_costs[i].append(-10000)
                if i is j:
                    self.future_costs[i].append(-10)
                self.future_costs[i].append(-10000)
    
    def calculate_translation_probability(self,position_to_translate,translation):
        """
        This method should be used only for calculating probabilities for future costs
        """
        
        phrase_pair=(' '.join(self.source_phrase[position_to_translate[0]:position_to_translate[1]+1]),translation)
        
        grade= math.log10(self.l1_given_source[phrase_pair])
        return grade
    
    def calculate_language_model_probability(self,history,translation,language_model):
        """
        This method should be used only for calculating probabilities for future costs
        IMPORTANT NOTE: assumption that translation length<=3
        """
        translation_array=translation.split()
        local_ngram=history[:]+translation_array
        '''
        while (len(local_ngram)>3):
            del local_ngram[0]
        '''
        local_ngram = local_ngram[-3:] #this takes the last 3 elements
        
        result_backoff=calculate_stupid_backoff(local_ngram,language_model)
        grade_language_model=math.log10(result_backoff)
        return grade_language_model

class Node:
    max_number_of_words=3 #max number of words in the history for language model
    previous_nodes=[]#links to thimport syse previous nodes
    last_history=[] #last n-1 words in history 
    already_translated=[]#  numbers of words which were translated- coverage vector
    current_positions=[] #indexes of words in the source sentence which are currently translated,first number indicates the beginning of the phrase and second indicates the end pf phrase
    source_phrase=[] #the whole source sentence
    current_position_translation='' #currently translated position
    probability=0
    stopped = False #this is to see if we should expand the node or not
    collapsed = False #difference with the prev one is that paths can go through this on the way back
    cost = 0

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
        self.cost = 0
        
    

    def calculate_probability(self,language_model,l1_given_source,source_given_l1):
        phrase_pair=(' '.join(self.source_phrase[self.current_positions[0]:self.current_positions[1]+1]),self.current_position_translation)
        
        grade1= math.log10(l1_given_source[phrase_pair])
        grade2=math.log10(source_given_l1[phrase_pair])
        
        translation_array=self.current_position_translation.split()
        local_ngram=self.previous_node.last_history[:]+translation_array
        '''
        while (len(local_ngram)>3):
            del local_ngram[0]
        '''
        local_ngram = local_ngram[-3:] #this takes the last 3 elements
        
        result_backoff=calculate_stupid_backoff(local_ngram,language_model)
        grade_language_model=-100
        if result_backoff!=0:
            grade_language_model=math.log10(result_backoff)
            
        
        phrase_penalty=-1
        
        word_penalty=len(translation_array)
        
        previous_end=self.previous_node.current_positions[1]
        disortion=-1*math.fabs(self.current_positions[0]-previous_end-1)
        
        result=grade1+grade2+grade_language_model+phrase_penalty+word_penalty+disortion;
        self.probability=result+self.previous_node.probability;
        return result
    

            
            
         
        
        
