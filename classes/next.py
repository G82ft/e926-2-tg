class Next:
    value: any
    matched: bool = False

    def __init__(self, value: any):
        self.value = value
        self.matched = False

    def __eq__(self, other):
        if self.value == other:
            self.matched = True
            return False

        return self.matched

    def __str__(self):
        return str(self.value)
