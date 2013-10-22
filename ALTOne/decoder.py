import sys

def translate(language1,l1_given_l2,l2_given_l1,ngrams_prob):
    language1 = open(language1, 'r')
    num_lines = number_of_lines(language1)
    beam_width=5
    for i, oneLine in enumerate(language1):
        if num_lines>100:
            if  i % (num_lines/100) is 0:
                sys.stdout.write('\r%d%%' % (i*100/num_lines,))
                sys.stdout.flush()
        sentences=oneLine.split('.')
        for sentence in sentences:
            grapth=Graph(sentence,beam_width)
            
                
                
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

    source_phrase = ''
    destination_phrase=''
    beam_width = 0
    nodes = []
    node_map = {} #maps indexes from nodes to their parents (sort of like pointers I guess?)
    equiv_nodes = {} #maps the best node to its equivalents
    expanded = True #This shows if the graph can still be expanded
    

    def __init__(self, source_phrase, beam_width):
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
        self.nodes[node_id] = node 
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
    
    def calculate_translation(self):
        return self.destination_phrase

class Node:
    previous_nodes=[]#links to thimport syse previous nodes
    last_history=[] #last n-1 words in history 
    already_translated=[]#  numbers of words which were translated- coverage vector
    current_positions=[] #numbers of word in the sentence which are currently translated
    source_phrase='' #the whole source sentence
    current_position_translation='' #currently translated position
    probability=0
    previous_cost=0
    stopped = False #this is to see if we should expand the node or not
    collapsed = False #difference with the prev one is that paths can go through this on the way back

    def __init__(self,_source_phrase,_current_position_translation,_previous_node,_last_history,_already_translated,_current_positions,_cost):
        self.last_history=_last_history
        self.already_translated=_already_translated
        self.current_postions=_current_positions
        self.previous_node=_previous_node
        self.previous_cost=_cost
        self.current_position_translation=_current_position_translation
        self.source_phrase=_source_phrase  

    def calculate_probability(self,language_model,l1_given_l2,l2_given_l2,translation):
        phrase_pair=(self.current_position_translation, ' '.join(self.source_phrase[self.current_positions[0]:self.current__positions[1]]))
        grade1=l1_given_l2(phrase_pair)
        grade2=l2_given_l2(phrase_pair)
        grade_language_model=language_model(phrase_pair)
        phrase_penalty=-1
        word_penalty=0
        disortion=0
        result=grade1+grade2+grade_language_model+phrase_penalty+word_penalty+disortion;
        self.probability=result;
        
        
        
