#this is a file on stacks 
#what are the applications? suppose you want to track the history of a browser, you can use a stack. 
#There are push and pop operations, also known as LIFO (last in first out) operations.
#The last element to be pushed is the first one to be popped.
#This is analagous to a stack of plates. 
#To search an element in a stack, it is O(n) time complexity. 



# s=[] 
# s.append('https://www.google.com')
# s.append('https://www.facebook.com')
# s.append('https://www.twitter.com')

# print(s) 
# print(s.pop())
# print(s.pop())
# print(s.pop())

#now what happens if i s.pop again?
# print(s.pop()) #this will give an error, because the stack is empty.
#the recommended way of using stack is deque from collections module.

from collections import deque
stack=deque()
# #let us see what methdos are available in deque
# print(dir(stack)) #this will show all the methods available in deque

stack.append('https://www.google.com')
stack.append('https://www.facebook.com')
print(stack)
print(stack.pop())

#Now i define a stack class, not really necessary, but just for practice.
class Stack:
    def __init__(self):
        self.container=deque()
    def push(self,val):
        self.container.append(val)
    def pop(self):
        return self.container.pop()
    def peek(self):
        return self.container[-1]
    def is_empty(self):
        return len(self.container)==0
    def size(self):
        return len(self.container)
        
  

#test
s=Stack()
s.push(5) 
s.push(6) 
print(s.pop()) 
print(s.pop())


#Exercise 1: Write a function in python that can reverse a string using stack data structure.  
#For example reverse_string("We will conquere COVID-19") should return "91-DIVOC ereuqnoc lliw eW"
 
# def reverse_string(string): 
#     s=Stack()
#     for i in string: 
#         s.push(i)
#     result=''
#     while s.size()!=0:
#         result+=s.pop()
#     return print(result)

# reverse_string("We will conquere COVID-19")
 
#Write a function in python that checks if paranthesis in the string are balanced or not. To be balanced, means that there is equal number of each parathensis. 
# Possible parantheses are "{}',"()" or "[]". 

#we will use the stack class 

# we will create one stack for each {, (, and [
# we will push the opening paranthesis into the stack
# we will pop the closing paranthesis from the stack
# if the stack is empty, then the paranthesis are balanced.

# def is_curly_brackets_balanced(string):
#     s=Stack()
#     for i in string:
#         if i=='{':
#             s.push(i)
#         elif i=='}':
#         #first check if the stack is empty
#             if s.is_empty():
#                 return False
#             #otherwise, pop the opening paranthesis
#             s.pop()
#     #if the stack is empty, then the paranthesis are balanced
#     return s.is_empty()

# #test
# print(is_curly_brackets_balanced("{{{}}}"))
# print(is_curly_brackets_balanced("{{{{}}"))

#however will only work for the curly brackets, we need to do the same for the other brackets 
# we will create three stacks all in one function

def is_balanced(string):
    s=Stack()
    #we will repeat the following code for each bracket type
    for i in string:
        if i=='(':
            s.push(i)
        elif i==')':
        #first check if the stack is empty
            if s.is_empty():
                return False
            #otherwise, pop the opening paranthesis
            s.pop()
    #now we will repeat above code for the bracket type []
    for i in string: 
        if i=='[':
            s.push(i)
        elif i==']':
            if s.is_empty():
                return False
            s.pop()
    #now we will repeat above code for the bracket type () 
    for i in string:
        if i =='(':
            s.push(i)
        elif i==')':
            if s.is_empty():
                return False
            s.pop()
    #if the stack is empty, then the paranthesis are balanced
    return s.is_empty()
#The time complexity for this algorithm seems to be 3N . Not so efficient , but oh well. 

#test 
print(is_balanced("{{{}}}"))
print(is_balanced("{{{{}}][[]]"))
print(is_balanced("))"))
print(is_balanced("[a+b]*(x+2y)*{gg+kk}"))