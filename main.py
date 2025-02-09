import re
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import Session
from models import Sneezer, Sneeze

DIGIT_ONLY = r"^\d+\s*$"
NAME_SPACE_DIGIT = r"^[a-zA-Z]+ \d+\s*$"
LEADERBOARD = r"^LEADERBOARD$"

load_dotenv()

# Load DB engine
url = os.environ.get('DATABASE_URL')
# Heroku URL doesn't play nice w/ psycopg2
url = url.replace('postgres://', 'postgresql://')
engine = create_engine(url)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def grammar(count):
    if count == 1:
        return ''
    return 's'

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

def write_leaderboard_entry(logSneezer):
    sneezeCount = logSneezer.sneeze_count
    name = logSneezer.name
    normalOutput = f'{name}: {sneezeCount}'
    if sneezeCount == 69:
        return f'{normalOutput} (Nice)'
    elif sneezeCount == 420:
        return f'{normalOutput} (Blaze it)'
    elif sneezeCount == 29:
        return f'{normalOutput} (29 PAYS)'
    else:
        return normalOutput
    

def produce_leaderboard():
    with Session(engine) as session:
        allSneezers = session.scalars(select(Sneezer)).all()
        sorted_sneezers = sorted(allSneezers, reverse=True) 
        leaderboard = ["*Der Gesundesliga*"]
        for index, logSneezer in enumerate(sorted_sneezers):
            leaderboard.append(f"{index + 1}. {write_leaderboard_entry(logSneezer)}")
        return '\n'.join(leaderboard)

def validate_tracking_params(count, sender, sneezer):
    if count == 0:
        return "Zero sneezes, huh wise guy?"
    if count > 25:
        return f"{count} sneezes?! Stop the game and call a DOCTOR"
    if sender is None:
        return "Don't recognize ya"
    if sneezer is None:
        return "I'm not tracking any sneezes for that name"

@app.message(re.compile(LEADERBOARD))
def leaderboard(say, ack):
    ack()
    leaderboard = produce_leaderboard()
    say(leaderboard)

@app.message(re.compile(DIGIT_ONLY))
def digit_only(message, say, ack):
    ack()
    count = int(message['text'])
    slack_user_id = message['user']
    sender = get_sneezer_by_slack_id(slack_user_id)
    objection = validate_tracking_params(count, sender, sender)
    if objection:
        say(objection)
        return

    say(f"Logging {count} sneeze{grammar(count)} for {sender.name}...")
    for index in range(count):
        add_sneeze_to_sneezer(sender)
    
    leaderboard = produce_leaderboard()
    say(leaderboard)

@app.message(re.compile(NAME_SPACE_DIGIT))
def name_space_digit(message, say, ack):
    ack()
    slack_user_id = message['user']
    text_parts = message['text'].split(' ')
    name, count = text_parts[0], int(text_parts[1])

    sneezer = get_sneezer_by_name(name)
    sender = get_sneezer_by_slack_id(slack_user_id)
    objection = validate_tracking_params(count, sender, sneezer)
    if objection:
        say(objection)
        return
    say(f"{sender.name} logging {count} sneeze{grammar(count)} for {name}...")
    for index in range(count):
        add_sneeze_to_sneezer(sneezer)

    leaderboard = produce_leaderboard()
    say(leaderboard)
    

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()