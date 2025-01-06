```shell
uv sync --all-groups
uv pip install -e .
source .venv/bin/activate
pytest
```

or using pip

```shell
python3.13 -m venv .venv
source .venv/bin/activate
pip install .
pip install pytest pytest-cov
pip install -e .
deactivate
source .venv/bin/activate
pytest
```
