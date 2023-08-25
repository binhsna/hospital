import functools
import json
import logging
import pickle
from odoo.tools import config
from redis.cluster import ClusterNode
from redis.cluster import RedisCluster
from werkzeug.contrib.sessions import SessionStore

_logger = logging.getLogger(__name__)

SESSION_TIMEOUT = 60 * 60 * 24 * 1


def retry_redis(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        for attempts in range(1, 6):
            try:
                return func(self, *args, **kwargs)
            except Exception as error:
                _logger.error("Lỗi Redis connection failed! (%s/5)" % attempts)
                if attempts >= 5:
                    raise error

    return wrapper


class RedisConfig:
    MAX_CONNECTIONS = int(config.get('session_store_max_connections', 0))
    PASSWORD = str(config.get('session_store_pass', ''))
    startup_nodes = config.get('session_store_nodes', '')


REDIS_CONNECTION_PARAMS = {
    'max_connections': RedisConfig.MAX_CONNECTIONS,
    'password': RedisConfig.PASSWORD,
    # 'encoding': 'utf-8',
    # 'decode_responses': True
}


class RedisSessionStore(SessionStore):

    def __init__(self, *args, **kwargs):
        super(RedisSessionStore, self).__init__(*args, **kwargs)
        self.prefix = config.get('session_store_prefix', '')
        nodes = list()
        # for item in RedisConfig.startup_nodes:
        for item in json.loads(RedisConfig.startup_nodes):
            nodes.append(ClusterNode(host=item.get('host'), port=item.get('port')))
        self.server = RedisCluster(startup_nodes=nodes, **REDIS_CONNECTION_PARAMS, health_check_interval=30)

    def _get_session_key(self, sid):
        key = (self.prefix + sid).encode('utf-8')
        if isinstance(sid, str):
            return key
        else:
            return sid

    @retry_redis
    def save(self, session):
        key = self._get_session_key(session.sid)
        payload = pickle.dumps(dict(session), pickle.HIGHEST_PROTOCOL)
        self.server.setex(name=key, time=SESSION_TIMEOUT, value=payload)

    @retry_redis
    def delete(self, session):
        self.server.delete(self._get_session_key(session.sid))

    @retry_redis
    def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()
        key = self._get_session_key(sid)
        payload = self.server.get(key)
        if payload:
            # self.server.setex(name=key, value=payload, time=SESSION_TIMEOUT)
            return self.session_class(pickle.loads(payload), sid, False)
        else:
            return self.session_class({}, sid, False)
