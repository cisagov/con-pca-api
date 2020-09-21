import os
import sys

from dotenv import load_dotenv, find_dotenv

script_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.realpath(f"{script_dir}/../.."))

load_dotenv(find_dotenv())

os.environ["DB_HOST"] = "localhost"

from lambda_functions.tasks.handler import lambda_handler

lambda_handler(None, None)
