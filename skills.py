# Static skill lexicon used to extract skills from resumes and job descriptions.
#
# Plain phrases, matched case-insensitively on word boundaries. No API calls,
# no models — just a curated list of data, AI/ML, engineering and tooling skills.

SKILLS = [
    # languages
    "python", "sql", "r", "java", "scala", "c++", "c#", "javascript",
    "typescript", "go", "rust", "julia", "matlab",

    # ml / ai
    "machine learning", "deep learning", "natural language processing", "nlp",
    "computer vision", "llm", "generative ai", "genai", "transformers",
    "pytorch", "tensorflow", "scikit-learn", "keras", "xgboost", "lightgbm",
    "hugging face", "langchain", "rag", "prompt engineering", "embeddings",
    "fine-tuning", "model evaluation", "hyperparameter tuning",
    "cross-validation", "mlops", "model deployment", "model monitoring",
    "anomaly detection", "recommendation systems", "sentiment analysis",
    "topic modeling", "named entity recognition", "summarization",

    # statistics / analytics
    "statistics", "a/b testing", "hypothesis testing", "regression",
    "classification", "clustering", "time series", "forecasting",
    "experimental design", "bayesian", "data analysis", "data visualization",
    "storytelling", "kpi", "dashboard",

    # python data stack
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "scipy",
    "statsmodels", "polars", "jupyter", "notebooks",

    # bi / spreadsheets
    "power bi", "tableau", "looker", "excel", "google sheets", "qlik",

    # data engineering
    "data engineering", "etl", "elt", "data pipeline", "airflow", "dbt",
    "spark", "pyspark", "hadoop", "kafka", "flink", "prefect",
    "data warehouse", "data lake", "data lakehouse", "data modeling",
    "dimensional modeling", "data cleaning", "data wrangling",
    "feature engineering", "streaming", "batch processing", "cdc",

    # cloud / infra
    "aws", "gcp", "azure", "databricks", "snowflake", "bigquery",
    "redshift", "docker", "kubernetes", "terraform", "ci/cd", "github actions",

    # databases
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sql server", "oracle",

    # web / backend
    "rest api", "graphql", "fastapi", "flask", "django", "node.js",
    "microservices", "websockets",

    # tools / process
    "git", "linux", "bash", "vscode", "jira", "confluence",
    "agile", "scrum", "kanban", "stakeholder communication",
    "requirements gathering", "documentation", "unit testing", "pytest",
]
