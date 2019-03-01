import logging
from . import configData

class Automata(object):
    """
    Automata:
        is a self-operating machine, or a machine or control mechanism
        designed to automatically follow a predetermined sequence of
        operations, or respond to predetermined instructions...
    Wikipedia. (2003). Automaton. Retrieved 23 February, 2019, from: https://en.wikipedia.org/wiki/Automaton
    """

    __slots__ = ['alphabet', 'states', 'transitions', 'logger']

    def __init__(self, data):
        self.logger = logging.getLogger('Automata')
        self.loadConfigData(data)

    def __str__(self):
        alphabet = "\tAlphabet:\n\t\t{0}".format(self.alphabet)
        automata = "Automata:\n"
        return automata+alphabet+str(self.states)+str(self.transitions)

    def __repr__(self):
        return {
                    'alphabet'      :   self.alphabet,
                    'states'        :   repr(self.states),
                    'transitions'   :   repr(self.transitions)
                }

    def loadConfigData(self, data):
        self.logger.info( "Loading data..." )
        self.logger.debug( 'Data:\n'+str(data) )
        keys = ['alphabet', 'states', 'transitions']
        configData.validateStructure( keys, data, '<Automata>' )
        self.alphabet = list( data[ 'alphabet' ][0] )
        self.states = State( data )
        self.transitions = Transition(
                                        data[ 'transitions' ],
                                        self.alphabet,
                                        self.states
                                        )
        self.logger.debug("Loaded alphabet:"+str(self.alphabet))
        self.logger.debug("Loaded "+str(self.states))
        self.logger.debug("Loaded "+str(self.transitions))

    def getAlphabet(self):
        return self.alphabet

    def getStates(self):
        return self.states

    def getTransition(self):
        return self.transitions

    def restart(self):
        self.states.setCurrent( self.states.getStart()[0] )

    def evaluate(self, char):
        """
            Return the final state, None otherwise
        """
        self.logger.info('Evaluating character...')
        self.logger.debug('Character:\t'+str(char))

        from_state = self.states.getCurrent()

        if(char is None): #To-Other
            return self.getOther(char, from_state)

        letter_index = self.alphabet.index( char )
        state_index = self.states.index( from_state )
        self.logger.debug('Letter index:\t'+str(letter_index))
        self.logger.debug('State index:\t'+str(state_index))
        to_state = self.transitions[state_index][letter_index]
        self.logger.debug('Current state:\t'+str(from_state))
        self.logger.debug('Next state:\t'+str(to_state))

        if( to_state is None ):
            self.restart()
            candidates = self.getCandidateCharacters(state_index)
            error_msg = BadSequenceException.buildMessage(char, from_state, candidates)
            raise BadSequenceException(error_msg)
        else:
            self.states.setCurrent( to_state )

        return self.states.isFinal( to_state )

    def getCandidateCharacters(self, from_state):
        # Returns the following valid characters for the given state
        candidates = []
        for index, transition in enumerate(self.transitions[from_state]):
            if(transition is not None):
                candidates.append( self.alphabet[index] )

        return candidates

    def getOther(self, char, current_state):
        """
            Returns the "other-state".
            Other-state
                >Is the next-state (this next state most be a final-state)
                from the current state, given:
                    -No entry and at non start-state or final-state.
                >Characteristics:
                    -Different from the current state.
                    -It's the most repited state at the current-state row in the
                    transition-matrix
        """
        self.logger.info("Obtaining other-state...")

        state_index = self.states.index( current_state )
        state_row = list(self.transitions[state_index])
        self.logger.debug("Current-state row:\t"+str(state_row))

        while( current_state in state_row ):
            """
                Erase from the state-row all transitions that lead
                to the same row.
            """
            del state_row[state_row.index( current_state )]

        to_state = max(set(state_row), key=state_row.count)
        self.logger.debug("Other-state:\t"+str(to_state))

        if( to_state is not None):
            return to_state
        else:
            self.states.setCurrent( self.states.getStart()[0] )
            candidates = self.getCandidateCharacters(state_index)
            error_msg = BadSequenceException.buildMessage(char, current_state, candidates)
            raise BadSequenceException(error_msg)

