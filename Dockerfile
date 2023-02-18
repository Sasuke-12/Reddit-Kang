FROM  python:3.9.7-slim-buster 
  
  
  WORKDIR  . 
  RUN  apt -qq update && apt -qq install -y git wget pv jq python3-dev mediainfo 
  COPY  . . 
  RUN  pip3 install -r requirements.txt 
  
CMD ["python3", "bot.py"]
