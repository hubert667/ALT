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
    equiv_nodes = {} #maps the best node to its equivalents
    expanded = True #This shows if the graph can still be expanded
    

    def __init__(self, source_phrase, beam_width,language_model,l1_given_source,source_given_l1,max_phrase_length):
        self.l1_given_source=l1_given_source
        self.source_given_l1=source_given_l1
        self.ngrams=language_model
        self.max_phrase_length=max_phrase_length
        self.source_phrase = source_phrase
        self.beam_width = beam_width

    def expand_graph(self):
        '''
        This loops through nodes to expand/collapse them
        '''
        self.expanded = False
        for n_id in xrange(len(self.nodes)):
            n = self.nodes[n_id]
            if not n.collapsed:
                self.collapse_node(n_id)
                self.expanded = True
            if not n.stopped:
                self.expand_node(n_id)
                self.expanded = True

    def expand_node(self, node_id):
        '''
        This method creates new nodes from node
        '''
        
        node = self.nodes[node_id]
        list_of_next_nodes=self.generate_next_nodes(node)
        """
        nodes from this list should be added to appropriate stacks, and some of them can be deleted
        if limit of the stacks is exceded
        """
        
        return 0

    def collapse_node(self, node_id):
        '''
        This method finds nodes equivalent to node and makes pointers to them
        Don't know if this should be in here, or maybe at the graph level?
        '''
        node1 = self.nodes[node_id]
        for n_id in xrange(len(self.nodes)):
            node2 = self.nodes[n_id]
            #if NODES EQUIVALENT:
            if node1.already_translated == node2.already_translated and\
                node1.current_position_translation == node2.current_position_translation:
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
        return 0
    
    def generate_next_nodes(self,node):
        """
        Generates all possible nodes from given node
        """
        coverage_vec=node.already_translated
        begin=0
        end=0
        within=0
        list_of_positions=[]
        for i in range(len(coverage_vec)):
            if within==0 and coverage_vec[i]==0:
                begin=i
                within =1
            elif within==1 and coverage_vec[i]==1:
                end=i-1
                within=0
                positions=self.generate_positions(begin,end)
                list_of_positions=list_of_positions+positions
        if within==1:
            positions=self.generate_positions(begin,len(coverage_vec)-1)
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
        
        nodes=[]
        for positions in list_of_positions:
            source_phrase=' '.join(node.source_phrase[positions[0]:positions[1]+1])
            keys=self.l1_given_source.keys()
            translations=[phrase_pair[1] for j, phrase_pair in enumerate(keys) if phrase_pair[0] == source_phrase] 
            for local_translation in translations:
                new_node=Node(local_translation,node,[positions[0],positions[1]])
                new_node.calculate_probability(self.ngrams, self.l1_given_source, self.source_given_l1)
                nodes.append(new_node)
        return nodes
    
    def calculate_translation(self):
        
        words=self.source_phrase.split()
        coverage_vector=self.create_coverage_vector(len(words))
        start_node=Node('',None,[0,0])
        start_node.last_history=['<s>']
        start_node.source_phrase=self.source_phrase.split()
        start_node.already_translated=coverage_vector
        just_for_test=self.generate_next_nodes(start_node)
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
        return self.destination_phrase
    
    def create_coverage_vector(self,number):
        array=[]
        for i in range(number):
            array.append(0)
        return array
    
    def calculate_translation_probability(self,position_to_translate,translation):
        """
        This method should be used only for calculating probabilities for future costs
        """
        
        phrase_pair=(' '.join(self.source_phrase[position_to_translate[0]:position_to_translate[1]+1]),translation)
        
        grade= math.log10(self.l1_given_source[phrase_pair])
        return grade
    
    def calculate_language_model_probability(self,history,translation):
        """
        This method should be used only for calculating probabilities for future costs
        IMPORTANT NOTE: assumption that translation length<=3
        """
        translation_array=translation.split()
        local_ngram=history[:]+translation_array
        while (len(local_ngram)>3):
            del local_ngram[0]
        
        result_backoff=calculate_stupid_backoff(local_ngram,self.language_model)
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
        
    

    def calculate_probability(self,language_model,l1_given_source,source_given_l1):
        phrase_pair=(' '.join(self.source_phrase[self.current_positions[0]:self.current_positions[1]+1]),self.current_position_translation)
        
        grade1= math.log10(l1_given_source[phrase_pair])
        grade2=math.log10(source_given_l1[phrase_pair])
        
        translation_array=self.current_position_translation.split()
        local_ngram=self.previous_node.last_history[:]+translation_array
        while (len(local_ngram)>3):
            del local_ngram[0]
        
        result_backoff=calculate_stupid_backoff(local_ngram,language_model)
        grade_language_model=math.log10(result_backoff)
        
        phrase_penalty=-1
        
        word_penalty=len(translation_array)
        
        previous_end=self.previous_node.current_positions[1]
        disortion=-1*math.fabs(self.current_positions[0]-previous_end-1)
        
        result=grade1+grade2+grade_language_model+phrase_penalty+word_penalty+disortion;
        self.probability=result+self.previous_node.probability;
        return result
    

            
            
         
        
        
