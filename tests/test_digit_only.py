from pytest_mock import MockerFixture
from main import digit_only
from conftest import ack, MOCK_LEADERBOARD


# TODO needing the mock_create_engine (etc) is magical...
#      local sqlite!
#      but then need an app factory (or something)
#      ...dependency injection?

def test_missing_user(mocker: MockerFixture,
                      mock_create_engine):
    message = {'user': 'A', 'text': '1'}
    say = mocker.Mock()
    mock_get_sneezer_by_slack_id = mocker.patch(
        "main.get_sneezer_by_slack_id",
        return_value=None)
    digit_only(message, say, ack)
    say.assert_called_once_with("Don't recognize ya")

def test_zero_handled(mocker: MockerFixture,
                      mock_create_engine,
                      mock_get_sneezer_by_slack_id):
    message = {'user': 'A', 'text': '0'}
    say = mocker.Mock()
    digit_only(message, say, ack)
    say.assert_called_once_with("Zero sneezes, huh wise guy?")

def test_one_sneeze(mocker: MockerFixture,
                    mock_create_engine,
                    mock_get_sneezer_by_slack_id,
                    mock_produce_leaderboard,
                    mock_add_sneeze_to_sneezer):
    message = {'user': 'A', 'text': '1'}
    say = mocker.Mock()
    digit_only(message, say, ack)
    say.assert_any_call("Logging 1 sneeze for A...")
    say.assert_any_call(MOCK_LEADERBOARD)
    assert say.call_count == 2
    assert mock_add_sneeze_to_sneezer.call_count == 1

def test_multiple_sneeze(mocker: MockerFixture,
                         mock_create_engine,
                         mock_get_sneezer_by_slack_id,
                         mock_produce_leaderboard,
                         mock_add_sneeze_to_sneezer):
    message = {'user': 'A', 'text': '3'}
    say = mocker.Mock()
    digit_only(message, say, ack)
    say.assert_any_call("Logging 3 sneezes for A...")
    say.assert_any_call(MOCK_LEADERBOARD)
    assert say.call_count == 2
    assert mock_add_sneeze_to_sneezer.call_count == 3

def test_too_many_sneezes(mocker: MockerFixture,
                          mock_create_engine,
                          mock_get_sneezer_by_slack_id):
    message = {'user': 'A', 'text': '26'}
    say = mocker.Mock()
    digit_only(message, say, ack)
    say.assert_called_once_with("26 sneezes?! Stop the game and call a DOCTOR")
