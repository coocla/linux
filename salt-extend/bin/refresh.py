from contextlib import contextmanager
import salt.config
try:
    import psycopg2
    HAS_PG = True
except:
    HAS_PG = False


def __virtual__():
    return HAS_PG

__opts__ = salt.config.client_config("/etc/salt/master")

@contextmanager
def db_call():
    conn = psycopg2.connect(
        user = __opts__["pg_user"],
        host = __opts__["pg_host"],
        port = __opts__["pg_port"],
        database = __opts__["pg_db"],
        password = __opts__["pg_pwd"],
    )
    cursor = conn.cursor()
    try:
        yield cursor
    except:
        pass
    finally:
        conn.close()


def data(lastmodified):
    try:
        lastmodified = int(lastmodified)
    except:
        raise TypeError("lastmodified not a int type")
    with db_call() as cur:
        sql = 'select id,type,property from assets where updated_at > %d' % lastmodified
        cur.execute(sql)
        data = cur.fetchall()
        ret = {}
        for single in data:
            single[2].update({"type": single[1]})
            ret[single[0]] = single[2]
        return ret
