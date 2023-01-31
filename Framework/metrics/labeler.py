from google.cloud import bigquery
from datetime import datetime
import os


GCP_TIMESTMAP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
USER_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"


def get_datetime_input(msg):
    user_date = datetime.strptime(
        input(f"Please input {msg} date and time in 24h format ({USER_TIMESTAMP_FORMAT}) (example: 2023-01-01 01:01): "),
        USER_TIMESTAMP_FORMAT,
    )
    return user_date.strftime(GCP_TIMESTMAP_FORMAT)


def main():
    client = bigquery.Client()

    # Table identifiers - these should be coming from zeuz server.
    actions_table_id = os.environ["GCP_BIGQUERY_ACTIONS_TABLE_ID"]
    steps_table_id = os.environ["GCP_BIGQUERY_STEPS_TABLE_ID"]
    browser_perf_table_id = os.environ["GCP_BIGQUERY_BROWSER_PERF_TABLE_ID"]
    test_cases_table_id = os.environ["GCP_BIGQUERY_TEST_CASES_TABLE_ID"]
    tables = [
        actions_table_id,
        steps_table_id,
        browser_perf_table_id,
        test_cases_table_id,
    ]

    try:
        start_date = get_datetime_input("START")
        end_date = get_datetime_input("END")
    except:
        print(f"Invalid date format, expected format: {USER_TIMESTAMP_FORMAT}." \
              "Visit https://strftime.org/ for more details.")
        return

    ignore = input("Do you want to ignore the results between the given date intervals? (y for yes): ").strip().lower() == 'y'
    user_label = input("Please specify a user label (press Enter to keep empty): ")

    for table in tables:
        query = f"""
        UPDATE `{table}`
        SET
            `ignore`={ignore},
            `user_label`='{user_label}'
        WHERE
            `time_stamp` >= '{start_date}'
            AND `time_stamp` <= '{end_date}'
        """
        query_job = client.query(query)
        rows = query_job.result()
        print(f"Updated `{table}` table.")
        print(f"{rows} rows affected.")


main()
