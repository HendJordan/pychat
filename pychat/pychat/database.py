from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#UPDATE WITH YOUR MYSQL USERNAME AND PASSWORD
engine = create_engine(
                "mysql://mysqlusername:password@localhost/broschat"
        )

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
def init_db():
    # import all models
    import models
    Base.metadata.create_all(bind=engine)

