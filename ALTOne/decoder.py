from uuid import _last_timestamp
from gettext import _current_domain
class State:
    previous_nodes=[]
    last_history=[]
    already_translated=[]
    current_positions=[]
    source_phrase=''
    current_position_translation=''
    probability=0
    previous_cost=0

    def __init__(self,_source_phrase,_current_position_translation,_previous_node,_last_history,_already_translated,_current_positions,_cost):
        last_history=_last_history
        already_translated=_already_translated
        current_postions=_current_positions
        previous_node=_previous_node
        previous_cost=_cost
        current_position_translation=_current_position_translation
        source_phrase=_source_phrase  
    def calculate_probability(self,language_model,l1_given_l2,l2_given_l2):
        phrase_pair=(current_position_translation, ' '.join(source_phrase[current_positions[0]:current__positions[1]]))
        grade1=l1_given_l2(phrase_pair)
        grade2=l2_given_l2(phrase_pair)
        grade_language_model=language_model(phrase_pair)
        phrase_penalty=-1
        word_penalty=0
        disortion=0
            
            
        