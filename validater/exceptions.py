class ValidaterError(ValueError):
    """Mark invalid position"""

    def __init__(self, args=None):
        super().__init__(args)
        # marks' item: (is_key, index_or_key)
        self.marks = []

    def mark_index(self, index):
        self.marks.insert(0, (False, index))

    def mark_key(self, key):
        self.marks.insert(0, (True, key))

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

    def __str__(self):
        if self.args:
            return "%s in %s" % (self.args[0], self.position)
        else:
            return "in %s" % self.position


class Invalid(ValidaterError):
    """Data invalid"""


class SchemaError(ValidaterError):
    """Schema error"""
