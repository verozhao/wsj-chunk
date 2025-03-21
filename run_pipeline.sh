#!/bin/bash

python main.py WSJ_02-21.pos-chunk training.feature True
python main.py WSJ_24.pos test.feature False
python main.py WSJ_23.pos final.test.feature False
javac -cp .:maxent-3.0.0.jar:trove.jar MEtrain.java MEtag.java
java -cp .:maxent-3.0.0.jar:trove.jar MEtrain training.feature model.chunk
java -cp .:maxent-3.0.0.jar:trove.jar MEtag test.feature model.chunk response.chunk
python score.chunk.py WSJ_24.pos-chunk response.chunk
python main.py WSJ_23.pos final.test.feature False
java -cp .:maxent-3.0.0.jar:trove.jar MEtag final.test.feature model.chunk WSJ_23.chunk
echo "--------------------Pipeline Completed--------------------"
