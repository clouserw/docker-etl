# etl-graph

## Quickstart

Run the crawler.

```bash
# optional: virtualenv
python3 -m venv venv
source venv/bin/activate
pip-compile
pip install -r requirements.txt

# generate table entities and resolve view references
python -m etl-graph crawl

# generate edgelist from query logs
python -m etl-graph query-log query_log_edges
python -m etl-graph query-log query_log_nodes

# generate final index
python -m etl-graph index
```

Start the web client for visualization.

```bash
npm run dev
```

Deploy to hosting.

```bash
./deploy.sh
```
