import random
import logging

from odoo import http, tools
from odoo.http import request
from odoo.tools.func import lazy_property

from odoo.addons.muk_utils.tools.patch import monkey_patch
from odoo.addons.muk_session_store.store.postgres import PostgresSessionStore
from odoo.addons.muk_session_store.store.redis import RedisSessionStore

_logger = logging.getLogger(__name__)

try:
    import redis
except ImportError:
    if tools.config.get('session_store_redis'):
        _logger.warning("The Python library redis is not installed.")
    redis = False


def get_session_store_database():
    return tools.config.get('session_store_dbname', 'session_store')


@monkey_patch(http)
def db_monodb(httprequest=None):
    if tools.config.get('session_store_database'):
        httprequest = httprequest or request.httprequest
        dbs = http.db_list(True, httprequest)
        store = get_session_store_database()
        db_session = httprequest.session.db
        if db_session in dbs:
            return db_session
        if store in dbs:
            dbs.remove(store)
        if len(dbs) == 1:
            return dbs[0]
        return None
    else:
        return db_monodb.super(httprequest)


@monkey_patch(http)
def db_filter(dbs, httprequest=None):
    dbs = db_filter.super(dbs, httprequest=httprequest)
    store = get_session_store_database()
    if store in dbs:
        dbs.remove(store)
    return dbs


@monkey_patch(http)
def session_gc(session_store):
    if tools.config.get('session_store_database'):
        if random.random() < 0.001:
            session_store.clean()
    elif tools.config.get('session_store_redis'):
        pass
    else:
        session_gc.super(session_store)


class Root(http.Root):
    @lazy_property
    def session_store(self):
        if tools.config.get('session_store_database'):
            return PostgresSessionStore(session_class=http.OpenERPSession)
        elif tools.config.get('session_store_redis') and redis:
            return RedisSessionStore(session_class=http.OpenERPSession)
        return super(Root, self).session_store


http.root = Root()