class State(list):

    __slots__ = ['start', 'final', 'next_state', 'current']

    def __init__(self, data):
        self.loadConfigData(data)

    def __contains__(self, element):
        error_msg = "Value=%r, not in %r" %(element, self)
        if( not isinstance(element, list) ):
            if( list.__contains__(self, element) ):
                return True
            else:
                raise LookupError(error_msg)
        elif( isinstance(element, list) ):
            for item in element:
                if( not list.__contains__(self, item) ):
                    raise LookupError(error_msg)
            return True
        else:
            error_msg = "Unable to perform >__contains__< over object type: ".format(type(element))
            raise Exception(error_msg)

    def __str__(self):
        states = "States:\n\t{0}\n".format( list.__repr__(self) )
        start = "\tStart:\n\t\t{0}\n".format(self.start)
        final = "\tFinal:\n\t\t{0}\n".format(self.final)
        return states+start+final

    def __repr__(self):
        return {
                    'states':   self,
                    'start' :   self.start,
                    'final' :   self.final
                }

    def loadConfigData(self, data):
        keys= ['states', 'start_states', 'final_states']
        configData.validateStructure( keys, data, '<States>' )
        self._validateSets(
                                data[ 'states' ][0],
                                [
                                    data[ 'start_states' ][0],
                                    data[ 'final_states' ][0]
                                ]
                            )
        super().__init__( data[ 'states' ][0] )
        self.start = list( data[ 'start_states' ][0] )
        self.final =  list( data[ 'final_states' ][0] )
        self.current = self.start[0]
        self.next_state = None

    def _validateSets(self, super, sub):
        self._validateNoRepetition( sub )
        super = set(super)
        for element in sub:
            if( not set(element).issubset( super ) ):
                error_msg = "Set {0} must be a sub-set of {1} ".format(element, super)
                raise Exception(error_msg)

    def _validateNoRepetition(self, states):
        for element in states:
            if( len(element) != len( set(element) ) ):
                error_msg = f"Element {element} at {states}."
                raise RepeatedValueException( error_msg )

    def getStart(self):
        return self.start

    def getFinal(self):
        return self.final

    def setCurrent(self, state):
        self.current = state

    def getCurrent(self):
        return self.current

    def isFinal(self, state):
        if( state in self.final ):
            return state

class Transition(object):
    """
        -Matrix of rows*columns ( len(states)*len(alphabet) ).
        -This matrix defines the different available sequences to follow
        to reach a final-state from the start_state.
        -Maps a state machine.
    """

    def __init__(self, transitions, alphabet, states):
        self.loadTransitions(transitions, alphabet, states)

    def __str__(self):
        transitions = "Transitions:\n[\n"
        for row in self.table:
            transitions += "\t"+str(row)+"\n"
        transitions += "]\n"
        return transitions

    def __repr__(self):
        return self.table

    def shape(self):
        return (self.height, self.width)

    def __getitem__(self, key):
        return self.table[key]

    def loadTransitions(self, transitions, alphabet, states):
        self.height = len(states)
        self.width = len(alphabet)
        self.table = setUpMatrix(self.height, self.width, None)
        for transition_function in transitions:
            self._setTransition(transition_function, alphabet, states)

    def _setTransition(self, transition_function, alphabet, states):
        if( len(transition_function) <= self.width ):
            from_state = states.index(transition_function[0])
            with_letter = alphabet.index(transition_function[1])
            to_state = transition_function[2]
            self.table[from_state][with_letter] = to_state
        else:
            expected = "<from_state,with_letter,to_state>"
            error_message = "Expected {0} values found {1}".format(expected, transition_function)
            raise ValueError(error_message)

class BadSequenceException(Exception):
    def __init__(self, msg):
        self.message = msg

    def buildMessage(char, from_state, candidates):
        msg = f"For character={char} from state={from_state}"
        msg += " next_state=None."
        msg += f"\nExpecting one of {candidates}"
        return msg

class RepeatedValueException(Exception):
    def __init__(self, msg):
        self.message = msg

def setUpMatrix(height, width, init_value):
    matrix = [init_value]*height
    for i in range(height):
        matrix[i] = [init_value] * width
    return matrix
