class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return None

    def top(self):
        if not self.is_empty():
            return self.stack[-1]
        return None

    def is_empty(self):
        return len(self.stack) == 0

    def len(self):
      return len(self.stack)
    
    def __str__(self):
        output = f"Stack ({len(self.stack)}): \n"
        for item in self.stack:
            if item is None:
                output += "None\n"
            else:
                output += f"{str(item)} {type(item)} \n"
        return output