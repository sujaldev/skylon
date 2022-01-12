class AtRule:
    def __init__(self, name, prelude=None, block=None):
        self.name = name
        if self.prelude is None:
            self.prelude = []
        else:
            self.prelude = prelude
        self.block = block


class QualifiedRule:
    def __init__(self, prelude=None, block=None):
        if prelude is None:
            self.prelude = []
        else:
            self.prelude = prelude
        self.block = block

    def __repr__(self):
        base = "".join([str(token.value) for token in self.prelude if token.value is not None])
        if self.block:
            base += " " + str(self.block)
        return base


class Declaration:
    def __init__(self, name=None, value=None, important=False):
        self.name = name
        if value is None:
            self.value = []
        else:
            self.value = value
        self.important = important

    def __repr__(self):
        return f"{self.name}: {self.value};"


class CSSFunction:
    def __init__(self, name, value=None):
        self.name = name
        if value is None:
            self.value = []
        else:
            self.value = value

    def __repr__(self):
        return f"{self.name}({self.value[1:-1]})"


class SimpleBlock:
    def __init__(self, associated_token, value=None):
        self.associated_token = associated_token
        if value is None:
            self.value = []
        else:
            self.value = value

    def __repr__(self):
        values = ",\n".join([str(token.value) for token in self.value if token.value is not None])
        return f"{{\n{values}\n}}"
