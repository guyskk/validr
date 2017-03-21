class ValidrError(ValueError):
    """Mark invalid position"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # marks' item: (is_key, index_or_key)
        self.marks = []

    def mark_index(self, int index):
        self.marks.append((False, index))
        return self

    def mark_key(self, str key):
        self.marks.append((True, key))
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
        cdef str text = ''
        cdef bint is_key
        for is_key, index_or_key in reversed(self.marks):
            if is_key:
                text = '%s.%s' % (text, index_or_key)
            else:
                if index_or_key == -1:
                    text = '%s[]' % text
                else:
                    text = '%s[%d]' % (text, index_or_key)
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
        cdef str position = self.position
        if self.args:
            if position:
                return '%s in %s' % (self.args[0], position)
            else:
                return self.args[0]
        else:
            if position:
                return 'in %s' % position
            else:
                return super().__str__()


class Invalid(ValidrError):
    """Data invalid"""


class SchemaError(ValidrError):
    """Schema error"""


cdef class mark_index:
    """Add current index to Invalid/SchemaError"""

    cdef int index

    def __init__(self, index):
        """index = -1 means the position is uncertainty"""
        self.index = index

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, ValidrError):
            exc_val.mark_index(self.index)


cdef class mark_key:
    """Add current key to Invalid/SchemaError"""

    cdef str key

    def __init__(self, key):
        self.key = key

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, ValidrError):
            exc_val.mark_key(self.key)
