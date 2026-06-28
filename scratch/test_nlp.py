import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.sentence_builder import SentenceBuilder

sb = SentenceBuilder()

test_sequences = [
    ["g_ticket", "g_when"],
    ["g_ticket", "g_two"],
    ["g_pune", "g_ticket", "g_two"],
    ["g_mobile", "g_price"]
]

for seq in test_sequences:
    sb.reset()
    for gesture in seq:
        sb.add(gesture)
    
    print(f"Sequence: {seq}")
    print(f"Context Detected: {sb.context_manager.get_display_name()}")
    print(f"Raw String: {sb.get_raw_intents_string()}")
    print(f"Sentence: {sb.get_sentence()}\n")
