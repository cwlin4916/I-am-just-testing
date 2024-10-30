import re
import collections

# Test out utf-8 encoding
test = 'reductive group over a finite field F_q, and N its maximal unipotent subgroup. V. Drinfeld has introduced a remarkable partial compactification of the moduli stack of N-bundles on a smooth projective curve X over F_q. In this paper we study Drinfeld'.split()  # Split the input into words
test_encoded = [list(map(int, word.encode('utf-8'))) for word in test]  # Convert each word into utf-8 encoded bytes

# This represents the raw bytes which is the utf-8 encoding of the string.
print("Encoded test words (in utf-8):", test_encoded)
# this is a list of list 
"""
Function to find the most common pair of symbols in the vocabulary.
"""

def get_stats(vocab):
    """
    vocab: List of lists, where each inner list is a list of utf-8 byte values for a word
    returns: a dictionary with the count of each adjacent pair of symbols in the vocabulary
    """
    counts = {}  # Use a regular dictionary instead of defaultdict

    for word in vocab:
        for i in range(len(word) - 1):
            pair = (word[i], word[i + 1])

            # Check if the pair is already in the dictionary
            if pair in counts:
                counts[pair] += 1  # Increment if it exists
            else:
                counts[pair] = 1  # Initialize with 1 if it doesn't exist

    return counts


# Get the most common pair of adjacent symbols
stats = get_stats(test_encoded)
# print("Most common pairs and their counts:", stats)
print(sorted(stats.items(), key=lambda x: x[1], reverse=True)) 


#let's look at the most common pair  these are 116, 105 
# which correspond to the utf-8 encoding of the word 'ti' 
# now let us iterate the whole vocabulary and replace all top occurences
top_pair = max(stats, key=stats.get) # Get the most common pair 
print(top_pair)

def merge(word, pair, idx):
    """
    word: List of bytes representing a single word
    pair: The pair of bytes to replace
    idx: The new byte value to use for replacement
    returns: A new word with the pairs replaced by the new value
    """
    new_word = []
    i = 0  # Index of the current word
    while i < len(word):
        # Check if current word has the pair
        if i < len(word) - 1 and word[i] == pair[0] and word[i + 1] == pair[1]:
            new_word.append(idx)  # Replace the pair with the new value
            i += 2  # Skip the next byte since it's part of the pair
        else:
            new_word.append(word[i])
            i += 1
    return new_word

def merge_vocab(vocab, pair, idx): # now we will apply the merge function to all words in the vocabulary
    """
    vocab: list of lists, where each inner list is a list of utf-8 byte values for a word
    pair: The pair of bytes to replace
    idx: The new byte value to use for replacement
    returns: A new vocabulary with the pairs replaced by the new value
	"""
    new_vocab=[]
    for word in vocab:
        new_word = merge(word, pair, idx)
        new_vocab.append(new_word)
    return new_vocab

# Apply the merge function to all words in the vocabulary
new_test_encoded = merge_vocab(test_encoded, top_pair, len(test_encoded))
print("Before merging:", test_encoded)
print("After merging:", new_test_encoded)
