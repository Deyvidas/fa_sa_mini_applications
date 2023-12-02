<!-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ -->

---

<h3 id="1" align="center">Banking app</h3>

Application with api and PostgreSQL DB.

<!-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ -->

---

<h3 id="2" align="center">Used technologies</h3>

- fastapi
- sqlalchemy
- alembic
- pydantic
- uvicorn

<!-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ -->

---

<h3 id="3" align="center">How to use</h3>

<p align="center">1. Clone project:</p>

```bash
git clone git@github.com:Deyvidas/fa_sa_mini_applications.git
```

<p align="center">2. Create virtual environment:</p>

with poetry:

```bash
poetry env use python3.X.X
```
with venv module:

```bash
python3.X.X -m venv .venv
```

<p align="center">3. Add root of project into PYTHONPATH:</p>

```sh
# .venv/bin/activate

PYTHONPATH='/absolute/path/to/fa_sa_mini_applications'
export PYTHONPATH
```

<p align="center">4. Activate virtual environment and install requirements:</p>

with poetry:

```bash
poetry shell && poetry install
```

with venv module:

```bash
. .venv/bin/activate && pip install -r requirement.txt
```

<p align="center">5. Make migrations</p>

```bash
alembic upgrade head
```

<p align="center">6. Run application on localhost</p>

```bash
uvicorn --reload src.banking_app.main:banking_app
```

<p align="center">7. Read documentation of API</p>

- http://localhost/docs
- http://localhost/redoc
