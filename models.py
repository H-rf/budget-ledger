class Transaction:
    
    def __init__(self, description, amount, kind):
        self.description = description
        self.amount = amount
        self.kind = kind

    def __repr__(self):
        return f"Task(title={self.description!r}, priority={self.amount!r}, done={self.kind!r})"
