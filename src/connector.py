import datetime
import os

import snowflake.connector
from flask import Blueprint, request, abort, jsonify, make_response

# Make the Snowflake connection

def connect() -> snowflake.connector.SnowflakeConnection:
    creds = {
        'host': os.getenv('SNOWFLAKE_HOST'),
        'port': os.getenv('SNOWFLAKE_PORT'),
        'protocol': "https",
        'account': os.getenv('SNOWFLAKE_ACCOUNT'),
        'authenticator': "oauth",
        'token': open('/snowflake/session/token', 'r').read(),
        'warehouse': "DATA_API_WH",
        'database': "API",
        'schema': "PUBLIC",
        'client_session_keep_alive': True
    }
    return snowflake.connector.connect(**creds)

# Make the API endpoints
connector = Blueprint('connector', __name__)

## Top 10 customers in date range
dateformat = '%Y-%m-%d'

@connector.route('/customers/top10')
def customers_top10():
    # Validate arguments
    sdt_str = request.args.get('start_range') or '1995-01-01'
    edt_str = request.args.get('end_range') or '1995-03-31'
    try:
        sdt = datetime.datetime.strptime(sdt_str, dateformat)
        edt = datetime.datetime.strptime(edt_str, dateformat)
    except:
        abort(400, "Invalid start and/or end dates.")
    sql_string = '''
        SELECT
            o_custkey
          , SUM(o_totalprice) AS sum_totalprice
        FROM snowflake_sample_data.tpch_sf10.orders
        WHERE o_orderdate >= '{sdt}'
          AND o_orderdate <= '{edt}'
        GROUP BY o_custkey
        ORDER BY sum_totalprice DESC
        LIMIT 10
    '''
    sql = sql_string.format(sdt=sdt, edt=edt)
    try:
        conn = connect()
        res = conn.cursor(DictCursor).execute(sql)
        return make_response(jsonify(res.fetchall()))
    except:
        abort(500, "Error reading from Snowflake. Check the logs for details.")

## Monthly sales for a clerk in a year
@connector.route('/clerk/<clerkid>/yearly_sales/<year>')
def clerk_montly_sales(clerkid, year):
    # Validate arguments
    try: 
        year_int = int(year)
    except:
        abort(400, "Invalid year.")
    if not clerkid.isdigit():
        abort(400, "Clerk ID can only contain numbers.")
    clerkid_str = f"Clerk#{clerkid}"
    sql_string = '''
        SELECT
            o_clerk
          ,  Month(o_orderdate) AS month
          , SUM(o_totalprice) AS sum_totalprice
        FROM snowflake_sample_data.tpch_sf10.orders
        WHERE Year(o_orderdate) = {year}
          AND o_clerk = '{clerkid}'
        GROUP BY o_clerk, month
        ORDER BY o_clerk, month
    '''
    sql = sql_string.format(year=year_int, clerkid=clerkid_str)
    try:
        conn = connect()
        res = conn.cursor(DictCursor).execute(sql)
        return make_response(jsonify(res.fetchall()))
    except:
        abort(500, "Error reading from Snowflake. Check the logs for details.")
