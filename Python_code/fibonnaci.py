

#now this is a code for time complexity O(n^2) 
def nsquare(n):
    result = 0 
    for i in range(n): #this ranges for i from 0 to n-1
        #now we let j range from i to n-1
        for j in range(i,n): #this ranges for j from i to n-1
            result += 1
    return result 

#For n=2, nsquare(2) = 3, for general n, the formula is n(n+1)/2. 

print("The 5th square", nsquare(5)) #calling nsquare function

#this is code for generating fibonnaci seriesm time complexity O(2^n) 

def fib(n):
    if n==0:
        return 0
    elif n==1:
        return 1
    else: 
        return fib(n-1)+fib(n-2) #recursive call


#test  

# for i in range(5):
#     print(fib(i)) #calling fib function




print("Now we will do some dynamic programming to reduce the time complexity of the fibonnaci series")
     
    