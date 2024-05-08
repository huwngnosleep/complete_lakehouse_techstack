import time


def run_function_with_time(func, param) -> None:
    st = time.time()
    print("Starting insert data into ICEBERG table")
    et = time.time()
    func(*param)
    print("Finished inserting ICEBERG table")
    print('Execution time:', (et - st) * 1000, 'miliseconds')


def run_sql_with_time(cursor_executor, sql: str) -> None:
    run_function_with_time(cursor_executor, param=sql)