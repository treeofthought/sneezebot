from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import func


Base = declarative_base()

class Sneezer(Base):
    __tablename__ = 'sneezers'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    slack_user_id = Column(String(9), nullable=True, unique=True)
    sneezes = relationship("Sneeze", backref="sneezer") 
    
    @property
    def sneeze_count(self):
        return len(self.sneezes)
    
    def __lt__(self, other):
        if len(self.sneezes) < len(other.sneezes):
            return True
        elif len(self.sneezes) > len(other.sneezes):
            return False
        else:  # If sneeze_count is equal, compare names alphabetically
            return self.name < other.name
    
class Sneeze(Base):
    __tablename__ = 'sneezes'
    id = Column(Integer(), primary_key=True)
    sneezer_id = Column(Integer(), ForeignKey('sneezers.id'))
    created_at = Column(DateTime, server_default=func.now()) 

# Code for crudely rebuilding the database...
# EXCLUDES SNEEZE DATA!!!

# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)

# Jordan = Sneezer(name='Jordan', slack_user_id='UFGNMPK7S')
# Stu = Sneezer(name='Stu', slack_user_id='UFKHJQN65')
# Pat = Sneezer(name='Pat', slack_user_id='UFH9MT6VA')
# Nate = Sneezer(name='Nate', slack_user_id='UFWTCKWM8')
# Krista = Sneezer(name='Krista')
# DC = Sneezer(name='DC')
# Max = Sneezer(name='Max', slack_user_id='UFMPEJ5PT')
# Jeff = Sneezer(name='Jeff', slack_user_id='UFNJXE0RK')
# Zook = Sneezer(name='Zook', slack_user_id='UFNBKNMHA')
# Tone = Sneezer(name='Tone', slack_user_id='UFPE1AA7P')

# with Session(engine) as session:
#     session.add_all([Jordan, Stu, Pat, Nate, Krista, DC, Max, Jeff, Zook, Tone])
#     session.commit()