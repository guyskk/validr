from validr import Invalid


def test_exception_message():
    assert Invalid("invalid").message == "invalid"
    assert Invalid().message is None


def test_exception_position():
    ex = Invalid("invalid").mark_index(0).mark_key("key")
    assert ex.position == "key[0]"
    assert ex.position in str(ex)
    assert ex.message in str(ex)
    ex = Invalid("invalid").mark_key("key").mark_index(0)
    assert ex.position == "[0].key"
    assert ex.position in str(ex)
    assert ex.message in str(ex)


def test_exception_str():
    ex = Invalid("invalid").mark_index(0).mark_key("key")
    assert str(ex) == "invalid in key[0]"

    ex = Invalid().mark_index(0).mark_key("key")
    assert str(ex) == "in key[0]"

    ex = Invalid("invalid")
    assert str(ex) == "invalid"

    ex = Invalid()
    assert str(ex) == ""
