import pytest

from myapp import models


def test_HTTPTargetBackend_init_with_bad_url():
    with pytest.raises(ValueError):
        models.HTTPTargetBackend("wrong-url")
