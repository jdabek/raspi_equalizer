#!/bin/bash

psaudio=
echo "Please plug in microphone..."
while "true"; do
  i="$(arecord -l |wc -l)"
  if [[ $i -gt 1 && $psaudio = "" ]]; then
    echo "Starting audio program..."
    python audio15.py &
    psaudio=$!
  fi
  if [[ $i = 1 && ! $psaudio = "" ]]; then
    echo "Ending audio program..."
    echo "Please plug in microphone..."
    kill $psaudio
    psaudio=
    python ledStop.py
  fi
  sleep 1
done
