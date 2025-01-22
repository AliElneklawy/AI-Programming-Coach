cohere_sys_msg = """
## Task and Context
You are an AI system that evaluates whether a user's answer to a given question is correct or not.
Analyze the provided question and the user's answer. If the user's answer is correct, respond with "1." Otherwise, respond with "0".
"""

initial_asses_qs = [
                    ("What is the output of print(5 + 3 * 3) in Python?", 1),
                    ("How do you create a variable in Python to store the value 10?", 1),
                    ("What does the len() function do in Python?", 1), 
                    ("How do you write a comment in Python?", 1),
                    ("What is the difference between a list and a dictionary in Python?", 2),
                    ("How would you check if a key exists in a dictionary?", 2),
                    ("What is a Python class, and how do you create one?", 2),
                    ("Explain the difference between positional and keyword arguments in Python functions.", 2),
                    ("What is the difference between a deep copy and a shallow copy in Python?", 3),
                    ("Explain the concept of Python's Global Interpreter Lock (GIL) and its impact on multithreading.", 3)
                ]

beginner_questions = [
                ("What is Python used for?", "beginner"), 
                ("How do you create a variable in Python?", "beginner"), 
                ("What is the difference between a list and a tuple in Python?", "beginner"), 
                ("How do you write a for loop in Python?", "beginner"), 
                ("What is the output of print(2 + 3 * 4) in Python?", "beginner"), 
                ("How do you convert a string to an integer in Python?", "beginner"), 
                ("What does the len() function do in Python?", "beginner"), 
                ("How do you define a function in Python?", "beginner"), 
                ("What is the difference between = and == in Python?", "beginner"), 
                ("How do you import a library in Python?", "beginner")
            ]

intermediate_questions = [
                ("What is the difference between a shallow copy and a deep copy in Python?", "intermediate"),
                ("Explain the use of decorators in Python and provide an example.", "intermediate"),
                ("What are Python's `*args` and `**kwargs`, and when should they be used?", "intermediate"),
                ("How does Python's Global Interpreter Lock (GIL) affect multithreading?", "intermediate"),
                ("Explain the difference between `is` and `==` in Python.", "intermediate"),
                ("What are list comprehensions, and how are they different from generator expressions?", "intermediate"),
                ("How can you handle exceptions in Python using `try`, `except`, `else`, and `finally`?", "intermediate"),
                ("What are Python's data classes, and when should they be used?", "intermediate"),
                ("Explain the concept of closures in Python with an example.", "intermediate"),
                ("What are Python's metaclasses, and how are they used?", "intermediate")
            ]

advanced_questions = [
                ("What is the purpose of the `__new__` method in Python, and how does it differ from `__init__`?", "advanced"),
                ("Explain how Python implements method resolution order (MRO) and its significance in multiple inheritance.", "advanced"),
                ("What are Python's coroutines, and how do they differ from generators? Provide an example.", "advanced"),
                ("How can you use `contextvars` to manage context-specific variables in asynchronous programming?", "advanced"),
                ("What is the difference between mutable and immutable types in Python, and how does it affect hashability?", "advanced"),
                ("Explain the internals of Python's garbage collection mechanism and how the `gc` module works.", "advanced"),
                ("How does the `@property` decorator work in Python, and how can it be used to define getters, setters, and deleters?", "advanced"),
                ("What are descriptors in Python, and how can you use them to create reusable property-like behavior?", "advanced"),
                ("Explain how Python's `asyncio` event loop works and how it coordinates multiple coroutines.", "advanced"),
                ("What are slots (`__slots__`) in Python, and how do they improve memory efficiency?", "advanced")
            ]

