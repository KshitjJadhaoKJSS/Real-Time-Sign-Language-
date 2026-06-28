import os
from utils.context_manager import ContextManager

class SentenceBuilder:
    def __init__(self):
        self.intents = []
        templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "templates.json")
        self.context_manager = ContextManager(templates_path)

    def set_context(self, context_name):
        self.context_manager.set_context(context_name)
        self.reset()

    def add(self, intent):
        intent = intent.strip().lower()
        if intent == 'undo':
            self.undo()
        elif len(self.intents) == 0 or self.intents[-1] != intent:
            # Auto-detect context
            detected_ctx = self.context_manager.detect_from_gesture(intent)
            if detected_ctx != self.context_manager.get_context():
                self.context_manager.set_context(detected_ctx)
            
            self.intents.append(intent)

    def undo(self):
        if self.intents:
            self.intents.pop()

    def reset(self):
        self.intents = []

    def get_raw_intents_string(self):
        marathi_words = []
        context_data = self.context_manager.contexts.get(self.context_manager.current_context, {})
        intents_dict = context_data.get("intents", {})
        for intent in self.intents:
            if intent in intents_dict:
                marathi_words.append(f"[{intents_dict[intent]['marathi']}]")
            else:
                found = intent
                for ctx in self.context_manager.contexts.values():
                    if intent in ctx.get("intents", {}):
                        found = ctx["intents"][intent]["marathi"]
                        break
                if found == intent:
                    found = intent.replace("g_", "")
                marathi_words.append(f"[{found}]")
        return " ".join(marathi_words)

    def get_sentence(self):
        return self.context_manager.generate_sentence(self.intents)
