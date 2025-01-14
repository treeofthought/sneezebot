import re
from main import DIGIT_ONLY, NAME_SPACE_DIGIT

def test_digit_only():
    regex = re.compile(DIGIT_ONLY)
    assert regex.match('1')
    assert not regex.match('-1')
    assert not regex.match('0.5')
    assert not regex.match(' 1')
    assert not regex.match('A')

def test_name_space_digit():
    regex = re.compile(NAME_SPACE_DIGIT)
    assert regex.match('Name 1')
    assert regex.match('Name 2')
    assert not regex.match('This is 2')
    assert not regex.match('Name only')
    assert not regex.match('Name -1')
    assert not regex.match('Name 0.5')
    