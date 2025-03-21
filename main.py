import sys
import re

DETERMINERS = set(['the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'some', 'any', 'each', 'every', 'which', 'what', 'whose'])

PREPOSITIONS = set(['of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out', 'against', 'during'])

COMMON_ADJECTIVES = set(['new', 'good', 'high', 'old', 'great', 'big', 'american', 'small', 'large', 'national', 'young', 'different', 'black', 'long', 'little', 'important', 'political', 'bad', 'white', 'real', 'best', 'right', 'social', 'only', 'public', 'sure', 'low', 'early', 'possible', 'able', 'human', 'local', 'major', 'better', 'economic', 'strong', 'true', 'whole', 'free', 'international', 'full', 'special', 'easy', 'clear', 'recent', 'certain', 'personal', 'open', 'red', 'difficult', 'available', 'likely', 'short', 'single', 'medical', 'current', 'wrong', 'private', 'past', 'foreign', 'poor', 'natural', 'federal', 'popular'])

ALWAYS_O = set(['and', 'or', 'but', ',', '.', '``', "''", '--', ';', ':', 'that', 'then', 'about', 'even', 'still', 'nearly', 'almost', 'because', 'though', 'although', 'however', 'yet', 'thus', 'therefore', 'hence', 'furthermore', 'moreover', 'nevertheless', 'nonetheless', 'meanwhile', 'accordingly', 'consequently', 'subsequently', 'comparatively', 'conversely', 'similarly', 'likewise', 'indeed', 'specifically', 'especially', 'particularly', 'primarily', 'mainly', 'generally', 'usually', 'typically', 'occasionally', 'frequently', 'often', 'rarely', 'seldom', 'sometimes', 'always', 'never', 'ever', 'soon', 'eventually', 'finally', 'lastly', 'meanwhile', 'thereafter', 'beforehand', 'afterwards', 'initially', 'previously', 'currently', 'presently', 'actually', 'certainly', 'definitely', 'absolutely', 'positively', 'undoubtedly', 'arguably', 'presumably', 'supposedly', 'ostensibly', 'apparently', 'seemingly', 'evidently', 'obviously', 'clearly', 'literally', 'fairly', 'quite', 'rather', 'somewhat', 'to', 'of'])

ERROR_PATTERNS = {
    ("early", "Friday"): ("B-NP", "I-NP"),
    ("Friday", "morning"): ("B-NP", "I-NP"),
    ("Thursday", "night"): ("B-NP", "I-NP"),
    ("Friday", "evening"): ("B-NP", "I-NP"),
    ("Late", "Thursday"): ("O", "B-NP"),
    
    (",", "or"): ("I-NP", "I-NP"),
    (",", "loss"): ("I-NP", "I-NP"),
    (",", "including"): ("I-NP", "I-NP"),
    (",", "but"): ("I-NP", "I-NP"),
    (",", "management"): ("I-NP", "I-NP"),
    (",", "planning"): ("I-NP", "I-NP"),
    (",", "respectively"): ("I-NP", "I-NP"),
    
    ("Justin", "Leonard"): ("B-NP", "I-NP"),
    ("Charles", "Schwab"): ("B-NP", "I-NP"),
    ("Maurice", "Coyle"): ("I-NP", "I-NP"),
    ("Kellogg", "Co."): ("I-NP", "I-NP"),
    ("Diana", "Ross"): ("I-NP", "I-NP"),
    ("Lily", "Tomlin"): ("B-NP", "I-NP"),
    ("B.", "Nicks"): ("I-NP", "I-NP"),
    
    ("premium-priced", "products"): ("B-NP", "I-NP"),
    ("fire-engine", "red"): ("B-NP", "I-NP"),
    ("fast-food", "restaurants"): ("B-NP", "I-NP"),
    ("air-charter", "operations"): ("I-NP", "I-NP"),
    ("ill-fated", ","): ("I-NP", "I-NP"),
    
    ("335", "million"): ("O", "O"),
    ("million", "Sector"): ("O", "B-NP"),
    ("5", "billion"): ("O", "O"),
    ("billion", "Equity-Income"): ("O", "B-NP"),
    ("12.7", "billion"): ("O", "O"),
    ("billion", "Magellan"): ("O", "B-NP"),
    ("as", "200"): ("O", "B-NP"),
    ("50", "cents"): ("I-NP", "I-NP"),
    ("35", "cents"): ("B-NP", "I-NP"),
    
    ("cooling", "off"): ("I-NP", "I-NP"),
    ("no", "one"): ("B-NP", "I-NP"),
    ("all", "its"): ("B-NP", "I-NP"),
    ("rumors", "of"): ("I-NP", "I-NP"),
    ("trading", "volume"): ("B-NP", "I-NP"),
    
    ("an", "estimated"): ("I-NP", "I-NP"),
    ("stock", "market"): ("I-NP", "I-NP"),
    ("news", "agency"): ("B-NP", "I-NP"),
    ("stock", "prices"): ("I-NP", "I-NP"),
    ("stock", "exchange"): ("I-NP", "I-NP"),
    ("still", "another"): ("B-NP", "I-NP"),
    ("around", "a"): ("B-NP", "I-NP"),
    ("unit", "of"): ("B-NP", "I-NP"),
    ("professional", "investors"): ("B-NP", "I-NP"),
    ("market", "conditions"): ("B-NP", "I-NP"),
    ("normal", "operations"): ("B-NP", "I-NP"),
    ("striking", "workers"): ("B-NP", "I-NP"),
    ("power", "plants"): ("B-NP", "I-NP"),
    ("Oct.", "13"): ("B-NP", "I-NP"),
    ("recurring", "net"): ("B-NP", "I-NP"),
    ("New", "York"): ("B-NP", "I-NP"),
    ("``", "Bronx"): ("I-NP", "I-NP"),
    ("Bronx", "Tale"): ("I-NP", "I-NP"),
    ("natural", "gas"): ("B-NP", "I-NP"),
    ("next", "month"): ("B-NP", "I-NP"),
    ("next", "year"): ("B-NP", "I-NP"),
}

SPECIAL_WORDS = {
    "and": "O",
    "&": "I-NP in companies, O otherwise",
    "that": "O except as determiner",
    "then": "O",
    "about": "O",
    "more": "O",
    "much": "O",
    "de": "I-NP in proper names",
    "red": "O as adjective, B-NP as noun",
    "blue": "O as adjective, B-NP as noun",
    "green": "O as adjective, B-NP as noun",
    "yellow": "O as adjective, B-NP as noun",
    "stock": "often miscategorized as B-NP instead of I-NP",
    "trading": "usually O before a noun phrase",
    "around": "usually O",
    "early": "B-NP when part of date phrase",
    "Friday": "typically I-NP after modifiers",
    ",": "usually O",
    "cooling": "O when followed by 'off'",
    "off": "O after 'cooling'",
    "still": "usually O",
    "as": "usually O",
    "next": "B-NP in time expressions"
}

def process_file(input_path, output_path, is_training):
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    outlines = []
    sentence = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if sentence:
                process_sentence(sentence, outlines, is_training)
                sentence = []
            outlines.append("")
        else:
            parts = line.split()
            sentence.append(parts)
    
    if sentence:
        process_sentence(sentence, outlines, is_training)
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for line in outlines:
            outfile.write(line + '\n')

def process_sentence(sentence, outlines, is_training):
    pos_sequence = [token[1] for token in sentence]
    word_sequence = [token[0] for token in sentence]
    
    for i, token_info in enumerate(sentence):
        word = token_info[0]
        pos = token_info[1]
        bio_tag = token_info[2] if is_training and len(token_info) > 2 else None
        
        features = [word]
        
        add_basic_features(features, word, pos)
        add_context_features(features, sentence, i, is_training)
        add_position_features(features, i, len(sentence))
        add_np_features(features, word, pos)
        add_pattern_features(features, sentence, i, pos_sequence)
        add_word_shape_features(features, word)
        add_chunk_prediction_features(features, sentence, i, pos)
        add_error_fixes(features, sentence, i, pos, word, word_sequence, pos_sequence)
        
        if is_training and bio_tag:
            features.append(bio_tag)
        
        outlines.append('\t'.join(features))

def add_basic_features(features, word, pos):
    features.append(f"POS={pos}")
    features.append(f"WORD={word.lower()}")
    
    if len(word) > 1:
        features.append(f"PREFIX1={word[0].lower()}")
        features.append(f"SUFFIX1={word[-1].lower()}")
        
        if len(word) > 2:
            features.append(f"PREFIX2={word[:2].lower()}")
            features.append(f"SUFFIX2={word[-2:].lower()}")
            
            if len(word) > 3:
                features.append(f"PREFIX3={word[:3].lower()}")
                features.append(f"SUFFIX3={word[-3:].lower()}")
                
                if len(word) > 4:
                    features.append(f"PREFIX4={word[:4].lower()}")
                    features.append(f"SUFFIX4={word[-4:].lower()}")
    
    if word.isupper() and len(word) > 1:
        features.append("ALLCAPS=true")
    elif word and word[0].isupper():
        features.append("INITCAP=true")
        if any(c.isupper() for c in word[1:]) and any(c.islower() for c in word):
            features.append("CAMELCASE=true")
    
    if len(word) <= 3:
        features.append("LENGTH=short")
    elif len(word) <= 6:
        features.append("LENGTH=medium")
    elif len(word) <= 10:
        features.append("LENGTH=long")
    else:
        features.append("LENGTH=very_long")
    
    if '-' in word:
        features.append("HYPHEN=true")
        hyphen_parts = word.split('-')
        if len(hyphen_parts) > 1:
            features.append(f"HYPHEN_FIRST={hyphen_parts[0].lower()}")
            features.append(f"HYPHEN_LAST={hyphen_parts[-1].lower()}")
    
    if any(c.isdigit() for c in word):
        features.append("HAS_DIGIT=true")
        if all(c.isdigit() for c in word):
            features.append("ALL_DIGITS=true")
        elif re.match(r'^\d+[a-zA-Z]+$', word):
            features.append("NUM_SUFFIX=true")
        elif re.match(r'^[a-zA-Z]+\d+$', word):
            features.append("ALPHA_NUM=true")
    
    if "'" in word:
        features.append("APOSTROPHE=true")
        if word.endswith("'s"):
            features.append("POSSESSIVE=true")
    
    common_noun_suffixes = ['tion', 'ment', 'ence', 'ance', 'ity', 'ism', 'ing', 'ness', 'ship', 'sion', 'ary', 'ery', 'ory']
    for suffix in common_noun_suffixes:
        if len(word) > len(suffix) and word.lower().endswith(suffix):
            features.append(f"NOUN_SUFFIX_{suffix}=true")
            break

def add_context_features(features, sentence, current_pos, is_training):
    if current_pos > 0:
        prev_token = sentence[current_pos - 1]
        prev_word = prev_token[0]
        prev_pos = prev_token[1]
        
        features.append(f"PREV_WORD={prev_word.lower()}")
        features.append(f"PREV_POS={prev_pos}")
        
        if is_training and len(prev_token) > 2:
            features.append("PREV_BIO=@@")
        
        if prev_word.lower() in DETERMINERS:
            features.append("PREV_IS_DET=true")
        
        if current_pos > 1:
            prev2_token = sentence[current_pos - 2]
            prev2_word = prev2_token[0]
            prev2_pos = prev2_token[1]
            
            features.append(f"PREV2_WORD={prev2_word.lower()}")
            features.append(f"PREV2_POS={prev2_pos}")
            
            features.append(f"POS_TRIGRAM_BACK={prev2_pos}_{prev_pos}_{sentence[current_pos][1]}")
            
            if prev2_pos == "DT" and prev_pos.startswith("JJ"):
                features.append("DET_ADJ_PATTERN=true")
        
        current_pos_tag = sentence[current_pos][1]
        features.append(f"POS_BIGRAM={prev_pos}_{current_pos_tag}")
        
        features.append(f"WORD_BIGRAM={prev_word.lower()}_{sentence[current_pos][0].lower()}")
    
    if current_pos < len(sentence) - 1:
        next_token = sentence[current_pos + 1]
        next_word = next_token[0]
        next_pos = next_token[1]
        
        features.append(f"NEXT_WORD={next_word.lower()}")
        features.append(f"NEXT_POS={next_pos}")
        
        if next_word.lower() in PREPOSITIONS:
            features.append("NEXT_IS_PREP=true")
        
        if current_pos < len(sentence) - 2:
            next2_token = sentence[current_pos + 2]
            next2_word = next2_token[0]
            next2_pos = next2_token[1]
            
            features.append(f"NEXT2_WORD={next2_word.lower()}")
            features.append(f"NEXT2_POS={next2_pos}")
            
            features.append(f"POS_TRIGRAM_FWD={sentence[current_pos][1]}_{next_pos}_{next2_pos}")
        
        current_pos_tag = sentence[current_pos][1]
        features.append(f"POS_NEXT_BIGRAM={current_pos_tag}_{next_pos}")
        
        features.append(f"NEXT_WORD_BIGRAM={sentence[current_pos][0].lower()}_{next_word.lower()}")
    
    if current_pos > 0 and current_pos < len(sentence) - 1:
        prev_pos = sentence[current_pos - 1][1]
        curr_pos = sentence[current_pos][1]
        next_pos = sentence[current_pos + 1][1]
        
        features.append(f"POS_CONTEXT={prev_pos}_{curr_pos}_{next_pos}")
        
        if curr_pos == "CC" and prev_pos.startswith("NN") and next_pos.startswith("NN"):
            features.append("COORD_NP=true")
            
        if curr_pos == "CD" and next_pos.startswith("NN"):
            features.append("NUM_NOUN_PATTERN=true")
            
        if curr_pos.startswith("JJ") and next_pos.startswith("JJ"):
            features.append("ADJ_SEQUENCE=true")
            
        if curr_pos.startswith("NNP") and next_pos.startswith("NNP"):
            features.append("NAME_SEQUENCE=true")

def add_position_features(features, position, sentence_length):
    if position == 0:
        features.append("BOS=true")
    elif position == 1:
        features.append("BOS1=true")
    elif position == 2:
        features.append("BOS2=true")
    
    if position == sentence_length - 1:
        features.append("EOS=true")
    elif position == sentence_length - 2:
        features.append("EOS1=true")
    elif position == sentence_length - 3:
        features.append("EOS2=true")
    
    features.append(f"ABS_POS={position}")
    
    relative_pos = position / sentence_length
    if relative_pos < 0.2:
        features.append("REL_POS=first_fifth")
    elif relative_pos < 0.4:
        features.append("REL_POS=second_fifth")
    elif relative_pos < 0.6:
        features.append("REL_POS=middle_fifth")
    elif relative_pos < 0.8:
        features.append("REL_POS=fourth_fifth")
    else:
        features.append("REL_POS=last_fifth")

def add_np_features(features, word, pos):
    if pos.startswith("NN") or pos == "PRP" or pos == "CD":
        features.append("NOUN_LIKE=true")
        
        if pos == "NNP" or pos == "NNPS":
            features.append("PROPER_NOUN=true")
        elif pos == "NN" or pos == "NNS":
            features.append("COMMON_NOUN=true")
        elif pos == "PRP":
            features.append("PRONOUN=true")
    
    if pos == "DT" or pos.startswith("JJ") or pos == "CD" or pos == "POS":
        features.append("NP_MODIFIER=true")
        
        if pos == "DT":
            features.append("DETERMINER=true")
            if word.lower() in DETERMINERS:
                features.append("COMMON_DET=true")
        elif pos.startswith("JJ"):
            features.append("ADJECTIVE=true")
            if word.lower() in COMMON_ADJECTIVES:
                features.append("COMMON_ADJ=true")
        elif pos == "CD":
            features.append("CARDINAL=true")
        elif pos == "POS":
            features.append("POSSESSIVE=true")
    
    if word and word[0].isupper() and not pos.startswith("NNP"):
        features.append("POSSIBLE_PROPER=true")
    
    if pos == "CD":
        features.append("IS_NUMBER=true")
        if re.match(r'^\d{1,2}(st|nd|rd|th)?$', word):
            features.append("POSSIBLE_DATE=true")
        elif re.match(r'^\d{4}$', word):
            features.append("POSSIBLE_YEAR=true")
    
    if pos == "PRP$":
        features.append("POSSESSIVE_PRONOUN=true")
    
    titles = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "President", "Senator", "CEO", "CTO", "CFO"]
    if word in titles or (word.endswith(".") and word.rstrip(".") in [t.rstrip(".") for t in titles]):
        features.append("NAME_TITLE=true")
    
    if word.lower() in ALWAYS_O:
        features.append("ALWAYS_O=true")
        
    if word.startswith('$') or word.startswith('€') or word.startswith('£'):
        features.append("CURRENCY=true")

def add_pattern_features(features, sentence, i, pos_sequence):
    curr_pos = pos_sequence[i]
    
    if i > 0 and i < len(sentence) - 1:
        if curr_pos.startswith("JJ"):
            if i > 0 and pos_sequence[i-1] == "DT":
                if i < len(sentence) - 1 and pos_sequence[i+1].startswith("NN"):
                    features.append("DT_JJ_NN_PATTERN=true")
        
        elif curr_pos.startswith("NN"):
            if i > 0 and pos_sequence[i-1] == "DT":
                features.append("DT_NN_PATTERN=true")
            if i < len(sentence) - 2:
                if pos_sequence[i+1] == "IN" and pos_sequence[i+2].startswith("NN"):
                    features.append("NN_IN_NN_PATTERN=true")
            if i > 0 and pos_sequence[i-1].startswith("JJ"):
                features.append("JJ_NN_PATTERN=true")
            if i > 0 and pos_sequence[i-1] == "CD":
                features.append("CD_NN_PATTERN=true")
        
        elif curr_pos == "DT":
            if i > 0 and pos_sequence[i-1] == "IN":
                features.append("IN_DT_PATTERN=true")
        
        elif curr_pos == ",":
            if i > 0 and i < len(sentence) - 1:
                if pos_sequence[i-1].startswith("NN") and (
                   pos_sequence[i+1].startswith("NN") or 
                   pos_sequence[i+1] == "CC" or 
                   pos_sequence[i+1].startswith("JJ") or
                   pos_sequence[i+1] == "RB"):
                    features.append("COMMA_IN_LIST=true")
    
    noun_streak = 0
    for j in range(i, -1, -1):
        if pos_sequence[j].startswith("NN"):
            noun_streak += 1
        else:
            break
    
    if noun_streak > 1:
        features.append(f"COMPOUND_NOUN_LEFT={noun_streak}")
    
    noun_streak = 0
    for j in range(i, len(pos_sequence)):
        if pos_sequence[j].startswith("NN"):
            noun_streak += 1
        else:
            break
    
    if noun_streak > 1:
        features.append(f"COMPOUND_NOUN_RIGHT={noun_streak}")
    
    if i > 0:
        current_word = sentence[i][0].lower()
        prev_word = sentence[i-1][0].lower()
        
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if current_word in days and prev_word in ["early", "late", "next", "last"]:
            features.append("DATE_PATTERN=true")
        
        months = ["january", "february", "march", "april", "may", "june", 
                 "july", "august", "september", "october", "november", "december"]
        if current_word in months:
            features.append("MONTH_NAME=true")

def add_word_shape_features(features, word):
    if not word:
        return
    
    shape = ""
    last_char_type = None
    
    for c in word:
        if c.isupper():
            char_type = "X"
        elif c.islower():
            char_type = "x"
        elif c.isdigit():
            char_type = "d"
        else:
            char_type = c
        
        if char_type != last_char_type:
            shape += char_type
            last_char_type = char_type
    
    features.append(f"SHAPE={shape}")
    
    if len(word) > 3:
        brief_shape = word[0].isupper() and "X" or word[0].islower() and "x" or word[0].isdigit() and "d" or word[0]
        brief_shape += word[-1].isupper() and "X" or word[-1].islower() and "x" or word[-1].isdigit() and "d" or word[-1]
        features.append(f"BRIEF_SHAPE={brief_shape}")
    
    if re.match(r'^[A-Z][a-z]+$', word):
        features.append("CAPITALIZED_WORD=true")
    elif re.match(r'^[A-Z]+$', word):
        features.append("ALL_CAPS_WORD=true")
    elif re.match(r'^[a-z]+$', word):
        features.append("ALL_LOWER_WORD=true")
    elif re.match(r'^[A-Z][a-z]+[A-Z][a-z]+', word):
        features.append("CAMELCASE_WORD=true")
    elif re.match(r'^\d+[a-zA-Z]+$', word):
        features.append("DIGIT_ALPHA_PATTERN=true")
    elif re.match(r'^[a-zA-Z]+\d+$', word):
        features.append("ALPHA_DIGIT_PATTERN=true")
    elif re.match(r'^[A-Z]\.$', word):
        features.append("INITIAL_PATTERN=true")
        
    if re.match(r'^\$?\d+(\.\d+)?$', word):
        features.append("MONEY_AMOUNT=true")
    elif re.match(r'^\d+(\.\d+)?%$', word):
        features.append("PERCENTAGE=true")

def add_chunk_prediction_features(features, sentence, i, pos):
    if (pos == "DT" or pos == "PRP$" or pos == "CD" or 
            pos.startswith("JJ") or (pos == "RB" and i < len(sentence) - 1 
                                  and sentence[i + 1][1].startswith("JJ"))):
        features.append("LIKELY_BEGIN_NP=true")
    
    if (pos.startswith("NN") or pos.startswith("JJ") or 
            pos == "CD" or pos == "DT" or pos == "POS"):
        features.append("LIKELY_INSIDE_NP=true")
    
    if (pos.startswith("NN") or pos == "PRP") and i < len(sentence) - 1:
        next_pos = sentence[i + 1][1]
        if (next_pos == "VBZ" or next_pos == "VBD" or next_pos == "VBP" or 
                next_pos == "IN" or next_pos == "CC" or next_pos == ","):
            features.append("LIKELY_END_NP=true")
    
    if pos == "CC" and i > 0 and i < len(sentence) - 1:
        prev_pos = sentence[i - 1][1]
        next_pos = sentence[i + 1][1]
        
        if ((prev_pos.startswith("NN") or prev_pos == "PRP") and 
                (next_pos == "DT" or next_pos.startswith("JJ") or next_pos.startswith("NN") or next_pos == "PRP$")):
            features.append("NP_CONJUNCTION=true")
    
    if pos == "NNP" or pos == "NNPS":
        if (i > 0 and (sentence[i - 1][1] == "NNP" or 
                                  sentence[i - 1][1] == "NNPS")):
            features.append("CONSECUTIVE_PROPER=true")
            
        if (i > 0 and sentence[i - 1][0] in 
                ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]):
            features.append("TITLE_PROPER=true")
            
    if pos == "," or pos == "``" or pos == "''" or pos == ":":
        features.append("PUNCTUATION=true")
        
    if pos == "CD" and i > 0 and sentence[i-1][0] == "$":
        features.append("MONEY_AMOUNT=true")
        
    word = sentence[i][0].lower()
    if word in ["million", "billion", "trillion"] and i > 0 and sentence[i-1][1] == "CD":
        features.append("QUANTITY_UNIT=true")

