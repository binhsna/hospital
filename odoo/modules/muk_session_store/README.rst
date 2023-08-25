pip3 install redis ( Version mới nhất)



Configuration
=============

Cài module: muk_session_store


Parameter: ``--load=web,muk_session_store``



* session_store_database = True
* session_store_redis = True

**Postgres:**

* session_store_dbname
* session_store_dbtable

**Redis:**

* session_store_redis = True
* session_store_prefix = BTE
* session_store_nodes = [
        {"host": "10.163.135.136", "port": "32000"},
        {"host": "10.163.135.137", "port": "31871"},
        {"host": "10.163.135.138", "port": "31829"},
        {"host": "10.163.135.139", "port": "31183"},
        {"host": "10.163.135.140", "port": "31944"},
        {"host": "10.163.135.141", "port": "30459"}
    ]
* session_store_pass = oQn[DBSAXTY$
* session_store_max_connections = 600000
