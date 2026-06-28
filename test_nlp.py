import os
from utils.context_manager import ContextManager
from utils.sentence_builder import SentenceBuilder

def main():
    sb = SentenceBuilder()
    
    print("=== Testing SHOP Context ===")
    sb.set_context("shop")
    
    print("Normal order:")
    sb.add("g_two")
    sb.add("g_mobile")
    sb.add("g_buy")
    print("Intents:", sb.get_raw_intents_string())
    print("Sentence:", sb.get_sentence())
    print()

    print("Unordered intents (Item -> Quantity -> Action):")
    sb.reset()
    sb.add("g_mobile")
    sb.add("g_two")
    sb.add("g_buy")
    print("Intents:", sb.get_raw_intents_string())
    print("Sentence:", sb.get_sentence())
    print()

    print("Single intent fallback:")
    sb.reset()
    sb.add("g_mobile")
    print("Intents:", sb.get_raw_intents_string())
    print("Sentence:", sb.get_sentence())
    print()

    print("=== Testing TRANSPORT Context ===")
    sb.set_context("transport")
    
    print("Unordered intents (Action -> Quantity -> Location -> Item):")
    sb.add("g_buy")
    sb.add("g_two")
    sb.add("g_pune")
    sb.add("g_ticket")
    print("Intents:", sb.get_raw_intents_string())
    print("Sentence:", sb.get_sentence())
    print()

    print("Single intent:")
    sb.reset()
    sb.add("g_ticket")
    print("Intents:", sb.get_raw_intents_string())
    print("Sentence:", sb.get_sentence())
    print()

    print("=== Testing DAILY Context ===")
    sb.set_context("daily")
    sb.add("g_hello")
    print("Intents:", sb.get_raw_intents_string())
    print("Sentence:", sb.get_sentence())
    print()

if __name__ == "__main__":
    main()
