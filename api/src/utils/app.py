import time

from src.utils.table_selection.table_selector import *
from src.utils.table_selection.table_details import *
from src.utils.api_data_request.api_generator import *
from src.utils.data_analysis.data_analysis import *
from src.utils.logs import *

def get_api(query, TABLES_PATH):
    start_time = time.time()

    manager = TableManager(TABLES_PATH)
    table = request_tables_to_lm_from_db(query, manager)
    variables, measures, cuts = get_api_params_from_lm(query, table, model = 'gpt-4')

    api = api_build(table, manager, variables, measures, cuts)
    api_url = api.build_url()
    print("API:", api_url)
    
    data, df, response = api.fetch_data()
    end_time = time.time()
    duration = end_time - start_time

    if (response == "No data found." or df.empty):
        log_apicall(query, "", response, "", "", "", table, duration)
        return api_url, data, response
    
    else:
        response = agent_answer(df, query)
        log_apicall(query, api_url, response, variables, measures, cuts, table, duration)
        return api_url, data, response
    

def get_api_new(query, TABLES_PATH):
    start_time = time.time()

    manager = TableManager(TABLES_PATH)
    
    table = request_tables_to_lm_from_db(query, manager)
    yield {"step": "request_tables_to_lm_from_db", "table": table}
    
    variables, measures, cuts = get_api_params_from_lm(query, table, model='gpt-4')
    yield {"step": "get_api_params_from_lm", "variables": variables, "measures": measures, "cuts": cuts}
    
    api = api_build(table, manager, variables, measures, cuts)
    api_url = api.build_url()
    print("API:", api_url)

    data, df, response = api.fetch_data()
    yield {"step": "fetch_data", "data": data, "df": df, "response": response}
    
    end_time = time.time()
    duration = end_time - start_time

    if (response == "No data found." or df.empty):
        log_apicall(query, "", response, "", "", "", table, duration)
        return
    
    else:
        response = agent_answer(df, query)
        log_apicall(query, api_url, response, variables, measures, cuts, table, duration)
        yield {"step": "agent_answer", "response": response}

    
TABLES_PATH = getenv('TABLES_PATH')
#get_api_new('how many tons of plastic were moved from Texas to California by truck during 2021', TABLES_PATH)


for result in get_api_new('how many tons of plastic were moved from Texas to California by truck during 2021', TABLES_PATH):
    print(result)