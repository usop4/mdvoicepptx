  
  rm scenario/*
  
  marp scenario.md --images png --output ./scenario/scenario.png
  python make_mp4_from_scenario.py
