import psycopg2
conn = psycopg2.connect(host='localhost', port=5433, dbname='ecommerce', user='admin', password='changeme')
cur = conn.cursor()
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2")
for row in cur.fetchall():
    print(row)
conn.close()