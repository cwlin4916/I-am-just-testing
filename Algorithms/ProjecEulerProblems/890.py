"""
The problem is to see how many ways we can write a number n as a sum of powers of 2s, ignoring order 2. 
We denote this function p(n)
For example, p(7) = 6, we list the sums below 
1 + 1 + 1 + 1 + 1 + 1 + 1
2 + 1 + 1 + 1 + 1 + 1
2 + 2 + 1 + 1 + 1
2 + 2 + 2 + 1 
4 + 1 + 1 + 1
4 + 2 + 1
Therefore, p(7) = 6 
Let task is to find p(7^111) mod 10^9 + 7 
We are given that p(7^7) = 144548435 mod 10^9 + 7 
"""

"""
The solution is a dynamic programming approach.  We will define a function p(m,k) 
where p(m,k) is the number of ways we can write m as a sum of powers of 2s, where the largest power of 2 is 2^k. 
We will define p(m,k) recursively. We will allow m,k to be negative integers. 
Below is the base case: 
If m=0, k>=0 then p(m,k)=1, there is only one way to write 0. 
if m>=0, k=0, then p(m,k)=1 since the largest power of 2 is 2^0=1 
If m<0, k<0, then p(m,k)=0 since we cannot write a negative number as a sum of powers of 2s 
The recursive formula is then 
p(m,k) = p(m-2^k,k) + p(m,k-1) , provided m>=2^k, so this guarantees our case only requires positive integers.
"""
# we initialize a dictionary to store the values of p(m,k) 
# we also initialize the base cases 

MOD  = 10**9 + 7 

# def p(n):
#     # determine the maximal length k such that 2^k <= n 
#     max_k = n.bit_length() - 1 
    
#     #create a 2d dp table with with (n+1)rows and (max_k+1) columns
#     dp = [[0]*(max_k+1) for _ in range(n+1)] 
#     #initialize base cases 
#     for k in range(max_k+1):
#         dp[0][k]=1
#     for m in range(n+1):
#         dp[m][0]=1 #p(m,0)=1 for all m>=0
#     #fill in the dp table
#     for k in range(1,max_k+1):
#         power_of_two =2**k
#         for m in range(1,n+1):
#             if m>=power_of_two:
#                 dp[m][k] = (dp[m-power_of_two][k] + dp[m][k-1])%MOD
#             else:
#                 dp[m][k]=dp[m][k-1] 
#     return dp[n][max_k]

# n=7**(7*3)
# result = print(f"p({n}) = {p(n)}")
MOD = 10**9 + 7

def partition_count(n):
    if n < 2:
        return 1
    
    # Find largest power of two not exceeding n
    h = n // 2
    k = 1
    while k <= h:
        k <<= 1
    
    # Initialize the coefficient array
    arr = [0] * (n + 1)
    arr[0] = 1  # Base case: only one way to sum to 0 (using no numbers)
    
    # Main loop: decrementing k through powers of two
    while k:
        for i in range(k, n + 1):
            arr[i] = (arr[i] + arr[i - k]) % MOD
        k //= 2
    
    return arr[n]

# Example usage:

# Example usage:
n = 7**8 # You can change this to test with other values
result = partition_count(n)
print(f"Number of partitions for {n} as sums of powers of two: {result}")
