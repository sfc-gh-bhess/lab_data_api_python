import datetime
import os

from flask import Blueprint, request, abort, make_response, jsonify

# Make the Snowflake connection
from snowflake.snowpark import Session
import snowflake.snowpark.functions as f

def connect() -> Session:
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
    return Session.builder.configs(creds).create()

# Make the API endpoints
snowpark = Blueprint('snowpark', __name__)

## Top 10 customers in date range
dateformat = '%Y-%m-%d'

@snowpark.route('/customers/top10')
def customers_top10():
    # Validate arguments
    sdt_str = request.args.get('start_range') or '1995-01-01'
    edt_str = request.args.get('end_range') or '1995-03-31'
    try:
        sdt = datetime.datetime.strptime(sdt_str, dateformat)
        edt = datetime.datetime.strptime(edt_str, dateformat)
    except:
        abort(400, "Invalid start and/or end dates.")
    try:
        session = connect()
        df = session.table('snowflake_sample_data.tpch_sf10.orders') \
                .filter((f.col('O_ORDERDATE') >= sdt) & (f.col('O_ORDERDATE') <= edt)) \
                .group_by(f.col('O_CUSTKEY')) \
                .agg(f.sum(f.col('O_TOTALPRICE')).alias('SUM_TOTALPRICE')) \
                .sort(f.col('SUM_TOTALPRICE').desc()) \
                .limit(10)
        return make_response(jsonify([x.as_dict() for x in df.to_local_iterator()]))
    except:
        abort(500, "Error reading from Snowflake. Check the logs for details.")

## Monthly sales for a clerk in a year
@snowpark.route('/clerk/<clerkid>/yearly_sales/<year>')
def clerk_montly_sales(clerkid, year):
    # Validate arguments
    try: 
        year_int = int(year)
    except:
        abort(400, "Invalid year.")
    if not clerkid.isdigit():
        abort(400, "Clerk ID can only contain numbers.")
    clerkid_str = f"Clerk#{clerkid}"
    try:
        session = connect()
        df = session.table('snowflake_sample_data.tpch_sf10.orders') \
                .filter(f.year(f.col('O_ORDERDATE')) == year_int) \
                .filter(f.col('O_CLERK') == clerkid_str) \
                .with_column('MONTH', f.month(f.col('O_ORDERDATE'))) \
                .groupBy(f.col('O_CLERK'), f.col('MONTH')) \
                .agg(f.sum(f.col('O_TOTALPRICE')).alias('SUM_TOTALPRICE')) \
                .sort(f.col('O_CLERK'), f.col('MONTH'))
        return make_response(jsonify([x.as_dict() for x in df.to_local_iterator()]))
    except:
        abort(500, "Error reading from Snowflake. Check the logs for details.")

