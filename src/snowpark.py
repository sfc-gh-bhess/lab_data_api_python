from flask import Blueprint, request, abort, make_response, jsonify
import json
import datetime

# Make the Snowflake connection
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from snowflake.snowpark import Session
import snowflake.snowpark.functions as f
from config import creds
def connect() -> Session:
    if 'private_key' in creds:
        if not isinstance(creds['private_key'], bytes):
            p_key = serialization.load_pem_private_key(
                    creds['private_key'].encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            pkb = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            creds['private_key'] = pkb
    return Session.builder.configs(creds).create()

session = connect()

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

