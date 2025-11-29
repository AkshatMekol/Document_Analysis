import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
TENDERS_COLLECTION = os.getenv("TENDERS_COLLECTION")
DOCS_STATUS_COLLECTION = os.getenv("DOCS_STATUS_COLLECTION")

MAX_PROCESSES_GROQ = 5
MAX_PROCESSES_DEEPSEEK = 10

CLASSIFY_PROMPT = """
                  You are a strict classifier for tender documents.
                  
                  Your task is to identify ONLY the pages that must be filled out by the contractor and sent back to the client.
                  These pages contain blanks, empty fields, places to write, tables to fill, or areas for signatures/seals.
                  
                  Ignore any page that is purely:
                  - Instructions, clauses, or general text
                  - Tender descriptions
                  - Annexures with information already filled
                  - Tables that only display data without requiring input
                  
                  Respond with ONE WORD ONLY: FORM or OTHER.
                  
                  Page content:
                  {content}
                  """
