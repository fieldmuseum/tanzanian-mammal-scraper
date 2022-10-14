'''Utils for general setup, config, and logging'''

import datetime, logging, sys
from dotenv import dotenv_values

def get_config(dato_env:str=None):
    '''Load variable from .env'''

    config = dotenv_values(".env")
    if not config: raise Exception("No .env config file found")

    return config


def start_log(config:dict=None, log_level=logging.INFO, cmd_args:list=sys.argv):
    '''
    Append console output to log-file
    See https://docs.python.org/2/howto/logging.html#logging-to-a-file
    '''
    
    if config is None:
        config = get_config()

    today = datetime.datetime.today().strftime('%Y%m%d')
    log_file = config['LOG_OUTPUT'] + f'dams-netx-{today}.log'

    if type(cmd_args) == list:
        cmd_args = ' '.join(cmd_args)

    logging.basicConfig(
        filename=log_file, 
        level=log_level, 
        format='%(asctime)s %(message)s', 
        datefmt='%H:%M:%S')

    start_time = datetime.datetime.now()
    logging.info(f'STARTED - {start_time} : {__file__} {cmd_args}')
    
    
def stop_log():
    '''Record finish time and stop logging'''

    stop_time = datetime.datetime.now()
    logging.info(f'FINISHED {stop_time} : {__file__}')