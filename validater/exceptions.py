class ValidaterError(ValueError):
    """Mark invalid position"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # marks' item: (is_key, index_or_key)
        self.marks = []

    def mark_index(self, index):
        self.marks.insert(0, (False, index))
        return self

    def mark_key(self, key):
        self.marks.insert(0, (True, key))
        return self

    @property
    def position(self):
        """A string which represent the position of invalid.

        For example:

            {
                "tags": ["ok", "invalid"],  # tags[1]
                "user": {
                    "name": "invalid",      # user.name
                    "age": 500              # user.age
                }
            }
        """
        text = ""
        for is_key, index_or_key in self.marks:
            if is_key:
                text = "%s.%s" % (text, index_or_key)
            else:
                if index_or_key is None:
                    text = "%s[]" % text
                else:
                    text = "%s[%d]" % (text, index_or_key)
        if text and text[0] == '.':
            text = text[1:]
        return text

    @property
    def message(self):
        """Error message"""
        if self.args:
            return self.args[0]
        else:
            return None

    def __str__(self):
        position = self.position
        if self.args:
            if position:
                return "%s in %s" % (self.args[0], position)
            else:
                return self.args[0]
        else:
            if position:
                return "in %s" % position
            else:
                return super().__str__()


class Invalid(ValidaterError):
    """Data invalid"""


class SchemaError(ValidaterError):
    """Schema error"""
