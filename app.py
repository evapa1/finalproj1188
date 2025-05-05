from flask import Flask, render_template, request, jsonify, redirect, url_for, session

import random
import datetime
import hashlib

# Define a list of reflection prompts
reflection_prompts = [
    "What would you do differently next time?",
    "Where did the AI outperform you?",
    "What was the most challenging part of this problem?",
    "What did you learn from solving this problem?",
    "How could you optimize your solution further?",
    "What problem-solving strategy worked best for you here?",
    "Did you notice any patterns that could help with future problems?",
    "How does your approach compare to the AI solution?",
    "What was your 'aha!' moment when solving this problem?",
    "If you had to explain this solution to someone else, what would you emphasize?"
]

app = Flask(__name__)
app.secret_key = 'ai_vs_coder_secret_key'  # Required for session

# Initialize global variables
current_question = None
current_difficulty = 1
used_questions = set()
total_attempts = 3
attempts_left = total_attempts
question_attempts = {}  # Track attempts per question


questions = [
    # Easy questions (difficulty: 1) - 40 questions
    {"prompt": "Add two numbers.", 
     "test_cases": [(1, 2, 3), (5, 7, 12)], 
     "ai_solution": "def add(a, b):\n    return a + b", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the + operator to add the two input numbers together."},
     
    {"prompt": "Return true if number is even, false if number is odd.", 
     "test_cases": [(2, True), (3, False)], 
     "ai_solution": "def is_even(n):\n    return n % 2 == 0", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the modulo operator (%) to check if a number is divisible by 2."},
     
    {"prompt": "Return the maximum of two numbers.", 
     "test_cases": [(3, 7, 7), (10, 2, 10)], 
     "ai_solution": "def maximum(a, b):\n    return max(a, b)", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use Python's built-in max() function to find the larger of two values."},
     
    {"prompt": "Return the length of a string.", 
     "test_cases": [("hello", 5), ("", 0)], 
     "ai_solution": "def str_length(s):\n    return len(s)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use Python's len() function to get the length of a string."},
     
    {"prompt": "Check if a string is a palindrome.", 
     "test_cases": [("racecar", True), ("hello", False)], 
     "ai_solution": "def is_palindrome(s):\n    return s == s[::-1]", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Compare the string with its reverse. You can reverse a string using s[::-1]."},
     
    {"prompt": "Return the first element of a list.", 
     "test_cases": [([1,2,3], 1), ([5], 5)], 
     "ai_solution": "def first_element(lst):\n    return lst[0]", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use indexing with [0] to access the first element of a list."},
     
    {"prompt": "Return the last element of a list.", 
     "test_cases": [([1,2,3], 3), ([5], 5)], 
     "ai_solution": "def last_element(lst):\n    return lst[-1]", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use indexing with [-1] to access the last element of a list."},
     
    {"prompt": "Find the sum of a list.", 
     "test_cases": [([1,2,3], 6), ([5,5,5], 15)], 
     "ai_solution": "def list_sum(lst):\n    return sum(lst)", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use Python's sum() function to add all elements in a list."},
     
    {"prompt": "Return True if a list is empty.", 
     "test_cases": [([], True), ([1], False)], 
     "ai_solution": "def is_empty(lst):\n    return len(lst) == 0", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Check if the length of the list is zero using len()."},
     
    {"prompt": "Double every number in a list.", 
     "test_cases": [([1,2,3], [2,4,6]), ([5], [10])], 
     "ai_solution": "def double_list(lst):\n    return [x*2 for x in lst]", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use a list comprehension to multiply each element by 2."},
     
    {"prompt": "Return the lowercase version of a string.", 
     "test_cases": [("HELLO", "hello"), ("Test", "test")], 
     "ai_solution": "def to_lowercase(s):\n    return s.lower()", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the lower() method to convert a string to lowercase."},
     
    {"prompt": "Count the number of words in a string.", 
     "test_cases": [("hello world", 2), ("one two three", 3)], 
     "ai_solution": "def count_words(s):\n    return len(s.split())", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Split the string by spaces and count the resulting list elements."},
     
    {"prompt": "Repeat a string n times.", 
     "test_cases": [("ha", 3, "hahaha"), ("yes", 2, "yesyes")], 
     "ai_solution": "def repeat_string(s, n):\n    return s * n", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the * operator to repeat a string."},
     
    {"prompt": "Return the absolute value of a number.", 
     "test_cases": [(-5, 5), (7, 7)], 
     "ai_solution": "def absolute_value(n):\n    return abs(n)", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use Python's abs() function to get the absolute value."},
     
    {"prompt": "Multiply two numbers.", 
     "test_cases": [(2, 3, 6), (5, 5, 25)], 
     "ai_solution": "def multiply(a, b):\n    return a * b", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the * operator to multiply the two input numbers together."},
     
    {"prompt": "Divide two numbers.", 
     "test_cases": [(10, 2, 5), (15, 3, 5)], 
     "ai_solution": "def divide(a, b):\n    return a / b", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the / operator to divide the first number by the second."},
     
    {"prompt": "Calculate the remainder when dividing two numbers.", 
     "test_cases": [(10, 3, 1), (15, 4, 3)], 
     "ai_solution": "def remainder(a, b):\n    return a % b", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the % (modulo) operator to find the remainder."},
     
    {"prompt": "Return the square of a number.", 
     "test_cases": [(2, 4), (5, 25)], 
     "ai_solution": "def square(n):\n    return n * n", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Multiply the number by itself."},
     
    {"prompt": "Return the cube of a number.", 
     "test_cases": [(2, 8), (3, 27)], 
     "ai_solution": "def cube(n):\n    return n ** 3", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the ** operator to raise the number to the power of 3."},
     
    {"prompt": "Convert a string to uppercase.", 
     "test_cases": [("hello", "HELLO"), ("Test", "TEST")], 
     "ai_solution": "def to_uppercase(s):\n    return s.upper()", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the upper() method to convert a string to uppercase."},
     
    {"prompt": "Check if a string starts with a specific substring.", 
     "test_cases": [("hello world", "hello", True), ("python code", "java", False)], 
     "ai_solution": "def starts_with(s, prefix):\n    return s.startswith(prefix)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the startswith() method to check if a string starts with a specific prefix."},
     
    {"prompt": "Check if a string ends with a specific substring.", 
     "test_cases": [("hello world", "world", True), ("python code", "java", False)], 
     "ai_solution": "def ends_with(s, suffix):\n    return s.endswith(suffix)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the endswith() method to check if a string ends with a specific suffix."},
     
    {"prompt": "Return the character at a specific index in a string.", 
     "test_cases": [("hello", 1, "e"), ("python", 0, "p")], 
     "ai_solution": "def char_at(s, index):\n    return s[index]", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use indexing with [] to access a specific character in a string."},
     
    {"prompt": "Count the occurrences of a character in a string.", 
     "test_cases": [("hello", "l", 2), ("banana", "a", 3)], 
     "ai_solution": "def count_char(s, char):\n    return s.count(char)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the count() method to count occurrences of a character in a string."},
     
    {"prompt": "Replace a substring in a string.", 
     "test_cases": [("hello world", "world", "python", "hello python"), ("I like cats", "cats", "dogs", "I like dogs")], 
     "ai_solution": "def replace_substring(s, old, new):\n    return s.replace(old, new)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the replace() method to substitute one substring with another."},
     
    {"prompt": "Find the average of a list of numbers.", 
     "test_cases": [([1, 2, 3], 2), ([5, 10, 15, 20], 12.5)], 
     "ai_solution": "def average(lst):\n    return sum(lst) / len(lst)", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Divide the sum of all elements by the number of elements."},
     
    {"prompt": "Find the minimum value in a list.", 
     "test_cases": [([3, 1, 4, 2], 1), ([7, 5, 9], 5)], 
     "ai_solution": "def min_value(lst):\n    return min(lst)", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use Python's built-in min() function to find the smallest value."},
     
    {"prompt": "Find the maximum value in a list.", 
     "test_cases": [([3, 1, 4, 2], 4), ([7, 5, 9], 9)], 
     "ai_solution": "def max_value(lst):\n    return max(lst)", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use Python's built-in max() function to find the largest value."},
     
    {"prompt": "Count the occurrences of an element in a list.", 
     "test_cases": [([1, 2, 2, 3, 2], 2, 3), ([5, 5, 5], 5, 3)], 
     "ai_solution": "def count_element(lst, element):\n    return lst.count(element)", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use the count() method to count occurrences of an element in a list."},
     
    {"prompt": "Check if an element exists in a list.", 
     "test_cases": [([1, 2, 3], 2, True), ([4, 5, 6], 7, False)], 
     "ai_solution": "def contains(lst, element):\n    return element in lst", 
     "difficulty": 1, 
     "type": "list",
     "hint": "Use the 'in' operator to check if an element is in a list."},
     
    {"prompt": "Reverse a string.", 
     "test_cases": [("hello", "olleh"), ("python", "nohtyp")], 
     "ai_solution": "def reverse_string(s):\n    return s[::-1]", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use string slicing with a negative step to reverse a string."},
     
    {"prompt": "Join a list of strings with a separator.", 
     "test_cases": [(["hello", "world"], "-", "hello-world"), (["a", "b", "c"], ":", "a:b:c")], 
     "ai_solution": "def join_strings(lst, separator):\n    return separator.join(lst)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the join() method to concatenate strings with a separator."},
     
    {"prompt": "Split a string by a delimiter.", 
     "test_cases": [("hello-world", "-", ["hello", "world"]), ("a:b:c", ":", ["a", "b", "c"])], 
     "ai_solution": "def split_string(s, delimiter):\n    return s.split(delimiter)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the split() method to divide a string into a list of substrings."},
     
    {"prompt": "Remove whitespace from the beginning and end of a string.", 
     "test_cases": [("  hello  ", "hello"), ("\tpython\n", "python")], 
     "ai_solution": "def trim_string(s):\n    return s.strip()", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the strip() method to remove leading and trailing whitespace."},
     
    {"prompt": "Check if a number is positive.", 
     "test_cases": [(5, True), (-3, False), (0, False)], 
     "ai_solution": "def is_positive(n):\n    return n > 0", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Check if the number is greater than zero."},
     
    {"prompt": "Check if a number is negative.", 
     "test_cases": [(-5, True), (3, False), (0, False)], 
     "ai_solution": "def is_negative(n):\n    return n < 0", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Check if the number is less than zero."},
     
    {"prompt": "Check if a number is zero.", 
     "test_cases": [(0, True), (5, False), (-5, False)], 
     "ai_solution": "def is_zero(n):\n    return n == 0", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Check if the number equals zero."},
     
    {"prompt": "Return the opposite of a boolean value.", 
     "test_cases": [(True, False), (False, True)], 
     "ai_solution": "def negate(b):\n    return not b", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the 'not' operator to invert a boolean value."},
     
    {"prompt": "Check if both boolean values are True.", 
     "test_cases": [(True, True, True), (True, False, False), (False, False, False)], 
     "ai_solution": "def logical_and(a, b):\n    return a and b", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the 'and' operator to check if both values are True."},
     
    {"prompt": "Check if at least one boolean value is True.", 
     "test_cases": [(True, True, True), (True, False, True), (False, False, False)], 
     "ai_solution": "def logical_or(a, b):\n    return a or b", 
     "difficulty": 1, 
     "type": "math",
     "hint": "Use the 'or' operator to check if at least one value is True."},
     
    {"prompt": "Convert a number to a string.", 
     "test_cases": [(123, "123"), (0, "0")], 
     "ai_solution": "def number_to_string(n):\n    return str(n)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the str() function to convert a number to a string."},
     
    {"prompt": "Convert a string to an integer.", 
     "test_cases": [("123", 123), ("0", 0)], 
     "ai_solution": "def string_to_int(s):\n    return int(s)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the int() function to convert a string to an integer."},
     
    {"prompt": "Convert a string to a float.", 
     "test_cases": [("3.14", 3.14), ("0.0", 0.0)], 
     "ai_solution": "def string_to_float(s):\n    return float(s)", 
     "difficulty": 1, 
     "type": "string",
     "hint": "Use the float() function to convert a string to a floating-point number."},
     
   # Medium questions (difficulty: 2) - 34 questions
    {"prompt": "Find the second largest number in a list.", 
    "test_cases": [([1,2,3,4],3), ([10,9,8,7],9)], 
    "ai_solution": "def second_largest(lst):\n    return sorted(lst)[-2]", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Sort the list and access the second-to-last element."},
    
    {"prompt": "Return True if two strings are anagrams.", 
    "test_cases": [("listen","silent",True), ("hello","world",False)], 
    "ai_solution": "def is_anagram(a,b):\n    return sorted(a)==sorted(b)", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Sort both strings and compare them. Anagrams will have the same characters in a different order."},
    
    {"prompt": "Return the n-th Fibonacci number.", 
    "test_cases": [(5,5), (7,13)], 
    "ai_solution": "def fib(n):\n    a,b=0,1\n    for _ in range(n):\n        a,b=b,a+b\n    return a", 
    "difficulty": 2, 
    "type": "recursion",
    "hint": "Use an iterative approach with two variables to track the current and previous Fibonacci numbers."},
    
    {"prompt": "Count the number of prime numbers less than n.", 
    "test_cases": [(10,4), (20,8)], 
    "ai_solution": "def count_primes(n):\n    primes=[]\n    for num in range(2,n):\n        if all(num%p!=0 for p in primes):\n            primes.append(num)\n    return len(primes)", 
    "difficulty": 2, 
    "type": "math",
    "hint": "Check each number from 2 to n-1. A number is prime if it's not divisible by any previously found prime."},
    
    {"prompt": "Return True if a list is sorted in ascending order.", 
    "test_cases": [([1,2,3],True), ([3,2,1],False)], 
    "ai_solution": "def is_sorted(lst):\n    return lst==sorted(lst)", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Compare the original list with its sorted version."},
    
    {"prompt": "Reverse a linked list represented as a list.", 
    "test_cases": [([1,2,3],[3,2,1]), ([5,6],[6,5])], 
    "ai_solution": "def reverse_linked_list(lst):\n    return lst[::-1]", 
    "difficulty": 2, 
    "type": "data_structures",
    "hint": "Use list slicing with a negative step to reverse the list."},
    
    {"prompt": "Return the common elements in two lists.", 
    "test_cases": [([1,2,3],[2,3,4],[2,3]), ([5,6],[7,8],[])], 
    "ai_solution": "def common_elements(a,b):\n    return list(set(a)&set(b))", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Convert both lists to sets and use the intersection operator (&)."},
    
    {"prompt": "Rotate a list right by k steps.", 
    "test_cases": [([1,2,3,4],1,[4,1,2,3]), ([5,6,7],2,[6,7,5])], 
    "ai_solution": "def rotate_right(lst,k):\n    k%=len(lst)\n    return lst[-k:]+lst[:-k]", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Use list slicing to split and recombine the list. Remember to handle k > len(lst)."},
    
    {"prompt": "Return the intersection of two strings (common characters).", 
    "test_cases": [("abc","bcd","bc"), ("hello","world","lo")], 
    "ai_solution": "def string_intersection(a,b):\n    return ''.join(sorted(set(a)&set(b)))", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Convert both strings to sets, find their intersection, and join the result."},
    
    {"prompt": "Return the sum of digits of a number recursively.", 
    "test_cases": [(123,6),(999,27)], 
    "ai_solution": "def sum_digits(n):\n    return n if n<10 else n%10+sum_digits(n//10)", 
    "difficulty": 2, 
    "type": "recursion",
    "hint": "Add the last digit to the sum of the remaining digits. Use modulo and integer division."},
    
    {"prompt": "Merge two sorted lists into one sorted list.", 
    "test_cases": [([1,3,5],[2,4,6],[1,2,3,4,5,6]), ([5],[1,2,3,4,5],[1,2,3,4,5,5])], 
    "ai_solution": "def merge_sorted(a,b):\n    return sorted(a+b)", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Combine the lists and sort the result, or implement a merge algorithm."},
    
    {"prompt": "Return the longest word in a string.", 
    "test_cases": [("hi hello world","hello"),("one two","one")], 
    "ai_solution": "def longest_word(s):\n    return max(s.split(), key=len)", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Split the string into words and find the one with maximum length."},
    
    {"prompt": "Return True if a string is a subsequence of another.", 
    "test_cases": [("abc","ahbgdc",True),("axc","ahbgdc",False)], 
    "ai_solution": "def is_subsequence(s,t):\n    it=iter(t)\n    return all(c in it for c in s)", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Use an iterator to maintain order while checking if each character exists in sequence."},
    
    {"prompt": "Find all pairs in a list that sum to a target value.", 
    "test_cases": [([1,2,3,4,5], 6, [[1,5],[2,4]]), ([3,1,4,2], 5, [[1,4],[2,3]])], 
    "ai_solution": "def find_pairs(lst, target):\n    pairs = []\n    seen = set()\n    for num in lst:\n        if target - num in seen:\n            pairs.append(sorted([num, target - num]))\n        seen.add(num)\n    return sorted(pairs)", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Use a set to keep track of numbers you've seen and check for complements."},
    
    {"prompt": "Check if a number is a power of two.", 
    "test_cases": [(1, True), (16, True), (10, False)], 
    "ai_solution": "def is_power_of_two(n):\n    return n > 0 and (n & (n-1)) == 0", 
    "difficulty": 2, 
    "type": "math",
    "hint": "A power of two has only one bit set in its binary representation."},
    
    {"prompt": "Find the missing number in a sequence from 0 to n.", 
    "test_cases": [([3,0,1], 2), ([9,6,4,2,3,5,7,0,1], 8)], 
    "ai_solution": "def missing_number(nums):\n    n = len(nums)\n    return n * (n + 1) // 2 - sum(nums)", 
    "difficulty": 2, 
    "type": "math",
    "hint": "Use the formula for the sum of first n natural numbers and subtract the sum of the array."},
    
    {"prompt": "Implement a queue using two stacks.", 
    "test_cases": [(["push 1", "push 2", "pop", "push 3", "pop"], [1, 2])], 
    "ai_solution": "class Queue:\n    def __init__(self):\n        self.stack1 = []\n        self.stack2 = []\n    \n    def push(self, x):\n        self.stack1.append(x)\n    \n    def pop(self):\n        if not self.stack2:\n            while self.stack1:\n                self.stack2.append(self.stack1.pop())\n        return self.stack2.pop() if self.stack2 else None", 
    "difficulty": 2, 
    "type": "data_structures",
    "hint": "Use one stack for enqueue operations and another for dequeue operations."},
    
    {"prompt": "Implement a stack using two queues.", 
    "test_cases": [(["push 1", "push 2", "pop", "push 3", "pop"], [2, 3])], 
    "ai_solution": "from collections import deque\n\nclass Stack:\n    def __init__(self):\n        self.q1 = deque()\n        self.q2 = deque()\n    \n    def push(self, x):\n        self.q1.append(x)\n    \n    def pop(self):\n        if not self.q1:\n            return None\n        while len(self.q1) > 1:\n            self.q2.append(self.q1.popleft())\n        result = self.q1.popleft()\n        self.q1, self.q2 = self.q2, self.q1\n        return result", 
    "difficulty": 2, 
    "type": "data_structures",
    "hint": "Make push operation O(1) and pop operation O(n) by moving elements between queues."},
    
    {"prompt": "Find the first non-repeating character in a string.", 
    "test_cases": [("leetcode", "l"), ("loveleetcode", "v"), ("aabb", "")], 
    "ai_solution": "def first_unique_char(s):\n    from collections import Counter\n    counts = Counter(s)\n    for char in s:\n        if counts[char] == 1:\n            return char\n    return \"\"", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Count the occurrences of each character, then find the first one with count 1."},
    
    {"prompt": "Check if a string can be rearranged to form a palindrome.", 
    "test_cases": [("racecar", True), ("hello", False), ("aab", True)], 
    "ai_solution": "def can_form_palindrome(s):\n    from collections import Counter\n    return sum(count % 2 for count in Counter(s).values()) <= 1", 
    "difficulty": 2, 
    "type": "string",
    "hint": "A string can form a palindrome if at most one character appears an odd number of times."},
    
    {"prompt": "Implement binary search on a sorted list.", 
    "test_cases": [([1,2,3,4,5], 3, 2), ([1,2,3,4,5], 6, -1)], 
    "ai_solution": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Repeatedly divide the search interval in half."},
    
    {"prompt": "Find the peak element in a list (an element greater than its neighbors).", 
    "test_cases": [([1,3,2,4,1], 3), ([1,2,3,1], 2)], 
    "ai_solution": "def find_peak(nums):\n    left, right = 0, len(nums) - 1\n    while left < right:\n        mid = (left + right) // 2\n        if nums[mid] < nums[mid + 1]:\n            left = mid + 1\n        else:\n            right = mid\n    return left", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Use binary search to find a position where the element is greater than its neighbors."},
    
    {"prompt": "Implement a function to check if a string has balanced parentheses.", 
    "test_cases": [("()", True), ("()[]{}", True), ("(]", False), ("([)]", False)], 
    "ai_solution": "def is_balanced(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            if not stack or stack.pop() != mapping[char]:\n                return False\n        else:\n            stack.append(char)\n    return len(stack) == 0", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Use a stack to keep track of opening brackets and match them with closing brackets."},
    
    {"prompt": "Find the longest common prefix of a list of strings.", 
    "test_cases": [(["flower","flow","flight"], "fl"), (["dog","racecar","car"], "")], 
    "ai_solution": "def longest_common_prefix(strs):\n    if not strs:\n        return \"\"\n    prefix = strs[0]\n    for s in strs[1:]:\n        while not s.startswith(prefix):\n            prefix = prefix[:-1]\n            if not prefix:\n                return \"\"\n    return prefix", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Start with the first string as the prefix and shorten it until it's a prefix of all strings."},
    
    {"prompt": "Implement a function to reverse words in a string.", 
    "test_cases": [("the sky is blue", "blue is sky the"), ("  hello world  ", "world hello")], 
    "ai_solution": "def reverse_words(s):\n    return ' '.join(s.split()[::-1])", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Split the string into words, reverse the list, and join it back with spaces."},
    
    {"prompt": "Find the majority element in a list (appears more than n/2 times).", 
    "test_cases": [([3,2,3], 3), ([2,2,1,1,1,2,2], 2)], 
    "ai_solution": "def majority_element(nums):\n    count = 0\n    candidate = None\n    for num in nums:\n        if count == 0:\n            candidate = num\n        count += (1 if num == candidate else -1)\n    return candidate", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Use the Boyer-Moore voting algorithm to find the majority element in linear time."},
    
    {"prompt": "Implement a function to check if a number is a palindrome.", 
    "test_cases": [(121, True), (-121, False), (10, False)], 
    "ai_solution": "def is_palindrome_number(x):\n    if x < 0:\n        return False\n    return str(x) == str(x)[::-1]", 
    "difficulty": 2, 
    "type": "math",
    "hint": "Convert the number to a string and check if it reads the same forward and backward."},
    
    {"prompt": "Find the single number in a list where every element appears twice except for one.", 
    "test_cases": [([2,2,1], 1), ([4,1,2,1,2], 4), ([1], 1)], 
    "ai_solution": "def single_number(nums):\n    result = 0\n    for num in nums:\n        result ^= num\n    return result", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Use the XOR operation to find the single number. XOR of a number with itself is 0."},
    
    {"prompt": "Implement a function to convert a roman numeral to an integer.", 
    "test_cases": [("III", 3), ("IV", 4), ("IX", 9), ("LVIII", 58), ("MCMXCIV", 1994)], 
    "ai_solution": "def roman_to_int(s):\n    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n    total = 0\n    i = 0\n    while i < len(s):\n        if i+1 < len(s) and values[s[i]] < values[s[i+1]]:\n            total += values[s[i+1]] - values[s[i]]\n            i += 2\n        else:\n            total += values[s[i]]\n            i += 1\n    return total", 
    "difficulty": 2, 
    "type": "string",
    "hint": "Map each symbol to its value and handle special cases where a smaller value precedes a larger one."},
    
    {"prompt": "Implement a function to find the first bad version in a sequence.", 
    "test_cases": [([False, False, True, True, True], 2), ([False, True, True], 1), ([True, True, True], 0)], 
    "ai_solution": "def first_bad_version(versions):\n    left, right = 0, len(versions) - 1\n    while left < right:\n        mid = (left + right) // 2\n        if versions[mid]:\n            right = mid\n        else:\n            left = mid + 1\n    return left", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Use binary search to find the first occurrence of True in the list."},
    
    {"prompt": "Implement a function to count the number of set bits in an integer.", 
    "test_cases": [(0, 0), (1, 1), (5, 2), (15, 4)], 
    "ai_solution": "def count_bits(n):\n    count = 0\n    while n:\n        count += n & 1\n        n >>= 1\n    return count", 
    "difficulty": 2, 
    "type": "math",
    "hint": "Use bitwise operations to count the number of 1s in the binary representation."},
    
    {"prompt": "Implement a function to find the maximum subarray sum.", 
    "test_cases": [([-2,1,-3,4,-1,2,1,-5,4], 6), ([1], 1), ([-1], -1)], 
    "ai_solution": "def max_subarray(nums):\n    current_sum = max_sum = nums[0]\n    for num in nums[1:]:\n        current_sum = max(num, current_sum + num)\n        max_sum = max(max_sum, current_sum)\n    return max_sum", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Use Kadane's algorithm to find the maximum subarray sum in linear time."},
    
    {"prompt": "Implement a function to check if a linked list has a cycle.", 
    "test_cases": [([], False), ([1,2,3,4,5], False), ([1,2,3,4,5,3], True)], 
    "ai_solution": "def has_cycle(head):\n    if not head or not head[1:]:\n        return False\n    slow = fast = 0\n    while fast < len(head) - 1:\n        slow = (slow + 1) % len(head)\n        fast = (fast + 2) % len(head)\n        if slow == fast:\n            return True\n    return False", 
    "difficulty": 2, 
    "type": "data_structures",
    "hint": "Use the Floyd's Tortoise and Hare algorithm (slow and fast pointers) to detect cycles."},
    
    {"prompt": "Implement a function to find the intersection of two linked lists.", 
    "test_cases": [([1,2,3,4,5], [9,8,4,5], [4,5]), ([1,2,3], [4,5,6], [])], 
    "ai_solution": "def get_intersection(listA, listB):\n    setA = set(listA)\n    return [x for x in listB if x in setA]", 
    "difficulty": 2, 
    "type": "data_structures",
    "hint": "Convert one list to a set and check which elements from the other list are in the set."},
    
    {"prompt": "Implement a function to find the kth largest element in a list.", 
    "test_cases": [([3,2,1,5,6,4], 2, 5), ([3,2,3,1,2,4,5,5,6], 4, 4)], 
    "ai_solution": "def find_kth_largest(nums, k):\n    return sorted(nums, reverse=True)[k-1]", 
    "difficulty": 2, 
    "type": "list",
    "hint": "Sort the list in descending order and return the (k-1)th element."},
    
    {"prompt": "Implement a function to find all permutations of a string with unique characters.", 
    "test_cases": [("abc", ["abc", "acb", "bac", "bca", "cab", "cba"]), ("a", ["a"])], 
    "ai_solution": "def permutations(s):\n    if len(s) <= 1:\n        return [s]\n    result = []\n    for i, c in enumerate(s):\n        for p in permutations(s[:i] + s[i+1:]):\n            result.append(c + p)\n    return sorted(result)", 
    "difficulty": 2, 
    "type": "recursion",
    "hint": "Use recursion to generate all permutations by fixing one character at a time."},

    # Hard questions (difficulty: 3) - 26 questions
    {"prompt": "Implement Dijkstra's algorithm to find shortest paths from a source vertex.", 
    "test_cases": [({'A':{'B':1,'C':4},'B':{'C':2,'D':5},'C':{'D':1},'D':{}},'A',{'A':0,'B':1,'C':3,'D':4})], 
    "ai_solution": "import heapq\n\ndef dijkstra(graph,start):\n    heap=[(0,start)]\n    dist={node:float('inf') for node in graph}\n    dist[start]=0\n    while heap:\n        d,node=heapq.heappop(heap)\n        if d>dist[node]: continue\n        for nei,weight in graph[node].items():\n            if d+weight<dist[nei]:\n                dist[nei]=d+weight\n                heapq.heappush(heap,(dist[nei],nei))\n    return dist", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Use a priority queue (heap) to always process the node with the smallest distance first."},

    {"prompt": "Find the longest increasing path in a matrix.", 
    "test_cases": [([[9,9,4],[6,6,8],[2,1,1]],4)], 
    "ai_solution": "def longest_increasing_path(matrix):\n    if not matrix: return 0\n    m,n=len(matrix),len(matrix[0])\n    dp=[[0]*n for _ in range(m)]\n    def dfs(i,j):\n        if dp[i][j]: return dp[i][j]\n        val=matrix[i][j]\n        dp[i][j]=1+max(\n            dfs(i+1,j) if i+1<m and matrix[i+1][j]>val else 0,\n            dfs(i-1,j) if i-1>=0 and matrix[i-1][j]>val else 0,\n            dfs(i,j+1) if j+1<n and matrix[i][j+1]>val else 0,\n            dfs(i,j-1) if j-1>=0 and matrix[i][j-1]>val else 0)\n        return dp[i][j]\n    return max(dfs(i,j) for i in range(m) for j in range(n))", 
    "difficulty": 3, 
    "type": "recursion",
    "hint": "Use DFS with memoization to avoid recalculating paths. Check all four directions from each cell."},

    {"prompt": "Implement a Max Heap.", 
    "test_cases": [(["insert 3","insert 5","extract_max"], 5), (["insert 1","insert 3","insert 2","extract_max","extract_max"], [3, 2])], 
    "ai_solution": "class MaxHeap:\n    def __init__(self):\n        self.heap = []\n    \n    def insert(self, val):\n        self.heap.append(val)\n        self._sift_up(len(self.heap) - 1)\n    \n    def extract_max(self):\n        if not self.heap:\n            return None\n        max_val = self.heap[0]\n        last_val = self.heap.pop()\n        if self.heap:\n            self.heap[0] = last_val\n            self._sift_down(0)\n        return max_val\n    \n    def _sift_up(self, idx):\n        parent = (idx - 1) // 2\n        if idx > 0 and self.heap[parent] < self.heap[idx]:\n            self.heap[parent], self.heap[idx] = self.heap[idx], self.heap[parent]\n            self._sift_up(parent)\n    \n    def _sift_down(self, idx):\n        largest = idx\n        left = 2 * idx + 1\n        right = 2 * idx + 2\n        if left < len(self.heap) and self.heap[left] > self.heap[largest]:\n            largest = left\n        if right < len(self.heap) and self.heap[right] > self.heap[largest]:\n            largest = right\n        if largest != idx:\n            self.heap[idx], self.heap[largest] = self.heap[largest], self.heap[idx]\n            self._sift_down(largest)", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Implement the heap property where each parent node is greater than or equal to its children."},

    {"prompt": "Find the number of islands (grid of 0s and 1s).", 
    "test_cases": [([[1,1,0,0],[1,0,0,1],[0,0,1,1]],3)], 
    "ai_solution": "def num_islands(grid):\n    if not grid: return 0\n    m,n=len(grid),len(grid[0])\n    def dfs(i,j):\n        if i<0 or i>=m or j<0 or j>=n or grid[i][j]==0: return\n        grid[i][j]=0\n        dfs(i+1,j)\n        dfs(i-1,j)\n        dfs(i,j+1)\n        dfs(i,j-1)\n    count=0\n    for i in range(m):\n        for j in range(n):\n            if grid[i][j]==1:\n                dfs(i,j)\n                count+=1\n    return count", 
    "difficulty": 3, 
    "type": "recursion",
    "hint": "Use DFS to 'sink' each island when you find it. Mark visited cells by changing their value to 0."},

    {"prompt": "Find the minimum window substring that contains all characters of another string.", 
    "test_cases": [("ADOBECODEBANC","ABC","BANC")], 
    "ai_solution": "def min_window(s,t):\n    from collections import Counter\n    need,counter=Counter(t),{}\n    l=r=0\n    res=(0,float('inf'))\n    required=len(need)\n    formed=0\n    while r<len(s):\n        c=s[r]\n        counter[c]=counter.get(c,0)+1\n        if c in need and counter[c]==need[c]: formed+=1\n        while l<=r and formed==required:\n            if r-l<res[1]-res[0]: res=(l,r)\n            counter[s[l]]-=1\n            if s[l] in need and counter[s[l]]<need[s[l]]: formed-=1\n            l+=1\n        r+=1\n    l,r=res\n    return s[l:r+1] if res[1]<float('inf') else ''", 
    "difficulty": 3, 
    "type": "string",
    "hint": "Use a sliding window approach with two pointers. Track character frequencies with a counter."},

    {"prompt": "Find the shortest path in a maze (2D grid).", 
    "test_cases": [([[0,0,1],[0,0,0],[1,0,0]],(0,0),(2,2),4)], 
    "ai_solution": "from collections import deque\n\ndef shortest_path(grid,start,end):\n    m,n=len(grid),len(grid[0])\n    q=deque([(start[0],start[1],0)])\n    visited=set([(start[0],start[1])])\n    while q:\n        x,y,d=q.popleft()\n        if (x,y)==end: return d\n        for dx,dy in ((0,1),(1,0),(-1,0),(0,-1)):\n            nx,ny=x+dx,y+dy\n            if 0<=nx<m and 0<=ny<n and not grid[nx][ny] and (nx,ny) not in visited:\n                visited.add((nx,ny))\n                q.append((nx,ny,d+1))\n    return -1", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Use BFS with a queue to find the shortest path. Keep track of visited cells to avoid cycles."},

    {"prompt": "Count the number of ways to climb stairs (n steps, 1 or 2 steps at a time).", 
    "test_cases": [(2,2), (3,3)], 
    "ai_solution": "def climb_stairs(n):\n    a,b=1,1\n    for _ in range(n):\n        a,b=b,a+b\n    return a", 
    "difficulty": 3, 
    "type": "recursion",
    "hint": "This is a Fibonacci sequence problem. The number of ways to reach step n is the sum of ways to reach steps n-1 and n-2."},

    {"prompt": "Given two strings, find the minimum number of edits to convert one into the other (edit distance).", 
    "test_cases": [("horse","ros",3),("intention","execution",5)], 
    "ai_solution": "def min_edit_distance(a,b):\n    dp=[[0]*(len(b)+1) for _ in range(len(a)+1)]\n    for i in range(len(a)+1):\n        for j in range(len(b)+1):\n            if i==0: dp[i][j]=j\n            elif j==0: dp[i][j]=i\n            elif a[i-1]==b[j-1]:\n                dp[i][j]=dp[i-1][j-1]\n            else:\n                dp[i][j]=1+min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1])\n    return dp[-1][-1]", 
    "difficulty": 3, 
    "type": "string",
    "hint": "Use dynamic programming with a 2D array. Consider three operations: insert, delete, and replace."},
    
    {"prompt": "Find all unique triplets in the list that sum to zero.", 
    "test_cases": [([-1,0,1,2,-1,-4],[[-1,-1,2],[-1,0,1]])], 
    "ai_solution": "def three_sum(nums):\n    nums.sort()\n    res=[]\n    for i in range(len(nums)-2):\n        if i>0 and nums[i]==nums[i-1]: continue\n        l,r=i+1,len(nums)-1\n        while l<r:\n            s=nums[i]+nums[l]+nums[r]\n            if s==0:\n                res.append([nums[i],nums[l],nums[r]])\n                while l<r and nums[l]==nums[l+1]: l+=1\n                while l<r and nums[r]==nums[r-1]: r-=1\n                l+=1\n                r-=1\n            elif s<0:\n                l+=1\n            else:\n                r-=1\n    return res", 
    "difficulty": 3, 
    "type": "list",
    "hint": "Sort the array first, then use a combination of iteration and two-pointer technique."},

    {"prompt": "Find the longest palindromic substring.", 
    "test_cases": [("babad","bab"), ("cbbd","bb")], 
    "ai_solution": "def longest_palindrome(s):\n    if not s: return ''\n    start, max_len = 0, 1\n    for i in range(len(s)):\n        # Odd length palindromes\n        left, right = i, i\n        while left >= 0 and right < len(s) and s[left] == s[right]:\n            if right - left + 1 > max_len:\n                start = left\n                max_len = right - left + 1\n            left -= 1\n            right += 1\n        # Even length palindromes\n        left, right = i, i + 1\n        while left >= 0 and right < len(s) and s[left] == s[right]:\n            if right - left + 1 > max_len:\n                start = left\n                max_len = right - left + 1\n            left -= 1\n            right += 1\n    return s[start:start + max_len]", 
    "difficulty": 3, 
    "type": "string",
    "hint": "Expand around centers for both odd and even length palindromes."},

    {"prompt": "Implement a trie (prefix tree) with insert, search, and startsWith methods.", 
    "test_cases": [(["insert apple", "search apple", "search app", "startsWith app"], [True, False, True])], 
    "ai_solution": "class TrieNode:\n    def __init__(self):\n        self.children = {}\n        self.is_end = False\n\nclass Trie:\n    def __init__(self):\n        self.root = TrieNode()\n    \n    def insert(self, word):\n        node = self.root\n        for char in word:\n            if char not in node.children:\n                node.children[char] = TrieNode()\n            node = node.children[char]\n        node.is_end = True\n    \n    def search(self, word):\n        node = self.root\n        for char in word:\n            if char not in node.children:\n                return False\n            node = node.children[char]\n        return node.is_end\n    \n    def startsWith(self, prefix):\n        node = self.root\n        for char in prefix:\n            if char not in node.children:\n                return False\n            node = node.children[char]\n        return True", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Use a tree structure where each node represents a character and has children for subsequent characters."},

    {"prompt": "Implement a LRU (Least Recently Used) cache.", 
    "test_cases": [(["put 1 1", "put 2 2", "get 1", "put 3 3", "get 2", "put 4 4", "get 1", "get 3", "get 4"], [1, -1, -1, 3, 4])], 
    "ai_solution": "class LRUCache:\n    def __init__(self, capacity=2):\n        self.capacity = capacity\n        self.cache = {}\n        self.order = []\n    \n    def get(self, key):\n        if key in self.cache:\n            self.order.remove(key)\n            self.order.append(key)\n            return self.cache[key]\n        return -1\n    \n    def put(self, key, value):\n        if key in self.cache:\n            self.order.remove(key)\n        elif len(self.cache) >= self.capacity:\n            oldest = self.order.pop(0)\n            del self.cache[oldest]\n        self.cache[key] = value\n        self.order.append(key)", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Use a dictionary for O(1) lookups and a list to track the order of usage."},

    {"prompt": "Implement a function to solve the N-Queens problem.", 
    "test_cases": [(4, 2), (8, 92)], 
    "ai_solution": "def solve_n_queens(n):\n    def is_safe(board, row, col):\n        # Check column\n        for i in range(row):\n            if board[i][col] == 'Q':\n                return False\n        # Check upper left diagonal\n        for i, j in zip(range(row-1, -1, -1), range(col-1, -1, -1)):\n            if board[i][j] == 'Q':\n                return False\n        # Check upper right diagonal\n        for i, j in zip(range(row-1, -1, -1), range(col+1, n)):\n            if board[i][j] == 'Q':\n                return False\n        return True\n    \n    def backtrack(row):\n        if row == n:\n            return 1\n        count = 0\n        for col in range(n):\n            if is_safe(board, row, col):\n                board[row][col] = 'Q'\n                count += backtrack(row + 1)\n                board[row][col] = '.'\n        return count\n    \n    board = [['.' for _ in range(n)] for _ in range(n)]\n    return backtrack(0)", 
    "difficulty": 3, 
    "type": "recursion",
    "hint": "Use backtracking to place queens one row at a time, checking for conflicts with previously placed queens."},

    {"prompt": "Implement a function to find the median of two sorted arrays.", 
    "test_cases": [([1,3], [2], 2.0), ([1,2], [3,4], 2.5)], 
    "ai_solution": "def find_median_sorted_arrays(nums1, nums2):\n    if len(nums1) > len(nums2):\n        nums1, nums2 = nums2, nums1\n    x, y = len(nums1), len(nums2)\n    low, high = 0, x\n    while low <= high:\n        partitionX = (low + high) // 2\n        partitionY = (x + y + 1) // 2 - partitionX\n        \n        maxX = float('-inf') if partitionX == 0 else nums1[partitionX - 1]\n        minX = float('inf') if partitionX == x else nums1[partitionX]\n        \n        maxY = float('-inf') if partitionY == 0 else nums2[partitionY - 1]\n        minY = float('inf') if partitionY == y else nums2[partitionY]\n        \n        if maxX <= minY and maxY <= minX:\n            if (x + y) % 2 == 0:\n                return (max(maxX, maxY) + min(minX, minY)) / 2\n            else:\n                return max(maxX, maxY)\n        elif maxX > minY:\n            high = partitionX - 1\n        else:\n            low = partitionX + 1", 
    "difficulty": 3, 
    "type": "list",
    "hint": "Use binary search to find the correct partition of the two arrays that gives the median."},

    {"prompt": "Implement a function to serialize and deserialize a binary tree.", 
    "test_cases": [({"val": 1, "left": {"val": 2, "left": None, "right": None}, "right": {"val": 3, "left": {"val": 4, "left": None, "right": None}, "right": {"val": 5, "left": None, "right": None}}}, "1,2,#,#,3,4,#,#,5,#,#")], 
    "ai_solution": "def serialize(root):\n    if not root:\n        return '#'\n    return str(root['val']) + ',' + serialize(root['left']) + ',' + serialize(root['right'])\n\ndef deserialize(data):\n    def dfs(nodes):\n        val = next(nodes)\n        if val == '#':\n            return None\n        node = {'val': int(val), 'left': dfs(nodes), 'right': dfs(nodes)}\n        return node\n    nodes = iter(data.split(','))\n    return dfs(nodes)", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Use preorder traversal for serialization and recursion for deserialization."},

    {"prompt": "Implement a function to find the longest consecutive sequence in an unsorted array.", 
    "test_cases": [([100,4,200,1,3,2], 4), ([0,3,7,2,5,8,4,6,0,1], 9)], 
    "ai_solution": "def longest_consecutive(nums):\n    if not nums:\n        return 0\n    num_set = set(nums)\n    max_length = 0\n    for num in num_set:\n        if num - 1 not in num_set:\n            current_num = num\n            current_streak = 1\n            while current_num + 1 in num_set:\n                current_num += 1\n                current_streak += 1\n            max_length = max(max_length, current_streak)\n    return max_length", 
    "difficulty": 3, 
    "type": "list",
    "hint": "Use a set for O(1) lookups and only start counting sequences from the smallest number in each sequence."},

    {"prompt": "Implement a function to find the kth smallest element in a BST.", 
    "test_cases": [({"val": 3, "left": {"val": 1, "left": None, "right": {"val": 2, "left": None, "right": None}}, "right": {"val": 4, "left": None, "right": None}}, 1, 1)], 
    "ai_solution": "def kth_smallest(root, k):\n    def inorder(node):\n        if not node:\n            return []\n        return inorder(node['left']) + [node['val']] + inorder(node['right'])\n    return inorder(root)[k-1]", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Use inorder traversal to get the elements in sorted order, then return the kth element."},

    {"prompt": "Implement a function to find the skyline of a city represented by buildings.", 
    "test_cases": [([[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]], [[2,10],[3,15],[7,12],[12,0],[15,10],[20,8],[24,0]])], 
    "ai_solution": "import heapq\n\ndef get_skyline(buildings):\n    # Add start and end points with heights\n    points = []\n    for l, r, h in buildings:\n        points.append((l, -h, r))  # Start point, negative height for max heap\n        points.append((r, 0, 0))   # End point\n    points.sort()  # Sort by x-coordinate\n    \n    result = []\n    heap = [(0, float('inf'))]  # (height, ending x-coordinate)\n    prev_height = 0\n    \n    for x, neg_h, r in points:\n        # Remove buildings that have ended\n        while heap[0][1] <= x:\n            heapq.heappop(heap)\n        \n        # Add new building\n        if neg_h != 0:\n            heapq.heappush(heap, (neg_h, r))\n        \n        # If height changes, add to result\n        curr_height = -heap[0][0]\n        if curr_height != prev_height:\n            result.append([x, curr_height])\n            prev_height = curr_height\n    \n    return result", 
    "difficulty": 3, 
    "type": "data_structures",
    "hint": "Use a priority queue (max heap) to track the highest building at each point."},

    {"prompt": "Implement a function to solve the word ladder problem (find shortest transformation sequence).", 
    "test_cases": [("hit", "cog", ["hot","dot","dog","lot","log","cog"], 5)], 
    "ai_solution": "from collections import deque, defaultdict\n\ndef word_ladder(begin_word, end_word, word_list):\n    if end_word not in word_list:\n        return 0\n    \n    # Create adjacency list\n    word_set = set(word_list)\n    word_set.add(begin_word)\n    adj_list = defaultdict(list)\n    \n    for word in word_set:\n        for i in range(len(word)):\n            pattern = word[:i] + '*' + word[i+1:]\n            adj_list[pattern].append(word)\n    \n    # BFS\n    queue = deque([(begin_word, 1)])\n    visited = {begin_word}\n    \n    while queue:\n        word, level = queue.popleft()\n        if word == end_word:\n            return level\n        \n        for i in range(len(word)):\n            pattern = word[:i] + '*' + word[i+1:]\n            for neighbor in adj_list[pattern]:\n                if neighbor not in visited:\n                    visited.add(neighbor)\n                    queue.append((neighbor, level + 1))\n    \n    return 0", 
    "difficulty": 3, 
    "type": "string",
    "hint": "Use BFS to find the shortest path, and use patterns with wildcards to find adjacent words efficiently."},

    {"prompt": "Implement a function to find the maximum profit from buying and selling stocks with at most k transactions.", 
    "test_cases": [([3,2,6,5,0,3], 2, 7)], 
    "ai_solution": "def max_profit_k_transactions(prices, k):\n    if not prices or k == 0:\n        return 0\n    \n    n = len(prices)\n    if k >= n // 2:  # If k is large enough, we can make as many transactions as we want\n        profit = 0\n        for i in range(1, n):\n            if prices[i] > prices[i-1]:\n                profit += prices[i] - prices[i-1]\n        return profit\n    \n    # dp[i][j] = max profit with at most i transactions up to day j\n    dp = [[0 for _ in range(n)] for _ in range(k+1)]\n    \n    for i in range(1, k+1):\n        max_diff = -prices[0]  # Initialize max_diff\n        for j in range(1, n):\n            dp[i][j] = max(dp[i][j-1], prices[j] + max_diff)\n            max_diff = max(max_diff, dp[i-1][j] - prices[j])\n    \n    return dp[k][n-1]", 
    "difficulty": 3, 
    "type": "list",
    "hint": "Use dynamic programming with a 2D array where dp[i][j] represents the max profit with at most i transactions up to day j."},

    {"prompt": "Implement a function to find the longest substring without repeating characters.", 
    "test_cases": [("abcabcbb", 3), ("bbbbb", 1), ("pwwkew", 3)], 
    "ai_solution": "def length_of_longest_substring(s):\n    char_dict = {}\n    max_length = start = 0\n    \n    for i, char in enumerate(s):\n        if char in char_dict and start <= char_dict[char]:\n            start = char_dict[char] + 1\n        else:\n            max_length = max(max_length, i - start + 1)\n        \n        char_dict[char] = i\n    \n    return max_length", 
    "difficulty": 3, 
    "type": "string",
    "hint": "Use a sliding window approach with a dictionary to track the most recent index of each character."},

    {"prompt": "Implement a function to find the maximum sum of a subarray with length k.", 
    "test_cases": [([1,3,-1,-3,5,3,6,7], 3, 16), ([1,2,3,4,5], 2, 9)], 
    "ai_solution": "def max_subarray_sum(nums, k):\n    if not nums or k <= 0 or k > len(nums):\n        return 0\n    \n    window_sum = sum(nums[:k])\n    max_sum = window_sum\n    \n    for i in range(k, len(nums)):\n        window_sum = window_sum + nums[i] - nums[i-k]\n        max_sum = max(max_sum, window_sum)\n    \n    return max_sum", 
    "difficulty": 3, 
    "type": "list",
    "hint": "Use a sliding window approach to efficiently calculate the sum of each k-length subarray."},

    {"prompt": "Implement a function to find the number of islands in a grid (connected horizontally, vertically, and diagonally).", 
    "test_cases": [([[1,1,0,0,0],[1,1,0,0,0],[0,0,1,0,0],[0,0,0,1,1]], 3)], 
    "ai_solution": "def count_islands(grid):\n    if not grid:\n        return 0\n    \n    rows, cols = len(grid), len(grid[0])\n    count = 0\n    \n    def dfs(r, c):\n        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:\n            return\n        \n        grid[r][c] = 0  # Mark as visited\n        \n        # Check all 8 directions\n        for dr in [-1, 0, 1]:\n            for dc in [-1, 0, 1]:\n                if dr == 0 and dc == 0:\n                    continue\n                dfs(r + dr, c + dc)\n    \n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == 1:\n                count += 1\n                dfs(r, c)\n    \n    return count", 
    "difficulty": 3, 
    "type": "recursion",
    "hint": "Use DFS to explore all connected cells (including diagonals) and mark them as visited."},

    {"prompt": "Implement a function to find the kth largest element in an unsorted array.", 
    "test_cases": [([3,2,1,5,6,4], 2, 5), ([3,2,3,1,2,4,5,5,6], 4, 4)], 
    "ai_solution": "def find_kth_largest(nums, k):\n    def quickselect(nums, k):\n        pivot = nums[len(nums) // 2]\n        left = [x for x in nums if x > pivot]\n        mid = [x for x in nums if x == pivot]\n        right = [x for x in nums if x < pivot]\n        \n        if k <= len(left):\n            return quickselect(left, k)\n        elif k <= len(left) + len(mid):\n            return pivot\n        else:\n            return quickselect(right, k - len(left) - len(mid))\n    \n    return quickselect(nums, k)", 
    "difficulty": 3, 
    "type": "list",
    "hint": "Use the quickselect algorithm, which is similar to quicksort but only explores one partition."}]

# Pre-filter questions by difficulty
easy_questions = [q for q in questions if q["difficulty"] == 1]
medium_questions = [q for q in questions if q["difficulty"] == 2]
hard_questions = [q for q in questions if q["difficulty"] == 3]

def pick_random_question(difficulty):
    global used_questions
    if difficulty == 1:
        available = [q for q in easy_questions if id(q) not in used_questions]
        if not available:
            available = easy_questions
            used_questions = set()
    elif difficulty == 2:
        available = [q for q in medium_questions if id(q) not in used_questions]
        if not available:
            available = medium_questions
            used_questions = set()
    else:
        available = [q for q in hard_questions if id(q) not in used_questions]
        if not available:
            available = hard_questions
            used_questions = set()
    next_q = random.choice(available)
    used_questions.add(id(next_q))
    return next_q

def analyze_code_style(user_code, ai_code):
    """
    Analyze the style similarities between user code and AI code.
    Returns a dictionary with style metrics and feedback.
    """
    # Initialize metrics
    metrics = {
        "brevity": 0,
        "structure": 0,
        "overall_similarity": 0,
        "feedback": ""
    }
    
    # Clean and split the code into lines
    user_lines = [line.strip() for line in user_code.strip().split('\n') if line.strip()]
    ai_lines = [line.strip() for line in ai_code.strip().split('\n') if line.strip()]
    
    # Calculate brevity score (comparing line count)
    user_line_count = len(user_lines)
    ai_line_count = len(ai_lines)
    
    if user_line_count <= ai_line_count * 1.2:  # User code is at most 20% longer than AI
        metrics["brevity"] = 100
    else:
        # Calculate how much longer the user code is
        brevity_ratio = ai_line_count / user_line_count if user_line_count > 0 else 0
        metrics["brevity"] = int(brevity_ratio * 100)
    
    # Calculate structure similarity (simple heuristic based on function structure)
    # Check if both have similar function definitions, loops, conditionals
    user_structure = []
    ai_structure = []
    
    # Extract structural elements (very simplified)
    for line in user_lines:
        if line.startswith('def ') or line.startswith('class ') or 'for ' in line or 'while ' in line or 'if ' in line:
            user_structure.append(line.split('(')[0] if '(' in line else line)
    
    for line in ai_lines:
        if line.startswith('def ') or line.startswith('class ') or 'for ' in line or 'while ' in line or 'if ' in line:
            ai_structure.append(line.split('(')[0] if '(' in line else line)
    
    # Compare structures
    if len(user_structure) > 0 and len(ai_structure) > 0:
        # Simple similarity measure
        common_elements = set(user_structure).intersection(set(ai_structure))
        structure_similarity = len(common_elements) / max(len(user_structure), len(ai_structure))
        metrics["structure"] = int(structure_similarity * 100)
    else:
        metrics["structure"] = 50  # Default if we can't determine
    
    # Calculate overall similarity
    metrics["overall_similarity"] = (metrics["brevity"] + metrics["structure"]) // 2
    
    # Generate feedback
    if metrics["overall_similarity"] >= 80:
        metrics["feedback"] = "Your code style is very similar to the AI solution - concise and well-structured!"
    elif metrics["overall_similarity"] >= 60:
        metrics["feedback"] = "Your code has good similarities with the AI solution, but could be more concise."
    else:
        metrics["feedback"] = "Consider studying the AI solution for ideas on how to make your code more concise and better structured."
    
    # Add specific feedback based on metrics
    if metrics["brevity"] < 60:
        metrics["feedback"] += " Your solution uses significantly more lines than necessary."
    
    if metrics["structure"] < 60:
        metrics["feedback"] += " The structure of your code differs from common patterns used in efficient solutions."
    
    return metrics

# Add this function after your imports and before your Flask app initialization
def analyze_code_comparison(user_code, ai_solution):
    """
    Analyze and compare user code with AI solution across multiple dimensions.
    Returns a detailed comparison object.
    """
    import ast
    
    # Initialize comparison metrics
    comparison = {
        "size": {
            "user_chars": len(user_code),
            "ai_chars": len(ai_solution),
            "user_lines": len(user_code.strip().split('\n')),
            "ai_lines": len(ai_solution.strip().split('\n')),
            "size_score": 0  # Will be calculated
        },
        "speed": {
            "estimated_complexity": "",
            "speed_score": 0  # Will be calculated
        },
        "elegance": {
            "pythonic_score": 0,
            "readability_score": 0,
            "elegance_score": 0  # Will be calculated
        },
        "overall_score": 0,  # Will be calculated
        "winner": "",  # Will be determined
        "feedback": []  # Will contain specific feedback points
    }
    
    # Calculate size score (lower is better)
    # If user code is shorter, they get a higher score
    char_ratio = comparison["size"]["ai_chars"] / max(1, comparison["size"]["user_chars"])
    line_ratio = comparison["size"]["ai_lines"] / max(1, comparison["size"]["user_lines"])
    comparison["size"]["size_score"] = min(100, int((char_ratio + line_ratio) * 50))
    
    # Add size feedback
    if comparison["size"]["user_chars"] < comparison["size"]["ai_chars"]:
        comparison["feedback"].append("Your solution is more concise than GPT-4's!")
    elif comparison["size"]["user_chars"] > comparison["size"]["ai_chars"] * 1.5:
        comparison["feedback"].append("GPT-4's solution is more concise. Consider if there are unnecessary steps in your code.")
    
    # Estimate code complexity and speed
    try:
        # Parse the code to look for loops and nested structures
        user_ast = ast.parse(user_code)
        ai_ast = ast.parse(ai_solution)
        
        # Count loops and conditionals
        user_loops = sum(1 for node in ast.walk(user_ast) if isinstance(node, (ast.For, ast.While)))
        ai_loops = sum(1 for node in ast.walk(ai_ast) if isinstance(node, (ast.For, ast.While)))
        
        user_conditionals = sum(1 for node in ast.walk(user_ast) if isinstance(node, ast.If))
        ai_conditionals = sum(1 for node in ast.walk(ai_ast) if isinstance(node, ast.If))
        
        # Estimate complexity
        user_complexity = user_loops * (1 + 0.5 * user_conditionals)
        ai_complexity = ai_loops * (1 + 0.5 * ai_conditionals)
        
        # Determine complexity class
        if user_loops == 0:
            comparison["speed"]["estimated_complexity"] = "O(1) - Constant time"
        elif user_loops == 1 and user_conditionals <= 1:
            comparison["speed"]["estimated_complexity"] = "O(n) - Linear time"
        elif user_loops > 1 or (user_loops == 1 and user_conditionals > 1):
            comparison["speed"]["estimated_complexity"] = "O(n²) or higher - Quadratic or higher"
        
        # Calculate speed score
        if user_complexity < ai_complexity:
            comparison["speed"]["speed_score"] = 90
        elif user_complexity == ai_complexity:
            comparison["speed"]["speed_score"] = 70
        else:
            comparison["speed"]["speed_score"] = 50
            
        # Add speed feedback
        if user_complexity < ai_complexity:
            comparison["feedback"].append("Your solution appears to be more efficient than GPT-4's!")
        elif user_complexity > ai_complexity:
            comparison["feedback"].append("GPT-4's solution might be more efficient. Look for ways to reduce loops or conditionals.")
    except:
        # If parsing fails, give a neutral score
        comparison["speed"]["speed_score"] = 50
        comparison["speed"]["estimated_complexity"] = "Unable to determine"
    
    # Evaluate elegance (Pythonic features, readability)
    # Check for Pythonic features
    pythonic_features = [
        ("list comprehension", any("for" in line and "[" in line and "]" in line for line in user_code.split("\n"))),
        ("built-in functions", any(func in user_code for func in ["map", "filter", "reduce", "zip", "enumerate", "any", "all"])),
        ("slicing", "[:" in user_code),
        ("dictionary comprehension", any("{" in line and "for" in line and "}" in line for line in user_code.split("\n"))),
        ("generator expressions", any("(" in line and "for" in line and ")" in line for line in user_code.split("\n"))),
        ("f-strings", "f\"" in user_code or "f'" in user_code)
    ]
    
    # Count Pythonic features used
    pythonic_count = sum(1 for _, used in pythonic_features if used)
    comparison["elegance"]["pythonic_score"] = min(100, pythonic_count * 20)
    
    # Estimate readability based on line length and variable names
    avg_line_length = sum(len(line) for line in user_code.split("\n")) / max(1, comparison["size"]["user_lines"])
    if avg_line_length < 50:
        comparison["elegance"]["readability_score"] = 80
    elif avg_line_length < 80:
        comparison["elegance"]["readability_score"] = 60
    else:
        comparison["elegance"]["readability_score"] = 40
    
    # Calculate overall elegance score
    comparison["elegance"]["elegance_score"] = (comparison["elegance"]["pythonic_score"] + comparison["elegance"]["readability_score"]) // 2
    
    # Add elegance feedback
    if pythonic_count >= 2:
        comparison["feedback"].append("Nice use of Pythonic features in your solution!")
    elif pythonic_count == 0:
        comparison["feedback"].append("Consider using more Pythonic features like list comprehensions or built-in functions.")
    
    if avg_line_length > 80:
        comparison["feedback"].append("Consider breaking up long lines for better readability.")
    
    # Calculate overall score
    comparison["overall_score"] = (comparison["size"]["size_score"] + comparison["speed"]["speed_score"] + comparison["elegance"]["elegance_score"]) // 3
    
    # Determine winner
    if comparison["overall_score"] >= 70:
        comparison["winner"] = "user"
        comparison["feedback"].insert(0, "Great job! Your solution outperforms GPT-4 overall.")
    elif comparison["overall_score"] >= 50:
        comparison["winner"] = "tie"
        comparison["feedback"].insert(0, "Your solution is comparable to GPT-4's. Well done!")
    else:
        comparison["winner"] = "ai"
        comparison["feedback"].insert(0, "GPT-4's solution has some advantages, but keep practicing!")
    
    return comparison

def get_daily_challenge():
    """
    Returns the daily challenge question based on the current date.
    The same question will be returned for all users on the same day.
    """
    # Get today's date in YYYY-MM-DD format
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Create a hash of the date to use as a seed
    date_hash = int(hashlib.md5(today.encode()).hexdigest(), 16)
    
    # Use the hash to select a question from the hard questions
    # This ensures the same question is selected for all users on the same day
    index = date_hash % len(hard_questions)
    return hard_questions[index]

@app.route('/')
def landing():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/save-reflection', methods=['POST'])
def save_reflection():
    data = request.get_json()
    prompt = data.get('prompt')
    reflection = data.get('reflection')
    
    # Initialize reflections in session if not present
    if 'reflections' not in session:
        session['reflections'] = []
    
    # Add the new reflection
    session['reflections'].append({
        'prompt': prompt,
        'reflection': reflection,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    
    return jsonify({"success": True})

@app.route('/game')
def index():
    global current_question, attempts_left, current_difficulty, question_attempts
    current_difficulty = 1
    attempts_left = total_attempts
    current_question = pick_random_question(current_difficulty)
    question_attempts[id(current_question)] = 0  # Reset attempts for this question
    
    # Initialize streak counter if it doesn't exist
    if 'streak' not in session:
        session['streak'] = 0
    if 'max_streak' not in session:
        session['max_streak'] = 0
        
    return render_template('index.html', question=current_question, 
                          streak=session['streak'], max_streak=session['max_streak'],
                          is_daily_challenge=False)

@app.route('/reflections')
def view_reflections():
    reflections = session.get('reflections', [])
    return render_template('reflections.html', reflections=reflections)


@app.route('/daily-challenge')
def daily_challenge():
    """Route for the daily coding challenge."""
    global current_question, attempts_left, question_attempts
    
    # Get today's date
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Check if user has already completed today's challenge
    daily_completed = session.get('daily_completed', {})
    has_completed = daily_completed.get(today, False)
    
    # If already completed, redirect to success page
    if has_completed:
        return redirect(url_for('daily_success'))
    
    # Get the daily challenge question
    current_question = get_daily_challenge()
    attempts_left = float('inf')  # Unlimited attempts for daily challenge
    question_attempts[id(current_question)] = 0  # Reset attempts for this question
    
    # Initialize streak counter if it doesn't exist
    if 'streak' not in session:
        session['streak'] = 0
    if 'max_streak' not in session:
        session['max_streak'] = 0
    if 'daily_streak' not in session:
        session['daily_streak'] = 0
    if 'max_daily_streak' not in session:
        session['max_daily_streak'] = 0
        
    return render_template('daily_challenge.html', 
                          question=current_question, 
                          streak=session['streak'], 
                          max_streak=session['max_streak'],
                          daily_streak=session.get('daily_streak', 0),
                          max_daily_streak=session.get('max_daily_streak', 0),
                          has_completed=has_completed,
                          is_daily_challenge=True)

@app.route('/daily-success')
def daily_success():
    """Route for the daily challenge success page."""
    # Initialize streak counter if it doesn't exist
    if 'daily_streak' not in session:
        session['daily_streak'] = 0
        
    return render_template('daily_success.html', 
                          daily_streak=session.get('daily_streak', 0))

@app.route('/time-attack')
def time_attack():
    """Route for the time attack mode - solve as many problems as possible in 10 minutes."""
    global current_question, attempts_left, question_attempts
    
    # Start with an easy question
    current_question = pick_random_question(1)
    attempts_left = total_attempts
    question_attempts[id(current_question)] = 0  # Reset attempts for this question
    
    # Initialize time attack stats if they don't exist
    if 'time_attack_high_score' not in session:
        session['time_attack_high_score'] = 0
    
    return render_template('time_attack.html', 
                          question=current_question,
                          high_score=session.get('time_attack_high_score', 0),
                          is_time_attack=True)

@app.route('/progress')
def progress():
    """Route for the progress tracker with performance analytics."""
    # Initialize stats if they don't exist
    if 'stats' not in session:
        session['stats'] = {
            'by_topic': {
                'math': {'correct': 0, 'total': 0},
                'string': {'correct': 0, 'total': 0},
                'list': {'correct': 0, 'total': 0},
                'recursion': {'correct': 0, 'total': 0},
                'data_structures': {'correct': 0, 'total': 0}
            },
            'by_difficulty': {
                '1': {'correct': 0, 'total': 0},
                '2': {'correct': 0, 'total': 0},
                '3': {'correct': 0, 'total': 0}
            },
            'time_spent': {
                'math': 0,
                'string': 0,
                'list': 0,
                'recursion': 0,
                'data_structures': 0
            },
            'difficulty_progression': [],
            'recent_submissions': []
        }
    
    # Calculate accuracy percentages
    topic_accuracy = {}
    for topic, data in session['stats']['by_topic'].items():
        if data['total'] > 0:
            topic_accuracy[topic] = round((data['correct'] / data['total']) * 100)
        else:
            topic_accuracy[topic] = 0
    
    difficulty_accuracy = {}
    for diff, data in session['stats']['by_difficulty'].items():
        if data['total'] > 0:
            difficulty_accuracy[diff] = round((data['correct'] / data['total']) * 100)
        else:
            difficulty_accuracy[diff] = 0
    
    # Format time spent data
    time_spent = {}
    for topic, seconds in session['stats']['time_spent'].items():
        minutes = seconds // 60
        time_spent[topic] = minutes
    
    return render_template('progress.html',
                          topic_accuracy=topic_accuracy,
                          difficulty_accuracy=difficulty_accuracy,
                          time_spent=time_spent,
                          difficulty_progression=session['stats'].get('difficulty_progression', []),
                          recent_submissions=session['stats'].get('recent_submissions', []))


@app.route('/submit', methods=['POST'])
def submit():
    global current_question, current_difficulty, used_questions, attempts_left, question_attempts

    if request.is_json:
        data = request.get_json()
    else:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    user_code = data.get('code')
    challenge_mode = data.get('challengeMode', False)
    
    if not user_code:
        return jsonify({"success": False, "error": "No code provided"}), 400

    if current_question is None:
        current_question = random.choice(easy_questions)
        question_attempts[id(current_question)] = 0

    # Increment attempts for this specific question
    question_id = id(current_question)
    if question_id not in question_attempts:
        question_attempts[question_id] = 0
    question_attempts[question_id] += 1

    try:
        local_vars = {}
        exec(user_code, {}, local_vars)
        if not local_vars:
            return jsonify({"success": False, "error": "No function defined in code"}), 400
        func_name = next((k for k in local_vars if callable(local_vars[k])), None)
        if func_name is None:
            return jsonify({"success": False, "error": "No function defined in code"}), 400
        user_func = local_vars[func_name]
    except Exception as e:
        return jsonify({"success": False, "error": f"Error in code: {str(e)}"}), 400

    test_cases = current_question['test_cases']
    passed = 0
    detailed_results = []

    for case in test_cases:
        try:
            input_args = case[:-1]
            expected = case[-1]
            result = user_func(*input_args)
            is_pass = result == expected
            if is_pass:
                passed += 1
            
            # Create detailed result with additional feedback for beginner mode
            result_info = {
                'input': input_args,
                'expected': expected,
                'result': result,
                'pass': is_pass
            }
            
            # Add step-by-step feedback for beginner mode
            if not is_pass and not challenge_mode:
                # Add hints based on the type of problem
                problem_type = current_question.get('type', '')
                
                if problem_type == 'math':
                    result_info['hint'] = "Check your mathematical operations and edge cases."
                elif problem_type == 'string':
                    result_info['hint'] = "Pay attention to string manipulation and character handling."
                elif problem_type == 'list':
                    result_info['hint'] = "Verify your list operations and indexing."
                elif problem_type == 'recursion':
                    result_info['hint'] = "Check your base case and recursive steps."
                elif problem_type == 'data_structures':
                    result_info['hint'] = "Review your data structure implementation and operations."
                else:
                    result_info['hint'] = "Compare your output with the expected result carefully."
            
            detailed_results.append(result_info)
            
        except Exception as e:
            detailed_results.append({
                'input': case[:-1],
                'expected': case[-1],
                'result': f"Error: {str(e)}",
                'pass': False,
                'hint': "Your code threw an exception. Check for bugs in your implementation."
            })

    user_lines = len(user_code.strip().split('\n'))
    ai_lines = len(current_question['ai_solution'].split('\n'))
    score = passed / len(test_cases)

    # Check if we should show the hint (after 2 failed attempts)
    show_hint = False
    if question_attempts[question_id] >= 2 and score < 1 and not challenge_mode:
        show_hint = True
        hint = current_question.get('hint', "Try a different approach to solve this problem.")
    else:
        hint = None

    # Update streak counter
    streak_broken = False
    daily_challenge_completed = False
    is_daily_challenge = data.get('isDailyChallenge', False)
    is_time_attack = data.get('isTimeAttack', False)
    time_attack_score_updated = False
    
    # Track statistics for progress page
    if 'stats' not in session:
        session['stats'] = {
            'by_topic': {
                'math': {'correct': 0, 'total': 0},
                'string': {'correct': 0, 'total': 0},
                'list': {'correct': 0, 'total': 0},
                'recursion': {'correct': 0, 'total': 0},
                'data_structures': {'correct': 0, 'total': 0}
            },
            'by_difficulty': {
                '1': {'correct': 0, 'total': 0},
                '2': {'correct': 0, 'total': 0},
                '3': {'correct': 0, 'total': 0}
            },
            'time_spent': {
                'math': 0,
                'string': 0,
                'list': 0,
                'recursion': 0,
                'data_structures': 0
            },
            'difficulty_progression': [],
            'recent_submissions': []
        }
    
    # Update statistics
    topic = current_question.get('type', 'other')
    difficulty = str(current_question.get('difficulty', 1))
    
    # Track time spent (using the time_taken parameter if provided, otherwise estimate 5 minutes)
    time_taken = data.get('time_taken', 300)  # Default to 5 minutes if not provided
    
    if topic in session['stats']['by_topic']:
        session['stats']['by_topic'][topic]['total'] += 1
        session['stats']['time_spent'][topic] += time_taken
        if score == 1:  # All tests passed
            session['stats']['by_topic'][topic]['correct'] += 1
    
    if difficulty in session['stats']['by_difficulty']:
        session['stats']['by_difficulty'][difficulty]['total'] += 1
        if score == 1:  # All tests passed
            session['stats']['by_difficulty'][difficulty]['correct'] += 1
    
    # Track difficulty progression
    if score == 1:  # All tests passed
        session['stats']['difficulty_progression'].append(int(difficulty))
        # Keep only the last 20 entries
        if len(session['stats']['difficulty_progression']) > 20:
            session['stats']['difficulty_progression'] = session['stats']['difficulty_progression'][-20:]
    
    # Track recent submissions
    submission_info = {
        'prompt': current_question['prompt'],
        'difficulty': int(difficulty),
        'type': topic,
        'success': score == 1,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    session['stats']['recent_submissions'].insert(0, submission_info)
    # Keep only the last 10 submissions
    if len(session['stats']['recent_submissions']) > 10:
        session['stats']['recent_submissions'] = session['stats']['recent_submissions'][:10]
    
    if score == 1:  # All tests passed
        session['streak'] = session.get('streak', 0) + 1
        if session['streak'] > session.get('max_streak', 0):
            session['max_streak'] = session['streak']
            
        # If this is the daily challenge, mark it as completed
        if is_daily_challenge:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            daily_completed = session.get('daily_completed', {})
            
            # Only update streak if this is the first time completing today's challenge
            if not daily_completed.get(today, False):
                daily_challenge_completed = True
                daily_completed[today] = True
                session['daily_completed'] = daily_completed
                
                # Check if yesterday's challenge was completed
                yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                if daily_completed.get(yesterday, False):
                    session['daily_streak'] = session.get('daily_streak', 0) + 1
                    if session['daily_streak'] > session.get('max_daily_streak', 0):
                        session['max_daily_streak'] = session['daily_streak']
                else:
                    # Reset streak if yesterday's challenge wasn't completed
                    session['daily_streak'] = 1
        
        # If this is time attack mode, update the score
        elif is_time_attack:
            current_score = data.get('timeAttackScore', 0) + 1
            if current_score > session.get('time_attack_high_score', 0):
                session['time_attack_high_score'] = current_score
                time_attack_score_updated = True
    else:
        if session.get('streak', 0) > 0:
            streak_broken = True
        session['streak'] = 0

    move_to_next = False
    current_solution = None
    if score == 1:
        current_difficulty = min(current_difficulty + 1, 3)
        move_to_next = True
        attempts_left = total_attempts
    else:
        # Check if this is a daily challenge
        is_daily_challenge = data.get('isDailyChallenge', False)
        
        if is_daily_challenge:
            # For daily challenge, don't decrement attempts (unlimited attempts)
            # And don't move to next question on failure
            pass
        else:
            # For regular practice and time attack, use limited attempts
            attempts_left -= 1
            if attempts_left == 0:
                # Store the current question's solution before moving to next question
                current_solution = current_question['ai_solution']
                current_difficulty = max(current_difficulty - 1, 1)
                move_to_next = True
                attempts_left = total_attempts

    if move_to_next:
        current_question = pick_random_question(current_difficulty)
        question_attempts[id(current_question)] = 0  # Reset attempts for new question

    # Analyze code style if all tests passed
    code_style_analysis = None
    reflection_prompt = None
    feedback_message = None
    
    if score == 1:  # All tests passed
        # Add a reflection prompt
        reflection_prompt = random.choice(reflection_prompts)
        
        # Analyze code style
        code_style_analysis = analyze_code_style(user_code, current_question['ai_solution'])
        code_comparison = analyze_code_comparison(user_code, current_question['ai_solution'])  # Add this line

    else:
        # Add feedback message for incorrect solution
        feedback_message = "❌ Your solution is incorrect. Try again!"
    
    return jsonify({
    "success": True,
    "passed": passed,
    "total": len(test_cases),
    "user_lines": user_lines,
    "ai_lines": ai_lines,
    "next_question": current_question,
    "detailed_results": detailed_results,
    "move_to_next": move_to_next,
    "attempts_left": attempts_left,
    "challenge_mode": challenge_mode,
    "show_hint": show_hint,
    "hint": hint,
    "question_attempts": question_attempts[question_id],
    "streak": session.get('streak', 0),
    "max_streak": session.get('max_streak', 0),
    "streak_broken": streak_broken,
    "daily_challenge_completed": daily_challenge_completed,
    "daily_streak": session.get('daily_streak', 0),
    "max_daily_streak": session.get('max_daily_streak', 0),
    "time_attack_score_updated": time_attack_score_updated,
    "time_attack_high_score": session.get('time_attack_high_score', 0),
    "topic": current_question.get('type', 'other'),
    "difficulty": current_question.get('difficulty', 1),
    "reflection_prompt": reflection_prompt,
    "code_style_analysis": code_style_analysis,
    "current_solution": current_solution,
    "feedback_message": feedback_message,
    "code_comparison": code_comparison  # Add this line
})


if __name__ == '__main__':
    app.run(debug=True)