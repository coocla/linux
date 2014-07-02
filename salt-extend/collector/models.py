"""
SQLAlchemy models
"""
import datetime
import log as logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
logging.setup_log(root=__file__, LogDir=logging.options["LogDir"], LogLevel=logging.options["LogLevel"])
LOG = logging.getLogger(__name__)

def gettimestamp():
    return int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

class Assets(Base):
    __tablename__ = "assets"
    id = Column(String(64), primary_key = True)
    type = Column(String(64))
    updated_at = Column(BigInteger(), 
        default=gettimestamp(), onupdate=gettimestamp())
    property = Column(JSON())

    def update(self, values):
        for k, v in values.iteritems():
            setattr(self, k, v)

    def save(self, session=None):
        if not session:
            session = get_session()
        session.add(self)
        try:
            session.flush()
        except IntegrityError, e:
            if str(e).endswith('is not unique'):
                raise exception.Duplicate(str(e))
            else:
                raise


def get_engine():
    engine = create_engine(logging.options["sql_connect"], echo=False)
    return engine


def get_session(autocommit=True, expire_on_commit=False):
    Session = sessionmaker(bind=get_engine(),
            autocommit = autocommit,
            expire_on_commit = expire_on_commit)
    session = Session()

    return session


def model_query(*args, **kwargs):
    session = get_session()
    query = session.query(*args)
    return query


def get_by_id(id):
    return model_query(Assets).filter_by(id=id).first()


def insert_or_update(values):
    keys = ["id", "type", "property"]
    if set(keys) != set(values):
        LOG.error("Does not meet the specified key %s" % str(values.keys()))
        return
    if not isinstance(values.get("property", ''), dict):
        LOG.error("%s property is not dict" % values["id"])
        return

    assets = get_by_id(values["id"])
    if assets:
        if cmp(assets.property, values["property"]):
            property = dict(assets.property)
            property.update(values["property"])
            assets.update({"property": property})
            assets.save()
            LOG.debug("update assets for %s" % values["id"])
            return
        else:
            LOG.debug("assets %s has not update, continue" % values["id"])
            return
    assets = Assets()
    assets.update(values)
    assets.save()
    LOG.debug("assets %s add" % values["id"])
    return assets

Assets.metadata.create_all(get_engine())
