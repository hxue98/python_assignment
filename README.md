# Project Description

This is a RESTful Service for stock data and statitics, the app gets stock data using AlphaVantage's API and can provide statitics of the data.

# Tech Stack

The backend framework is Flask with Database hosted using MYSQL.
The connection between the web app and the database is done through mysql-connector-python for simplicity. For more complicated data schema, ORM should be used for faster and eaiser development.

# Run the project

To run the project, simply run

```
docker-compose up
```

When the Database and API service finish initialization, you can populate the database by running

```
py .\get_raw_data.py
```

Then, you can get financial data or statitics for IBM and/or APPL by running

```
curl -X GET 'http://localhost:5000/api/financial_data?symbol=IBM'
curl -X GET 'http://localhost:5000/api/statistics?start_date=2023-07-14&end_date=2023-07-19&symbol=IBM'
```

*Note that for financial_data API, symbol, start_date, end_date are optional

# API Key storage

Sensitive data such as password and API keys should not be commited to public repositories or even private repositories as they could be compromised and be used for malicous activities. I stored my API keys and database password in .env file and inject them as environment variable in application's container. Though I included this file in my submission, it should be listed in .gitignore file. In Dev environment, developers who need to run the project needs to ask peers for the credentials and mannually create their .env file. In a production environment, these keys should come from a more secured place. For exmaple, these credential can be stored in Secret Manager in AWS/GCP with role based security and other functionalities such as rotating keys to maximize security.