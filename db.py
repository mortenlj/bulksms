#!/usr/bin/env python
# -*- coding: utf-8

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

class Mapping(Base):
    __tablename__ = "mapping"
    __table_args__ = (
        UniqueConstraint('channel', 'preference'),
        )

    id = Column(Integer, primary_key=True)
    channel = Column(String(64), index=True)
    preference = Column(String(64))

    def __init__(self, channel, preference):
        self.channel = channel
        self.preference = preference

class Database(object):
    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = create_engine(db_url,
                                    connect_args={'check_same_thread':False},
                                    poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def close(self):
        self.engine.dispose()
        del self.engine

    def add_mapping(self, channel, preference):
        session = self.Session()
        mapping = Mapping(channel, preference)
        session.add(mapping)
        session.commit()

    def remove_mapping(self, channel, preference):
        session = self.Session()
        mapping = self.get_mapping(channel, preference)
        session.delete(mapping)
        session.commit()

    def get_mapping(self, channel, preference):
        session = self.Session()
        return session.query(Mapping)\
            .filter(Mapping.channel == channel)\
            .filter(Mapping.preference == preference)\
            .first()

    def has_mapping(self, channel, preference):
        return self.get_mapping(channel, preference) is not None

    def get_mappings(self, channel):
        session = self.Session()
        return session.query(Mapping)\
            .filter(Mapping.channel == channel)

if __name__ == "__main__":
    pass
