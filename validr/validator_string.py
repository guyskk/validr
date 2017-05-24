import json

from pyparsing import (
    Dict, FollowedBy, Forward, Group, Keyword, Optional, ParseBaseException,
    StringEnd, StringStart, Suppress, Word, ZeroOrMore, alphanums, alphas,
    dblQuotedString, delimitedList, originalTextFor, pyparsing_common,
    removeQuotes, replaceWith
)

from ._exception import SchemaError


def _make_keyword(kwd_str, kwd_value):
    return Keyword(kwd_str).setParseAction(replaceWith(kwd_value))


def _define_json():
    # https://pyparsing.wikispaces.com/file/view/jsonParser.py
    TRUE = _make_keyword('true', True)
    FALSE = _make_keyword('false', False)
    NULL = _make_keyword('null', None)

    LBRACK, RBRACK, LBRACE, RBRACE, COLON = map(Suppress, '[]{}:')

    jsonString = dblQuotedString().setParseAction(removeQuotes)
    jsonNumber = pyparsing_common.number()

    jsonObject = Forward()
    jsonValue = Forward()
    jsonElements = delimitedList(jsonValue)
    jsonArray = Group(LBRACK + Optional(jsonElements, []) + RBRACK)
    jsonValue << (jsonString | jsonNumber | Group(jsonObject) | jsonArray | TRUE | FALSE | NULL)  # noqa
    memberDef = Group(jsonString + COLON + jsonValue)
    jsonMembers = delimitedList(memberDef)
    jsonObject << Dict(LBRACE + Optional(jsonMembers) + RBRACE)
    return jsonValue


def _define_vs():
    KEY = Word(alphas + '_$', alphanums + '_$').setName('identifier').setResultsName('key')  # noqa
    VALUE = originalTextFor(_define_json()).setResultsName('value')
    # validator name, eg: int
    NAME = Optional(Optional(Suppress('?')) + pyparsing_common.identifier.setResultsName('name'))  # noqa
    # refers, eg: @xx@yy
    REFERS = Group(ZeroOrMore(Suppress('@') + pyparsing_common.identifier)).setResultsName('refers')  # noqa
    # args, eg: (), (1), (1,2,3), ([1,2], {"key":"value"}, "Any JSON")
    ARGS = Group(Optional(Suppress('(') + Optional(delimitedList(VALUE)) + Suppress(')'))).setResultsName('args')  # noqa
    # key-value, eg: key, key=True, key=[1,2,3]
    KW = Group(KEY + Optional(Suppress('=') + VALUE))
    # kwargs, eg: &key1&key2=True&key3=[1,2,3]
    KWARGS = Group(ZeroOrMore(Suppress('&') + KW)).setResultsName('kwargs')
    # lead xxx is key: xxx@yyy, xxx?yyy, $self&abc
    # lead xxx except '$self' is validator name: xxx(1,2), xxx&abc, xxx
    VS_KEY = Optional((KEY + FollowedBy(Word('@?'))) | Keyword('$self'))
    VS_DEF = REFERS + NAME + ARGS + KWARGS
    return StringStart() + VS_KEY + VS_DEF + StringEnd()


VS_GRAMMAR = _define_vs()


class ValidatorString:
    """ValidatorString

    eg::
        int(0,"JSON")&k1&k2="JSON"
        key?int(0,"JSON")&k1&k2="JSON"
        key@xx@yy(0,"JSON")&k1&k2="JSON"
    """

    def __init__(self, text):

        if text is None:
            raise SchemaError("can't parse None")

        try:
            result = VS_GRAMMAR.parseString(text.strip(), parseAll=True)
        except ParseBaseException as ex:
            msg = 'invalid syntax in col {} of {}'\
                .format(ex.col, repr(ex.line))
            raise SchemaError(msg) from None

        self.key = str(result.key) or None
        self.refers = [str(x) for x in result.refers] or None
        if self.refers and not all(self.refers):
            raise SchemaError("refer name can't be empty")
        self.name = str(result.name) or None
        if self.refers and self.name:
            raise SchemaError("refer and validator can't both exist")
        args = []
        for x in result.args:
            try:
                args.append(json.loads(str(x)))
            except ValueError:
                raise SchemaError('invalid JSON value in {}'.format(str(x)))
        self.args = tuple(args)
        kwargs = {}
        for x in result.kwargs:
            if x.value:
                try:
                    value = json.loads(str(x.value))
                except ValueError:
                    msg = 'invalid JSON value in %s' % repr(str(x.value))
                    raise SchemaError(msg)
            else:
                value = True
            kwargs[str(x.key)] = value
        self.kwargs = kwargs

    def __repr__(self):
        return 'ValidatorString({})'.format(repr({
            k: getattr(self, k, None)
            for k in ['key', 'name', 'refers', 'args', 'kwargs']
            if hasattr(self, k)
        }))
