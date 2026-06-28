import json
import os

class ContextManager:
    CONTEXTS = {
        'daily': 'Daily Routine',
        'shop': 'Shopping',
        'transport': 'Transport'
    }

    def __init__(self, templates_path=None):
        if templates_path is None:
            templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "templates.json")
        self.contexts = {}
        self.current_context = "daily"
        self.load_templates(templates_path)

    def load_templates(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.contexts = json.load(f)

    def get_context(self):
        return self.current_context

    def get_display_name(self):
        return self.CONTEXTS.get(self.current_context, self.current_context.title())

    def refresh(self):
        self.current_context = "daily"

    def set_context(self, context_name, manual=False):
        context_name = context_name.lower()
        if context_name in self.contexts:
            self.current_context = context_name

    def detect_from_gesture(self, gesture):
        """Auto-detect context based on unique gestures"""
        gesture = gesture.lower()
        
        # Mapping gestures strictly to their context
        for ctx_name, ctx_data in self.contexts.items():
            intents_dict = ctx_data.get("intents", {})
            if gesture in intents_dict:
                # If it's a unique defining gesture for a context, return that context
                if gesture in ["g_mobile"]:
                    return "shop"
                if gesture in ["g_ticket", "g_pune", "g_mumbai"]:
                    return "transport"
                if gesture in ["g_water", "g_help"]:
                    return "daily"
                
        return self.current_context

    def generate_sentence(self, raw_intents):
        if not raw_intents:
            return ""

        context_data = self.contexts.get(self.current_context, {})
        if not context_data:
            return " ".join(raw_intents)

        intents_dict = context_data.get("intents", {})
        templates = context_data.get("templates", [])
        fallback = context_data.get("fallback", "{intents}")

        # Parse intents
        parsed_intents = {}
        marathi_words = []
        for intent in raw_intents:
            intent = intent.lower()
            if intent in intents_dict:
                intent_info = intents_dict[intent]
                parsed_intents[intent_info["type"]] = intent_info["marathi"]
                marathi_words.append(intent_info["marathi"])
            else:
                # Cross-context translation
                found_translation = intent
                found_type = None
                for ctx_data in self.contexts.values():
                    if intent in ctx_data.get("intents", {}):
                        found_translation = ctx_data["intents"][intent]["marathi"]
                        found_type = ctx_data["intents"][intent]["type"]
                        break
                
                if found_type:
                    parsed_intents[found_type] = found_translation
                
                if found_translation == intent:
                    found_translation = intent.replace("g_", "")
                marathi_words.append(found_translation)

        # Build sentence by selecting best template
        matched_sentence = None
        
        # 1. Try strict matching (exact number of types)
        for tmpl in templates:
            required_types = tmpl.get("required_types", [])
            if set(required_types) == set(parsed_intents.keys()):
                sentence = tmpl["template"]
                for req in required_types:
                    sentence = sentence.replace(f"{{{req}}}", parsed_intents[req])
                matched_sentence = sentence
                break

        # 2. Try relaxed match (all required types present, but ignoring extra intents)
        if not matched_sentence:
            for tmpl in templates:
                required_types = tmpl.get("required_types", [])
                if all(req in parsed_intents for req in required_types):
                    sentence = tmpl["template"]
                    for req in required_types:
                        sentence = sentence.replace(f"{{{req}}}", parsed_intents[req])
                    matched_sentence = sentence
                    break

        if matched_sentence:
            return matched_sentence

        # Fallback
        fallback_str = fallback.replace("{intents}", " ".join(marathi_words))
        return fallback_str