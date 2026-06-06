[root@de ~]# cd /u01/nl_sql
[root@de ~]# mkdir banking_rag && cd banking_rag
[root@de banking_rag]# pwd
/u01/nl_sql/banking_rag

dnf install epel-release
dnf install python3.13
dnf install python3.13-pip

[root@de banking_rag]# python3.13 -m pip --version
pip 25.1.1 from /usr/lib/python3.13/site-packages/pip (python 3.13)
[root@de banking_rag]# python3.13 --version
Python 3.13.13

[root@de banking_rag]# python3.13 -m venv .venv && source .venv/bin/activate

mkdir -p sql src scripts
touch src/__init__.py

[root@de banking_rag]# vi requirements.txt

langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
langchain-postgres>=0.0.12
langgraph>=0.2.0
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
rich>=13.7.0
tabulate>=0.9.0

[root@de banking_rag]# pip3.13 install -r requirements.txt
[root@de ~]# cd /u01/nl_sql/banking_rag/src
[root@de ~]# vi .env
[root@de ~]# cd /u01/nl_sql/banking_rag/scripts/

[root@de ~]# cd /u01/nl_sql/banking_rag/
(.venv) [root@de banking_rag]# python3.13 -m scripts.ingest_schema

[root@de ~]# cd /u01/nl_sql/banking_rag
(.venv) [root@de banking_rag]# python main.py

-- Testing
(.venv) [root@de banking_rag]# pwd
/u01/nl_sql/banking_rag
(.venv) [root@de banking_rag]# python main.py
╭──────────────────────────────────────────────╮
│ Banking NL-to-SQL RAG                        │
│ LangGraph · Ollama · PostgreSQL              │
│ Type debug to toggle SQL view · quit to exit │
╰──────────────────────────────────────────────╯
You › How many customers do we have?
 total_customers
 10
╭────────────────────────────────────────────────────────── Answer 
│ There are a total of 10 customers.
╰─────────────────────────────────────────────────────────────────

You › debug
Debug mode ON

You › Which customer has the highest total balance across all accounts?
╭────────────────────────────────────────────────────────── Answer
│ Priya Das has the highest total balance across all accounts, with a total of 670,000.00
╰─────────────────────────────────────────────────────────────────────

