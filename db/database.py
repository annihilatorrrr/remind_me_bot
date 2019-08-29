import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json
import datetime 
from dateutil.parser import parse
# from actions.remind import remind

load_dotenv()

engine = create_engine(os.environ['DB_URL'])
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Remind(Base):
    __tablename__ = 'reminds'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    remind_time = Column(String(20))
    remind_text = Column(String(100))
    expired = Column(Boolean, default=False)
    done = Column(Boolean, default=False)


    def __init__(self, chat_id, remind_time, remind_text, expired, done):
        self.chat_id = chat_id
        self.remind_time = remind_time
        self.remind_text = remind_text
        self.expired = expired
        self.done = done



class RemindEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Remind):
            return obj.__dict__


# Generate database schema
Base.metadata.create_all(engine)

# Create new remind in DB
def create_remind(chat_id, time, text, expired=False, done=False):
    # Create a new session
    session = Session()
    parsed_time = parse(time)
    remind = Remind(chat_id, parsed_time, text, expired, done)
    session.add(remind)
    # Commit and close session
    session.commit()
    session.close()


def update_remind(chat_id, id, time, text):
    session = Session()
    session.query(Remind).filter_by(chat_id=chat_id).filter_by(id=id).update({"remind_time": parse(time), "remind_text": text})
    
    # Commit and close session
    session.commit()
    session.close()


# update_remind(chat_id=365899971, id=2, time='2019-08-30 22:22:00', text='change')


def expire_remind(delete_id):
    session = Session()
    session.query(Remind).filter_by(id=delete_id[0]).update({"expired": True}, synchronize_session=False)

    # Commit and close session
    session.commit()
    session.close()


def get_reminds(user_chat_id):
    session = Session()
    # Select all reminds with expired == False, user is defined by chat_id
    reminds_list = session.query(Remind).order_by(Remind.id).filter_by(expired=False).filter_by(chat_id=user_chat_id).all()
    json_data = json.loads(json.dumps(reminds_list, cls=RemindEncoder, indent=4))
    
    # Close session
    session.close()
    return json_data


def check_remind():
    session = Session()
    current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
    remind = session.query(Remind).filter_by(remind_time=current_time).filter_by(expired=False).all()

    remind_j = json.loads(json.dumps(remind, cls=RemindEncoder, indent=4))
    if remind_j: 
        return remind_j

    # Close session
    session.close()


def close_remind(user_chat_id):
    session = Session()
    last_remind_id = session.query(Remind).filter_by(chat_id=user_chat_id).filter_by(done=False).order_by(Remind.id).first()
    print(last_remind_id.id)

    # TODO 
    # handle if there is no 'not done' reminds
    session.query(Remind).filter_by(id=last_remind_id.id).update({"done": True}, synchronize_session=False)

    # Commit and close session
    session.commit()
    session.close()


def delete_remind(delete_id):
    session = Session()
    for i in delete_id:
        session.query(Remind).filter_by(id=i).delete(synchronize_session=False)

    # Commit and close session
    session.commit()
    session.close()

