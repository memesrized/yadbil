draft instruction:

# DB query
0. run pipeline from config
    - get before keys
        - openai, pinecone
    - run
    - check?
1. install aws from website
    - login with configure
2. install serverless e.g. homebrew
3. api keys / env credentials for lambda itself
    - or put it as api keys for api gateway???
    - COPY from terminal generated key
4. requirements into layer?
    - build it with proper linux folder


# TG parsing
5. create functions and s3 bucket using serverless
    - parse tg
    - query db
6. create session state by logging in and upload it to s3


# TODO:
 - fix requirements, make it compile to proper arch
 - add layers properly
 - investigate why package: include doesn't work
