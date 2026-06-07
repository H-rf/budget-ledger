class Transaction:
    
    def __init__(self, description: str, amount: int | float, kind: str):
        self.description = description
        self.amount = amount
        self.kind = kind

    def __repr__(self) -> str:
        return f"Transaction(description={self.description!r}, amount={self.amount!r}, kind={self.kind!r})"
