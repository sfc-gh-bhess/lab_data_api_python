# Create a Data API for Snowflake Data using Python and Flask
Technologies used: [Snowflake](https://snowflake.com/), [Python](https://www.python.org/), 
[Flask](https://palletsprojects.com/p/flask/), [Anaconda](https://www.anaconda.com/)

This project demonstrates how to build a custom REST API powered by Snowflake. 
It uses a simple Python Flask API service running locally. Connectivity is made to 
Snowflake via key pair authentication.

## Requirements:
* Snowflake account
* Snowflake user with
  * SELECT access to the `SNOWFLAKE_SAMPLES.TPCH_SF10.ORDERS` table
  * USAGE access on a warehouse
* Python 3.8
* Anaconda (or Miniconda)

## Configuration
### Python
Using `conda`, create a new environment from the `conda_environment.yml` file:
```
conda env create -f conda_environment.yml
```

This environment will be created with all the necessary prerequisite packages.
It will be activated once created. If you need to activate the environment
again at some other time, you can do so:
```
conda activate pylab
```

### Snowflake
Use the template in `config.py.example` to enter your information in JSON format:
* account
* user
* password
* Snowflake warehouse

See [Snowflake documentation](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api#label-account-format-info) for information on how to find your account identifier.

## Running
To start the server, from the `src/` directory, run:
```
python app.py
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

