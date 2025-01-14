from pytest_mock import MockerFixture
from main import name_space_digit
from conftest import ack, MOCK_LEADERBOARD

def test_missing_user(mocker: MockerFixture,
                      mock_create_engine,
                      mock_get_sneezer_by_name):
    message = {'user': 'A', 'text': 'B 1'}
    say = mocker.Mock()
    mock_get_sneezer_by_slack_id = mocker.patch(
        "main.get_sneezer_by_slack_id",
        return_value=None)
    
    name_space_digit(message, say, ack)
    say.assert_called_once_with("Don't recognize ya")

def test_missing_sneezer(mocker: MockerFixture,
                         mock_create_engine,
                         mock_get_sneezer_by_slack_id):
    message = {'user': 'A', 'text': 'B 1'}
    say = mocker.Mock()
    mock_get_sneezer_by_name = mocker.patch(
        "main.get_sneezer_by_name",
        return_value=None)
    name_space_digit(message, say, ack)
    say.assert_called_once_with("I'm not tracking any sneezes for that name")

def test_zero_handled(mocker: MockerFixture,
                      mock_create_engine,
                      mock_get_sneezer_by_slack_id,
                      mock_get_sneezer_by_name):
    message = {'user': 'A', 'text': 'B 0'}
    say = mocker.Mock()
    name_space_digit(message, say, ack)
    say.assert_called_once_with("Zero sneezes, huh wise guy?")

def test_too_many_sneezes(mocker: MockerFixture,
                          mock_create_engine,
                          mock_get_sneezer_by_slack_id,
                          mock_get_sneezer_by_name):
    message = {'user': 'A', 'text': 'B 26'}
    say = mocker.Mock()
    name_space_digit(message, say, ack)
    say.assert_called_once_with("26 sneezes?! Stop the game and call a DOCTOR")

def test_one_sneeze(mocker: MockerFixture,
                    mock_create_engine,
                    mock_get_sneezer_by_slack_id,
                    mock_get_sneezer_by_name,
                    mock_produce_leaderboard,
                    mock_add_sneeze_to_sneezer):
    message = {'user': 'A', 'text': 'B 1'}
    say = mocker.Mock()
    name_space_digit(message, say, ack)
    say.assert_any_call("A logging 1 sneeze for B...")
    say.assert_any_call(MOCK_LEADERBOARD)
    assert say.call_count == 2
    assert mock_add_sneeze_to_sneezer.call_count == 1

def test_multiple_sneeze(mocker: MockerFixture,
                         mock_create_engine,
                         mock_get_sneezer_by_slack_id,
                         mock_get_sneezer_by_name,
                         mock_produce_leaderboard,
                         mock_add_sneeze_to_sneezer):
    message = {'user': 'A', 'text': 'B 3'}
    say = mocker.Mock()
    name_space_digit(message, say, ack)
    say.assert_any_call("A logging 3 sneezes for B...")
    say.assert_any_call(MOCK_LEADERBOARD)
    assert say.call_count == 2
    assert mock_add_sneeze_to_sneezer.call_count == 3
