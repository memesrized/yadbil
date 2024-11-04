# yadbil
Yet Another DataBase for Intelligent Lookup

1. pip install -e .
2. pre-commit install

## How to scrap telegram channels

1. Specify env variables as in `.env_example`
    - `API_HASH` and `API_ID` - [instruction](https://docs.telethon.dev/en/stable/basic/signing-in.html)
        - be aware of this [ToS part](https://docs.telethon.dev/en/stable/basic/next-steps.html#a-note-on-developing-applications)
2. Adjust config: `configs/parse_telegram.json`
2. Adjust permissions: `chmod 777 scripts/tg_scraping.sh`
3. Run the script `./scripts/tg_scraping.sh`
