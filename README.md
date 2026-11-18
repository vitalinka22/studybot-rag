# StudyBot – a RAG chatbot about TU Berlin study programs

StudyBot answers questions about study programs, admission and studying at TU Berlin.
Its answers are based only on pages of the TU Berlin website, and it shows the source links.

Built for the bachelor thesis *"Comparing Real and LLM-Simulated Users in Chatbot Evaluation:
Behavioural Similarity, Quality Judgments, and Sensitivity to Answer Degradation"*
(Quality and Usability Lab, TU Berlin).

## How it works

1. **Data:** 143 program pages + 194 linked TU pages (crawled in November 2026, depth 2 from the
   [program list](https://www.tu.berlin/en/studying/study-programs/all-programs-offered)).
2. **Chunks:** the pages are cut into 3,584 text pieces (one per section).
3. **Search:** every chunk is turned into an embedding (`multilingual-e5-large-instruct`)
   and stored in Chroma. A question finds the 10 most similar chunks.
4. **Answer:** the LLM (`gemma-4-31b-it`, via the GWDG SAIA API) answers only from these chunks
   and an overview table of all programs.
5. **Multi-turn:** each message is first rewritten into a complete English search query,
   using the conversation so far.

## Setup (once)

```bash
cd studybot-rag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a file `.env` in the project folder with your GWDG API key:

```
ACADEMIC_CLOUD_CHATAI_API_KEY="your-key-here"
```

## Build the data (once, in this order)

```bash
python src/crawl_list.py        # 143 program addresses           (~30 s)
python src/crawl_programs.py    # download the program pages       (~4 min)
python src/crawl_pages.py       # download the linked TU pages     (~6 min)
python src/build_programs.py    # key facts -> data/processed/programs.db
python src/build_chunks.py      # pages -> data/processed/chunks.jsonl
python src/build_index.py       # embeddings -> data/chroma        (~4 min)
```

## Run the chatbot

```bash
streamlit run src/app.py
```

The chat opens at http://localhost:8501. Stop it with `Ctrl + C`.

There is also a Terminal version: `python src/chat.py`

## Answer conditions (for the study)

The condition is chosen in the web address. Participants do not see it.

| Address | Condition |
|---|---|
| `http://localhost:8501` | normal (default) |
| `http://localhost:8501/?condition=incomplete` | the most important information is left out |
| `http://localhost:8501/?condition=incorrect` | one important fact is changed to a wrong value |

The correct answer is always generated first. In the incomplete/incorrect conditions,
a second LLM call changes it. Both versions are logged.

## Logs

Every turn is saved in `data/logs/conversations.jsonl` (session ID, time, condition, question,
search query, found chunks, original and shown answer, response time).

```bash
python src/show_logs.py         # quick overview
```

## Checks and tests

```bash
python src/check_programs.py    # questions to the programs database
python src/check_chunks.py      # look at random chunks
python src/test_search.py       # 10 test questions for the search (currently 8/10)
python src/test_conditions.py   # one answer in all three conditions
```

## Project structure

```
studybot-rag/
├── .env                    # API key (never commit!)
├── requirements.txt
├── README.md
├── data/                   # all data, not in git
│   ├── raw/                # downloaded pages
│   ├── processed/          # programs.db, chunks.jsonl
│   ├── chroma/             # search database
│   └── logs/               # conversation logs
└── src/
    ├── config.py           # API connection and model names
    ├── web.py              # download pages, find links
    ├── crawl_*.py          # crawling (Day 2)
    ├── extract.py          # HTML -> clean text sections
    ├── build_*.py          # build database, chunks, search index
    ├── embeddings.py       # texts/questions -> embeddings
    ├── search.py           # find the best chunks for a question
    ├── answer.py           # rewrite, search, answer, conditions
    ├── conversation_log.py # save every turn
    ├── app.py              # web chat (Streamlit)
    └── chat.py             # Terminal chat
```

## Notes

- Pages whose address contains `/alumni` are excluded (not about studying).
- The data is a snapshot from November 2026. To update it, run the "Build the data" steps again.
- API limits of the key: 10 requests per 10 seconds, 3,000 per hour.