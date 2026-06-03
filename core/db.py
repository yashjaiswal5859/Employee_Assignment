from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

master_engine = None
replica_engine = None
MasterSession = None
ReplicaSession = None


def init_db_connections(app):
    global master_engine, replica_engine, MasterSession, ReplicaSession

    master_url = app.config['MASTER_DATABASE_URL']
    replica_url = app.config['REPLICA_DATABASE_URL']

    master_engine = create_engine(master_url)
    replica_engine = create_engine(replica_url)

    MasterSession = sessionmaker(bind=master_engine, autoflush=False, expire_on_commit=False)
    ReplicaSession = sessionmaker(bind=replica_engine, autoflush=False, expire_on_commit=False)


def get_master_session():
    if MasterSession is None:
        raise RuntimeError('Master DB session is not initialized. Call init_db_connections(app) first.')
    return MasterSession()


def get_replica_session():
    if ReplicaSession is None:
        raise RuntimeError('Replica DB session is not initialized. Call init_db_connections(app) first.')
    return ReplicaSession()
