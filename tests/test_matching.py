import pytest

from distributed_websocket._matching import matches


def test_matches_01():
    assert matches('a', {'a'})
    assert matches('a', {'a', 'b'})
    assert matches('a', {'a', 'b', 'c'})
    assert matches('a', {'a', 'b', 'c', 'd'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e', 'f'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e', 'f', 'g'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'})
    assert matches('a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'})
    assert matches(
        'a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'}
    )
    assert matches(
        'a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'}
    )
    assert matches(
        'a', {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'}
    )


def test_matches_02():
    assert matches('root/sub1/sub2', {'root/sub2/sub2', 'root/sub1/sub2'})
    assert matches('root/sub1/sub2', {'root/sub2/sub2', 'root/sub1/+'})
    assert matches('root/sub1/sub2', {'root/sub2/sub2', 'root/#'})
    assert matches('root/sub1/sub2', {'root/sub2/sub2', 'root/+/sub2'})
    assert matches('root/sub1/sub2', {'root/sub2/sub2', 'root/sub1/#'})
    assert matches('root/sub1/sub2', {'root/sub2/sub2', '+/sub1/sub2'})
    assert matches('root/sub1/sub2', {'root/sub2/sub2', '#/sub1/sub2'})
    assert not matches('root/sub1/sub2', {'root/sub2/sub2', 'root/sub1/sub3'})
    assert not matches('root/sub1/sub2', {'root/sub2/sub2', 'root/sub1/sub3/#'})
    assert not matches('root/sub1/sub2', {'root/sub2/sub2', 'root/+'})
    assert not matches('root/sub1/sub2', {'root/sub2/sub2', '+/sub2'})


def test_matches_03():
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/sub2/sub2'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/sub2/+'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/+/+'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/#'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/+/sub2/sub2'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/+/sub2'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/sub2/#'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', '+/sub1/sub2/sub2'})
    assert matches('root/sub1/sub2/sub2', {'root/sub2/sub2', '#/sub1/sub2/sub2'})
    assert not matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/sub2/sub3'})
    assert not matches(
        'root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub1/sub2/sub3/#'}
    )
    assert not matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/+/+'})
    assert not matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/+/sub2'})
    assert not matches('root/sub1/sub2/sub2', {'root/sub2/sub2', 'root/sub2/+/sub2'})
    assert not matches('root/sub1/sub2/sub2', {'root/sub2/sub2', '+/sub2/sub2'})
