# wsj-chunk

### Features I tried:
The chunking system implemented the Named Entity Recognition (NER) task focusing on noun group tagging. The system employs a comprehensive set of features including basic word attributes (POS tags, prefixes, suffixes, capitalization patterns), contextual information (surrounding words and their POS tags, bigrams, trigrams), positional features (sentence boundaries, relative position), and specialized NP-specific features (noun patterns, compound detection). The code incorporated sophisticated pattern recognition for error correction, addressing common misclassifications through a curated error pattern dictionary. The implementation handles special cases like hyphenated adjectives, time expressions, and numeric quantities. The feature set particularly focuses on capturing syntactic patterns like determiner-adjective-noun sequences and proper name continuations, with specific attention to edge cases like company names with ampersands, color words that can function as both adjectives and nouns, and date expressions. This rich feature engineering approach demonstrates a strong understanding of the linguistic patterns necessary for accurate noun phrase chunking.

----------------------
### Score on the development corpus:
57958 out of 59100 tags correct<br>
  accuracy: 98.07<br>
14666 groups in key<br>
14817 groups in response<br>
13983 correct groups<br>
  precision: 94.37<br>
  recall:    95.34<br>
  F1:         9.49<br>

----------------------
### How to run the system:
Run the following scripts in sequence (don't forget to change the directory):

**Step 1:** Create training features:
```br
python main.py WSJ_02-21.pos-chunk training.feature True
```

**Step 2:** Create development test features:
```br
python main.py WSJ_24.pos test.feature False
```

**Step 3:** Create final test features:
```br
python main.py WSJ_23.pos final.test.feature False
```

**Step 4:** Compile the Java files:
```br
javac -cp .:maxent-3.0.0.jar:trove.jar MEtrain.java MEtag.java
```

**Step 5:** Run the compiled class:
```br
java -cp .:maxent-3.0.0.jar:trove.jar MEtrain training.feature model.chunk
```

**Step 6:** Apply trained model to the development test data:
```br
java -cp .:maxent-3.0.0.jar:trove.jar MEtag test.feature model.chunk response.chunk
```

**Step 7:** Evaluate how well the model performs on the development data:
```br
python score.chunk.py WSJ_24.pos-chunk response.chunk
```

**Step 8:** Generate features for the final test corpus:
```br
python main.py WSJ_23.pos final.test.feature False
```

**Step 9:** Generate submission file using the trained model:
```br
java -cp .:maxent-3.0.0.jar:trove.jar MEtag final.test.feature model.chunk WSJ_23.chunk
```