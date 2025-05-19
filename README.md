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

### Snowpark Container Services
You can deploy this API in Snowpark Container Services. To do so, first create
the Docker image for SPCS by running the following:
```bash
docker build --platform linux/amd64 -t dataapi .
```

Next, we need to create some objects in Snowflake. Log into Snowflake and follow
the following steps:
1. Navigate to the database and schema you would like to use, e.g.:
```SQL
CREATE DATABASE IF NOT EXISTS api;
USE SCHEMA api.public;
```

2. Create an IMAGE REPOSITORY:
```SQL
CREATE IMAGE REPOSITORY api;
```

3. Get the URL for the IMAGE REPOSITORY. 
```SQL
DESCRIBE IMAGE REPOSITORY api;
```
Note the value for `repository_url`.

4. Log into Docker via SnowCLI

5. Upload the image to your image repository:
```bash
docker tag dataapi:latest <repository_url>/dataapi:latest
docker push <repository_url>/dataapi:latest
```

6. Create the COMPUTE POOL:
```sql
USE ROLE ACCOUNTADMIN;
CREATE COMPUTE POOL api
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_XS;
GRANT USAGE, MONITOR ON COMPUTE POOL api TO ROLE data_api_role;
```

7. Create warehouse for the service to use:
```sql
CREATE WAREHOUSE IF NOT EXISTS data_api_wh WITH WAREHOUSE_SIZE='X-SMALL';
```

8. Create the API service
```sql
CREATE SERVICE api
  IN COMPUTE POOL api
  FROM SPECIFICATION $$
spec:
  containers:
    - name: api
      image: <repository_url>/dataapi:latest
  endpoints:
    - name: api
      port: 8001
      public:true
serviceRoles:
- name: api_sr
  endpoints:
  - api
  $$
  QUERY_WAREHOUSE = data_api_wh
  ;
```

9. Grant usage on the endpoint to some role:
```sql
GRANT SERVICE ROLE api!api_sr TO ROLE api_user_role;
```

10. See that the services have started by executing `SHOW SERVICES IN COMPUTE POOL pool1` 
   and `SELECT system$get_service_status('api_svc')`.
11. Find the public endpoint for the router service by executing `SHOW ENDPOINTS IN SERVICE api_svc`.
12. Navigate to the endpoint, login, and see the `Nothing to see here` message.

#### Test with test programs
First we need to create a user that we can use to access the endpoint.
```sql
CREATE USER api_test ...
```

Next, we grant the user a role that has been granted the `api_svc!api_sr` SERVICE ROLE.
```sql
GRANT ROLE api_user_role TO USER api_test;
```

We need to create a [Programmatic Access Token](https://docs.snowflake.com/en/sql-reference/sql/alter-user-add-programmatic-access-token)
to access the endpoint programmatically. We can do that in SQL:
```sql
ALTER USER api_test ADD PROGRAMMATIC_ACCESS_TOKEN api_pat;
```
Copy the returned PAT token to a file named `api-token-secret.txt` in the test directory.

You can test with the `test.py` script in the test directory:
```bash
python text.py --account_url <account URL> --role test_role --endpoint https://<SPCS endpoint>/
```
which should return the "Nothing to see here" message. You can then test other paths.

Check out `python test.py --help` for help.

Additionally, we created a Streamlit to test the API. You can start that by running
```bash
python -m streamlit run test_streamlit.py
```
Fill in the details and hit "Fetch it!".
