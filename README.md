# yadbil
Yet Another DataBase for Intelligent Lookup

YADBIL is a tool for data collection and semantic search. 

_While this is primarily a library for my personal use, I would be glad if it proves useful for you._

It features:
- 🤖 Data scraping pipeline for automated content collection (currently supporting Telegram channels)
- 🌐 Web-based UI for easy searching through collected data
- 🔍 Semantic search functionality to find similar content and text pieces
- 📊 Built for researchers and analysts who need to search through data that is not indexed by Google

## Installation
```
git clone https://github.com/memesrized/yadbil
cd yadbil
pip install -e .
```

## How to run pipeline
1. Set all parameters and credentials
    1. Specify env variables as in `.env_example`
        - `API_HASH` and `API_ID` - [instruction](https://docs.telethon.dev/en/stable/basic/signing-in.html)
            - be aware of this [ToS part](https://docs.telethon.dev/en/stable/basic/next-steps.html#a-note-on-developing-applications)
    2. Adjust config: `configs/pipeline.yml`
2. Run
    1. as python scripts from config
        1. `python yadbil/run/pipeline.py --config_path configs/pipeline.yml`
    2. as bash script from default config path config
        1. Adjust permissions: `chmod 777 scripts/tg_scraping.sh`
        2. Run the script `./scripts/tg_scraping.sh`
    3. as custom python script
        1. check `examples/run_tg_pipe_sync.py` for example


## Development
Install pre-commit for proper checks:  
`pre-commit install`