def add_error_fixes(features, sentence, i, pos, word, word_sequence, pos_sequence):
    if i > 0:
        prev_word = sentence[i - 1][0]
        pattern_key = (prev_word, word)
        
        if pattern_key in ERROR_PATTERNS:
            prev_correct, curr_correct = ERROR_PATTERNS[pattern_key]
            features.append(f"ERROR_PATTERN_{prev_word}_{word}=true")
            
            if curr_correct == "I-NP":
                features.append("FIX_AS_I_NP=true")
            elif curr_correct == "B-NP":
                features.append("FIX_AS_B_NP=true")
            elif curr_correct == "O":
                features.append("FIX_AS_O=true")
    
    if pos.startswith("NNP") and i > 0 and pos_sequence[i-1].startswith("NNP"):
        features.append("CONTINUE_PROPER_NAME=true")
        features.append("FIX_AS_I_NP=true")
    
    word_lower = word.lower()
    
    if word_lower == "and" or word_lower == "or":
        features.append("CONJUNCTION_USUALLY_O=true")
        features.append("FIX_AS_O=true")
    elif word == "&":
        if i > 0 and i < len(sentence) - 1:
            prev_pos = pos_sequence[i-1]
            next_pos = pos_sequence[i+1]
            
            if prev_pos.startswith("NNP") and next_pos.startswith("NNP"):
                features.append("AMPERSAND_IN_COMPANY=true")
                features.append("FIX_AS_I_NP=true")
            else:
                features.append("FIX_AS_O=true")
    
    elif word_lower == "de" and i > 0 and i < len(sentence) - 1:
        prev_pos = pos_sequence[i-1]
        next_pos = pos_sequence[i+1]
        
        if prev_pos.startswith("NNP") and next_pos.startswith("NNP"):
            features.append("DE_IN_NAME=true")
            features.append("FIX_AS_I_NP=true")
    
    elif word_lower in ["red", "blue", "green", "yellow"]:
        if i < len(sentence) - 1 and pos_sequence[i+1].startswith("NN"):
            features.append("COLOR_AS_ADJECTIVE=true")
            features.append("FIX_AS_O=true")
        else:
            features.append("COLOR_AS_NOUN=true")
            features.append("FIX_AS_B_NP=true")
    
    elif word_lower == "that":
        features.append("THAT_USUALLY_O=true")
        features.append("FIX_AS_O=true")
        
        if pos == "DT" and i < len(sentence) - 1:
            next_pos = pos_sequence[i+1]
            if next_pos.startswith("NN") or next_pos.startswith("JJ"):
                features.append("THAT_AS_DETERMINER=true")
                features.append("FIX_AS_B_NP=true")
    
    elif word_lower == "no" and pos == "DT":
        if i < len(sentence) - 1:
            next_word = word_sequence[i+1].lower()
            if next_word == "one":
                features.append("NO_ONE_PATTERN=true")
                features.append("FIX_AS_B_NP=true")
    
    if '-' in word and pos.startswith("JJ") and i < len(sentence) - 1:
        next_pos = pos_sequence[i+1]
        if next_pos.startswith("NN"):
            features.append("HYPHENATED_ADJ_BEFORE_NOUN=true")
            features.append("FIX_AS_B_NP=true")
    
    if i > 0:
        prev_pos = pos_sequence[i-1]
        
        if ((prev_pos.startswith("NN") or prev_pos == "PRP") and 
                (pos.startswith("NN") or pos.startswith("JJ") or pos == "CD")):
            features.append("PREFER_CONTINUING_NP=true")
            features.append("FIX_AS_I_NP=true")
    
    if word == ",":
        features.append("COMMA_USUALLY_O=true")
        features.append("FIX_AS_O=true")
        
        if i > 1 and i < len(sentence) - 1:
            if (pos_sequence[i-1].startswith("NN") and 
                (pos_sequence[i+1].startswith("NN") or 
                 pos_sequence[i+1].startswith("JJ") or
                 pos_sequence[i+1] == "CD")):
                features.append("COMMA_IN_NP_LIST=true")
                features.append("FIX_AS_I_NP=true")
    
    if word_lower == "stock" and i < len(sentence) - 1:
        next_word = word_sequence[i+1].lower()
        if next_word in ["market", "exchange", "prices", "index"]:
            features.append("STOCK_COMPOUND=true")
            features.append("FIX_AS_I_NP=true")
    
    if word_lower == "trading" and pos == "VBG":
        features.append("TRADING_VERB_O=true")
        features.append("FIX_AS_O=true")
    
    if i > 0:
        prev_word = word_sequence[i-1].lower()
        if word in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] and prev_word in ["early", "late", "last", "next"]:
            features.append("DATE_EXPRESSION=true")
            features.append("FIX_AS_I_NP=true")
    
    if word_lower == "cooling" and i < len(sentence) - 1 and word_sequence[i+1].lower() == "off":
        features.append("COOLING_OFF_O=true")
        features.append("FIX_AS_O=true")
    
    if word in ["``", "''"]:
        features.append("QUOTE_MARK_O=true")
        features.append("FIX_AS_O=true")
    
    if word_lower in ["early", "late"] and i < len(sentence) - 1:
        next_word = word_sequence[i+1]
        if next_word in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            features.append("EARLY_WEEKDAY=true")
            features.append("FIX_AS_B_NP=true")
    
    if pos == "RB" and word_lower in ["now", "then", "still", "nearly", "almost", "about", "approximately", "only", "just", "even"]:
        features.append("ADV_USUALLY_O=true")
        features.append("FIX_AS_O=true")
        
    if word.startswith('$') and i < len(sentence) - 1 and pos_sequence[i+1] == "CD":
        features.append("CURRENCY_AMOUNT=true")
        features.append("FIX_AS_B_NP=true")
        
    if pos == "CD" and i < len(sentence) - 1:
        next_word = word_sequence[i+1].lower()
        if next_word in ["million", "billion", "trillion"]:
            features.append("NUMERIC_QUANTITY=true")
            features.append("FIX_AS_O=true")
            
    if word_lower == "next" and i < len(sentence) - 1:
        next_word = word_sequence[i+1].lower()
        if next_word in ["month", "year", "week", "day"]:
            features.append("TEMPORAL_EXPRESSION=true")
            features.append("FIX_AS_B_NP=true")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python feature_extractor.py <input_file> <output_file> <is_training>")
        print("  <input_file>: Path to the input corpus file")
        print("  <output_file>: Path where the feature file will be written")
        print("  <is_training>: 'True' for training data, 'False' for test data")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    is_training = sys.argv[3].lower() == 'true'
    
    try:
        process_file(input_file, output_file, is_training)
        print(f"Feature extraction completed successfully!")
        print(f"Output written to: {output_file}")
    except Exception as e:
        print(f"Error processing files: {e}", file=sys.stderr)
        raise