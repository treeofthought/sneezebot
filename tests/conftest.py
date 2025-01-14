import pytest
from pytest_mock import MockerFixture
ack = lambda: None
MOCK_LEADERBOARD = 'MOCKLEADERBOARD'

class MockSneezer:
    def __init__(self, name):
        self.name = name

@pytest.fixture
def mock_create_engine(mocker: MockerFixture):
    mock_engine = mocker.Mock()
    return mocker.patch("sqlalchemy.create_engine",
                        return_value=mock_engine)

@pytest.fixture
def mock_get_sneezer_by_slack_id(mocker: MockerFixture):
    return mocker.patch("main.get_sneezer_by_slack_id",
                        return_value=MockSneezer('A'))

@pytest.fixture
def mock_produce_leaderboard(mocker: MockerFixture):
    return mocker.patch("main.produce_leaderboard",
                        return_value=MOCK_LEADERBOARD)

@pytest.fixture
def mock_add_sneeze_to_sneezer(mocker: MockerFixture):
    return mocker.patch("main.add_sneeze_to_sneezer")

@pytest.fixture
def mock_get_sneezer_by_name(mocker: MockerFixture):
    return mocker.patch("main.get_sneezer_by_name",
                        return_value=MockSneezer('B'))