from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import credentials

connection_string = "mysql+pymysql://" + credentials.username + ":" + credentials.password + "@" + credentials.aws_endpoint + ":3306/" + credentials.db_name

Base = declarative_base()
engine = create_engine(connection_string)
db_user = credentials.username

# start a session
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()