from terminaltables import AsciiTable


_NOT_SET = object()


cpdef shorten(str text, int length):
    if len(text) > length:
        return text[:length] + '..'
    return text


cpdef _format_error(args, str position, str value_clause=None):
    cdef str msg = str(args[0]) if args else 'invalid'
    if position:
        msg = '%s: %s' % (position, msg)
    if value_clause:
        msg = '%s, %s' % (msg, value_clause)
    return msg


class ValidrError(ValueError):
    """Base exception of validr"""

    def __init__(self, *args, value=_NOT_SET, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = value
        # marks item: (is_key, index_or_key)
        self.marks = []

    def mark_index(self, int index=-1):
        self.marks.append((False, index))
        return self

    def mark_key(self, str key):
        self.marks.append((True, key))
        return self

    @property
    def has_value(self):
        """Check has value set"""
        return self._value is not _NOT_SET

    def set_value(self, value):
        """Set value if not set"""
        if self._value is _NOT_SET:
            self._value = value

    @property
    def value(self):
        """The invalid value"""
        if self._value is _NOT_SET:
            return None
        return self._value

    @property
    def field(self):
        """First level index or key, usually it's the field"""
        if not self.marks:
            return None
        __, index_or_key = self.marks[-1]
        return index_or_key

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
        return _format_error(self.args, self.position)


class Invalid(ValidrError):
    """Data invalid"""
    def __str__(self):
        cdef str value_clause = None
        if self.has_value:
            value_clause = 'value=%s' % shorten(str(self.value), 75)
        return _format_error(self.args, self.position, value_clause)


class ModelInvalid(Invalid):
    """Model data invalid"""
    def __init__(self, errors):
        if not errors:
            raise ValueError('errors is required')
        self.errors = errors
        message = errors[0].message or 'invalid'
        message += ' ...total {} errors'.format(len(errors))
        super().__init__(message)

    def __str__(self):
        error_items = [(ex.position, ex.message) for ex in self.errors]
        table = [("Key", "Error")] + error_items
        return '\n' + AsciiTable(table).table


class SchemaError(ValidrError):
    """Schema error"""
    def __str__(self):
        cdef str value_clause = None
        if self.has_value:
            value_clause = 'schema=%s' % self.value.repr(prefix=False, desc=False)
        return _format_error(self.args, self.position, value_clause)


cdef class mark_index:
    """Add current index to Invalid/SchemaError"""

    cdef int index

    def __init__(self, index=-1):
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
