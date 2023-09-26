#This will code out the cut rod problem
# The main input is a list list of length n, where the ith element represents the price of a rod of length i.
# For example we have
p=[0,1,5]

#the lenght function will give the length of the list
n=3
print(p,n)
# Now we define a function that will return the maximum revenue that can be obtained by cutting up the rod and selling the pieces.
#This is the first go. If the rod is of length n, then we can cut it in n-1 ways, and we have to find the maximum of all these ways.
#This is a recursive function.



def cut_rod1(p,n):
    if n==0:
        return 0 #if the length of the rod is 0, then the revenue is 0.
    #initialize q for the money we can make by cutting the rod
    q = -1 #initialize q to -1, because we want to maximize the revenue.
    for i in range(0,n): #this will range from index 0 to n-1
        q = max(q,p[i]+cut_rod1(p,n-(i+1))) #this is the recursive call
    return q

#let us try this out on p1 
print(cut_rod1(p,n)) #this will give a recursion error, because the recursion depth is exceeded.

