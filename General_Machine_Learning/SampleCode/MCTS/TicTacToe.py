#Coding tictactoe
# AI that learns to play Tic Tac Toe using reinforcement learning. 


from copy import deepcopy 


#Tic Tac Toe board class
class Board(): 
    # create a constructor, a constructor is a special method that is called when an object is created. 
    def __init__(self, board=None): #the we allow to take a previous board as an argument. 
        self.player_x='x' 
        self.player_o='o' 
        self.empty_square='.' #empty square is a constant that we will define later.
        #define board position 
        self.position = {} 
        self.init_board() #initialize the board. 
        #if board is not empty, we will copy the board 
        if board is not None: 
            self.__dict__ = deepcopy(board.__dict__) #deepcopy creates a new object with the same value as the current object. 

    def init_board(self):
        for row in range(3): #over row 
            for col in range(3): #set every board position to empty 
                self.position[row,col]=self.empty_square #empty square is a constant that we will define later.
				
    def __str__(self):
        #define board string representation 
        board_str='' 
        #loop over board rows 
        for row in range(3):
            #loop over board columns 
            for col in range(3):
                board_str += '%s ' % self.position[row,col] #add the board position to the board string.
            board_str +='\n' 
        return board_str #return the board string representation. 
        
# main driver
if __name__ == '__main__':
    #create board instance 
    board=Board() 
    print(board) #print the board dictionary.