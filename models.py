class Transaction:
    
    def __init__(self, description, amount, kind):
        self.description = description
        self.amount = amount
        self.kind = kind

    def __repr__(self):
        return f"Transaction(description={self.description!r}, amount={self.amount!r}, kind={self.kind!r})"
