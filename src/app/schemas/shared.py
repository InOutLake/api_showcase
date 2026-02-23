class NotAssigned:
    def __bool__(self):
        return False

    def __repr__(self) -> str:
        return "NOT_ASSIGNED"


NOT_ASSIGNED = NotAssigned()
