class Person:
    counter = 1
    def __init__(self):
        self.timeSpent = 0
        self.id = Person.counter
        Person.counter += 1
