# Corpus scope and editorial notes

The dataset contains 1,000 authored English troubleshooting entries: **350 Python, 250 pandas, 175 pip, and 225 FastAPI**. The first 200 entries are in `create_entries.py` and `extra_entries.py`; 800 additional explicit records are in `corpus/*.txt`, read by `corpus_expansion.py`. They cover exceptions, warnings, configuration failures, and recognizable incorrect behavior. Each record has a unique ID, title, example, explanation, likely cause, suggested fix, and category tags.

Examples are illustrative. Context prefixes distinguish similar messages in different operations; exact wording and behavior can vary by package version. They are not copied production logs, and the project does not claim to have reproduced all 1,000 failures in their original libraries. Entries contain no user-submitted data. The dataset is written as individual cases, not expanded by substituting variable or package names into a template.

## Retrieval checks and limits

The build uses the examples, titles, explanations, causes, fixes, and tags. Examples receive extra document weight. Tests check unique titles/examples, exact category counts, retrieval of every stored example, and a small separate set of rephrased queries. Self-retrieval demonstrates consistency; it is not an estimate of real-world accuracy. The rephrased set is a regression check, not an independently collected benchmark. Related failures can share vocabulary and rank together; similarity scores are not confidence.

## Technical references

Selected version-sensitive guidance was checked against primary documentation:

- [Python asyncio exceptions](https://docs.python.org/3/library/asyncio-exceptions.html)
- [pandas indexing](https://pandas.pydata.org/docs/user_guide/indexing.html) and [grouping](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas GroupBy.apply](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.api.typing.DataFrameGroupBy.apply.html)
- [pip dependency resolution](https://pip.pypa.io/en/stable/topics/dependency-resolution/), [requirements format](https://pip.pypa.io/en/stable/reference/requirements-file-format/), and [secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/)
- [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/), [dependency lifetimes](https://fastapi.tiangolo.com/advanced/advanced-dependencies/), and [response models](https://fastapi.tiangolo.com/tutorial/response-model/)

These are reference links, not claims that every entry has a separate runtime reproduction or individual documentation citation. The application's pinned runtime dependencies are separate from the varied libraries and versions discussed by the troubleshooting corpus.
