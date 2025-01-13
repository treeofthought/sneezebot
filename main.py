import re
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import Session
from models import Sneezer, Sneeze

DIGIT_ONLY = "^\d+$"
NAME_SPACE_DIGIT = "^[a-zA-Z]+ \d+$"

load_dotenv()

# Load DB engine
url = os.environ.get('DATABASE_URL')
# Heroku URL doesn't play nice w/ psycopg2
url = url.replace('postgres://', 'postgresql://')
engine = create_engine(url)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def get_sneezer_by_slack_id(slack_user_id):
    with Session(engine) as session:
        sneezer = session.scalars(
            select(Sneezer).where(Sneezer.slack_user_id == slack_user_id)).first()
        return sneezer
    
def get_sneezer_by_name(name):
    with Session(engine) as session:
        sneezer = session.scalars(
            select(Sneezer).where(func.lower(Sneezer.name) == name.lower())).first()
        return sneezer

def add_sneeze_to_sneezer(sneezer):
    with Session(engine) as session:
        newSneeze = Sneeze(sneezer_id=sneezer.id)
        session.add(newSneeze)
        session.commit()


def produce_leaderboard():
    with Session(engine) as session:
        allSneezers = session.scalars(select(Sneezer)).all()
        sorted_sneezers = sorted(allSneezers, reverse=True) 
        leaderboard = ["*Sneeze Leaderboard*"]
        for index, logSneezer in enumerate(sorted_sneezers):
            leaderboard.append(f"{index + 1}. {logSneezer.name}: {logSneezer.sneeze_count}")
        return '\n'.join(leaderboard)

@app.message(re.compile(DIGIT_ONLY))
def digit_only(message, say, ack):
    ack()
    slack_user_id = message['user']
    sender = get_sneezer_by_slack_id(slack_user_id)
    if sender is None:
        say("Don't recognize ya")
        return
    text = message['text']
    if text == "0":
        say("Zero sneezes, huh wise guy?")
        return
    grammar = 's'
    if text == "1":
        grammar = ''
    say(f"Logging {text} sneeze{grammar} for {sender.name}...")
    for index in range(int(text)):
        add_sneeze_to_sneezer(sender)
    
    leaderboard = produce_leaderboard()
    say(leaderboard)

@app.message(re.compile(NAME_SPACE_DIGIT))
def name_space_digit(message, say, ack):
    ack()
    slack_user_id = message['user']
    sender = get_sneezer_by_slack_id(slack_user_id)
    if sender is None:
        say("Don't recognize ya")
        return
    
    text_parts = message['text'].split(' ')
    name, count = text_parts[0], int(text_parts[1])

    if count == "0":
        say("Zero sneezes, huh wise guy?")
        return

    if count > 25:
        say("I don't log more than 25 sneezes at a time")
        return

    grammar = 's'
    if count == 1:
        grammar = ''

    sneezer = get_sneezer_by_name(name)
    if sneezer is None:
        say(f"I'm not tracking sneezes for {name}")
        return
    say(f"{sender.name} logging {count} sneeze{grammar} for {name}")
    for index in range(count):
        add_sneeze_to_sneezer(sneezer)

    leaderboard = produce_leaderboard()
    say(leaderboard)
    

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()