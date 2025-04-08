# Create a Data API for Snowflake Data using Python and Flask
Technologies used: [Snowflake](https://snowflake.com/), [Python](https://www.python.org/), 
[Flask](https://palletsprojects.com/p/flask/), [Docker](https://www.docker.com/)

This project demonstrates how to build a custom REST API powered by Snowflake. 
It uses a simple Python Flask API service running in Snowflake Container Services.

## Requirements:
* Snowflake account
* Snowflake user with
  * SELECT access to the `SNOWFLAKE_SAMPLES.TPCH_SF10.ORDERS` table
  * USAGE access on a warehouse
* Docker

## Configuration
### Docker
Using `docker`, build the container:
```bash
docker build -t api .
```

The container will be created with all the necessary prerequisite packages.

## Running
To start the server, run the following command updated with your Snowflake Account, User, Password, and Warehouse:
```
docker run -it -d -e SNOWFLAKE_ACCOUNT='<YOUR_SNOWFLAKE_ACCOUNT>' -e SNOWFLAKE_USER='<YOUR_SNOWFLAKE_USER>' -e SNOWFLAKE_PASSWORD='<YOUR_SNOWFLAKE_PASSWORD>' -e SNOWFLAKE_WAREHOUSE='<YOUR_SNOWFLAKE_WAREHOUSE>' -e SNOWFLAKE_DATABASE='SNOWFLAKE_SAMPLE_DATA' -e SNOWFLAKE_SCHEMA='TPCH_SF10' -p 8001:8001 api
```

### Endpoints
The API creates two sets of endpoints, one for using the Snowflake connector:
1. `http://localhost:8001/connector/customers/top10`
  * Which takes the following optional query parameters:
    1. `start_range` - the start date of the range in `YYYY-MM-DD` format. Defaults to `1995-01-01`.
    1. `end_range` - the end date of the range in `YYYY-MM-DD` format. Defaults to `1995-03-31`.
2. `http://localhost:8001/connector/clerk/<CLERKID>/yearly_sales/<YEAR>`
  * Which takes 2 required path parameters:
    1. `CLERKID` - the clerk ID. Use just the numbers, such as `000000001`.
    2. `YEAR` - the year to use, such as `1995`.

And the same ones using Snowpark:
1. `http://localhost:8001/snowpark/customers/top10`
  * Which takes the following optional query parameters:
    1. `start_range` - the start date of the range in `YYYY-MM-DD` format. Defaults to `1995-01-01`.
    1. `end_range` - the end date of the range in `YYYY-MM-DD` format. Defaults to `1995-03-31`.
2. `http://localhost:8001/snowpark/clerk/<CLERKID>/yearly_sales/<YEAR>`
  * Which takes 2 required path parameters:
    1. `CLERKID` - the clerk ID. Use just the numbers, such as `000000001`.
    2. `YEAR` - the year to use, such as `1995`.

### Testing
You can test this API using curl or other command-line tools. You can also use a tool such as
Postman.

Additionally, the API serves a testing page you can open in a web browser at `http://localhost:8001/test`.

