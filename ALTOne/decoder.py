class Graph:

    source_phrase = ''
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
            n = nodes[n_id]
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
        node = nodes[node_id]
        nodes[node_id] = node 
        return 0

    def collapse_node(self, node_id):
        '''
        This method finds nodes equivalent to node and makes pointers to them
        Don't know if this should be in here, or maybe at the graph level?
        '''
        node = nodes[node_id]
        nodes[node_id] = node 
        return 0

class Node:
    previous_nodes=[]
    last_history=[]
    already_translated=[]
    current_positions=[]
    source_phrase=''
    current_position_translation=''
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

    def calculate_probability(self,language_model,l1_given_l2,l2_given_l2):
        phrase_pair=(current_position_translation, ' '.join(self.source_phrase[self.current_positions[0]:self.current__positions[1]]))
        grade1=l1_given_l2(phrase_pair)
        grade2=l2_given_l2(phrase_pair)
        grade_language_model=language_model(phrase_pair)
        phrase_penalty=-1
        word_penalty=0
        disortion=0
