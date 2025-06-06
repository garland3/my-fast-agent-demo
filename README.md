
# setup

```bash
uv venv venv --python=python3.12
source venv/bin/activate # on windows use venv\Scripts\activate
uv pip install -r requirements.txt

# maybe connect to a remove ollama, if you dont' want to run locall. 
ssh -L 11434:localhost:11434 user@server

# ssh user@server -
# ollama run qwen3:0.6b
```
