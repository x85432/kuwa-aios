from openai import OpenAI
from operator import attrgetter
import os
client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)
models = client.models.list()
for model in sorted(models, key=attrgetter('id')):
    print(model.id)

