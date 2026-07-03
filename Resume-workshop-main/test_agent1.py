# test_agent1.py
from agents.jd_parser import parse_jd
import json

sample_jd = """
We are looking for a Data Scientist with 3+ years of experience.
Required skills: Python, Machine Learning, SQL, TensorFlow, Docker.
Preferred: AWS, Spark, Kubernetes.
Responsibilities: Build ML models, deploy to production, work with product teams.
Education: BTech in Computer Science or related field.
"""

result = parse_jd(sample_jd)
print(json.dumps(result, indent=2))