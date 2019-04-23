from collections import defaultdict

# TuringMachine class represents our Turing machinedd


class TuringMachine:

    # Action class represents the action that can be taken in any step of
    # the execution of Turing machine
    class Action:

        # Action consists of:
        #
        # - self.turing_machine is a reference to the Turing machine this action
        #   takes place on. Action can change the state of the machine,
        #   so it needs to be aware of the machine.
        #
        # - self.write is a character with which the character at the position
        #   to which head points to should be replaced (character to write as a
        #   result of this action)
        #
        # - self.direction is an integer (1, 0 or -1) that indicates
        #   the direction in which we should move the head after replacing
        #   the character that the head points to
        #
        # - self.new_state is an integer indicating the number of the state
        #   to which machine should transition to as a result of this action
        def __init__(self, turing_machine, write, direction, new_state):
            self.turing_machine = turing_machine
            self.write = write
            self.direction = direction
            self.new_state = new_state

        # This method implements the procedure that takes place when the action
        # is taken. As the definition of Turing machine describes, action
        # consists of 3 steps:
        # - Replace the character that the head points to
        # - Move the head in the appropriate direction (or don't move it at all)
        # - Change the current state of the Turing machine to a new appropriate
        #   state
        def take_action(self):
            # Replacing the character with self.write character
            # *** HAPPENS ONLY IF self.write ISN'T * (* means DON'T WRITE) ***
            if self.write != "*":
                self.turing_machine.tape_contents[self.turing_machine.head] = self.write

            # Moving the head - self.direction 1 will move it right, -1 left and
            # 0 will keep it at the same position
            self.turing_machine.head += self.direction

            # Moving the head can result in head becoming -1 (if head was
            # pointing to the first character of tape contents list
            # (head was 0) and was moved to the left.
            # If this is the case, we want to expand the content of the tape
            # that we are keeping track of. Since the tape is infinite
            # and blank symbols (-) are written all over the place we're not
            # keeping track of yet, once we start to keep track of this spot,
            # initially it's going to be filled with -. So our new content
            # consists of -<old_content>, which means we just have to append -
            # to the beginning of our tape_content list, and now we consider
            # head 0 again (since it points to the first element of our
            # content list
            if self.turing_machine.head < 0:
                self.turing_machine.tape_contents = ["-"] + self.turing_machine.tape_contents
                self.turing_machine.head = 0
            # Moving the head right can result in head pointing to the position
            # that is to the right of the last character we are keeping track of
            # We need to include this character in the tape content we are
            # keeping track of as well, so we need to append it to our
            # tape_contents list. Since we haven't kept track of it previously,
            # it's filled with blank symbol ("-") so this is what we append
            elif self.turing_machine.head >= len(self.turing_machine.tape_contents):
                self.turing_machine.tape_contents.append("-")

            # Lastly, we change the state of the Turing machine to the new
            # state specified by this action
            self.turing_machine.state = self.new_state

    # Constructor of TuringMachine class.
    # What we need to keep track of in a machine:
    # - self.head - the position to which the head points to
    # - self.state - the current state of the machine
    # - self.halt_state - the halt state - state of the machine which indicates
    #   that the execution of the machine should stop (end state)
    # - tape_contents - a list of characters representing the part of (infinite)
    #   machine tape that we keep track of. The rest of the tape (that we aren't
    #   keeping track of) consists of blank symbols (-)
    # - self.action_table - The action table of this state machine.
    #   It is a dictionary (hash table) with possible machine states as keys
    #   and for every state we keep another dictionary (so this is dictionary
    #   of dictionaries). The second dictionary keeps track of actions that
    #   should be taken for each possible read character, so it has read
    #   characters as keys and corresponding actions as values
    #
    #   defaultdict is used because it automatically adds a (key, value)
    #   pair when we access the key for the first time, so we don't have to
    #   care about creating an empty dictionary before adding the first element
    #   for each machine state. Otherwise, usage of defaultdict is the same
    #   as of dict.
    def __init__(self):
        self.head = 0
        self.state = 0
        self.halt_state = 0
        self.tape_contents = []
        self.action_table = defaultdict(dict)

    # This method parses the machine definition from the file with name filename
    # Returns a success flag:
    # - True if the whole parsing was successful
    # - False if there's been an error in any step of parsing (meaning file
    #   isn't correctly formatted)
    def read_machine(self, filename):
        # We read the whole file content into a list of lines
        with open(filename, "r") as f:
            lines = f.read().splitlines()

        # Correct input file has at least first 4 lines:
        # <Starting contents of tape>
        # <Starting offset of machine head>
        # <Start state index (integer)>
        # <Halting state index (integer)>
        # If this isn't a case, stop parsing and return error flag
        if len(lines) < 4:
            return False

        try:
            # First line is <Starting contents of tape>
            self.tape_contents = list(lines[0])
            # Second line is <Starting offset of machine head>
            self.head = int(lines[1])
            # Third line is <Start state index (integer)>
            self.state = int(lines[2])
            # Fourth line is <Halting state index (integer)>
            self.halt_state = int(lines[3])

            # All the other lines, beginning from fifth line (index 4)
            # are <Action table>
            for i in range(4, len(lines)):
                # Each Action line is in this form:
                # <State index> <Read> <Write> <Direction> <New state index>
                # Let's make a list (called line) with these 5 values
                # (we have to split our line using the space as a delimiter)
                # So now,
                # <State index> is in line[0]
                # <Read> is in line[1]
                # <Write> is in line[2]
                # <Direction> is in line[3]
                # <New state index> is in line[4]
                # but they are all strings, so when we need integers
                # (like for Direction or State index), we need to convert them
                # to int with e.g. int(line[3]). If there's an error in file,
                # and these strings cannot be converted to int, conversion
                # methods throw ValueError exceptions (thus this is all done
                # in try block)

                line = lines[i].split(' ')

                # If we didn't get all of our 5 needed values, return error flag
                if len(line) < 5:
                    return False

                # If we didn't get a SINGLE character for <Read> OR
                # if we didn't get a SINGLE character for <Write> OR
                # if we got a direction that's not -1, 0 or 1
                # it's an error, so just stop parsing and return error flag
                if len(line[1]) > 1 or len(line[2]) > 1 or abs(int(line[3])) > 1:
                    return False

                # If all is right, add an entry to our action table
                # In our action_table, using the key <State> (line[0])
                # to access the dictionary of Actions, and using the key
                # <Read> for that dictionary, add a new Action given <Write>
                # character, <Direction> integer and <New state index> integer
                self.action_table[int(line[0])][line[1]] =\
                    TuringMachine.Action(self, line[2], int(line[3]), int(line[4]))
        except ValueError:
            # If there was any conversion error, return error flag
            return False
        else:
            # If everything was OK, return True
            return True

    # This method executes the Turing machine after the starting
    # state, halt state, starting tape contents, starting head position have
    # been set and action table filled with appropriate actions
    #
    # This method returns a list of strings, where each string
    # represents characters on tape that we are currently keeping track of
    # (which are in self.tape_contents list), so it returns a list
    # of tape contents in each step of execution until the halt state is reached
    # If an error is detected during execution, the method returns None instead
    def execute(self):
        # Add the starting tape contents to the resulting list of tape contents
        all_tape_contents = ["".join(self.tape_contents)]

        # Execute the machine - while the state doesn't become halt state
        while self.state != self.halt_state:
            # If the current state is not in our action table (we reached
            # an "impossible state" for some reason, stop the execution and
            # return None
            if self.state not in self.action_table:
                return None
            # If the exact character that our head points to is in our action
            # table for the current state, keep it in a read variable
            if self.tape_contents[self.head] in self.action_table[self.state]:
                read = self.tape_contents[self.head]
            # If there isn't the exact read character, maybe there's a wild-card
            # character (*). If so, keep it in read for later
            elif "*" in self.action_table[self.state]:
                read = "*"
            # If there isn't an action for the character we read from head
            # position, we don't know what to do at this point, so just
            # stop the execution and return None
            else:
                return None

            # If everything was OK, variable read keeps track of the place
            # in dictionary where we should look for our action
            # Access the action and take it!
            self.action_table[self.state][read].take_action()

            # Finally, since the action put us in a new state and (most likely)
            # changed the tape content, we have to save it in our list
            # of contents in all steps.
            # Since we're keeping track of tape contents in a list of characters
            # we want to convert it to string first. join method does that, and
            # "".join(...) tells join not to add any character in between (thus
            # empty string "")
            all_tape_contents.append("".join(self.tape_contents))

        return all_tape_contents


