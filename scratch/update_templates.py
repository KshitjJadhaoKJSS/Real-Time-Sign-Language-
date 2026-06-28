import json

templates = {
  "shop": {
    "intents": {
      "g_one": {"type": "quantity", "marathi": "एक"},
      "g_two": {"type": "quantity", "marathi": "दोन"},
      "g_buy": {"type": "action_buy", "marathi": "घ्यायचा आहे"},
      "g_price": {"type": "query_price", "marathi": "किती आहे?"},
      "g_mobile": {"type": "item", "marathi": "मोबाईल"}
    },
    "templates": [
      {
        "required_types": ["quantity", "item", "action_buy"],
        "template": "मला {quantity} {item} {action_buy}."
      },
      {
        "required_types": ["quantity", "item"],
        "template": "मला {quantity} {item} पाहिजे."
      },
      {
        "required_types": ["item", "query_price"],
        "template": "या {item}ची किंमत {query_price}"
      },
      {
        "required_types": ["item", "action_buy"],
        "template": "मला {item} {action_buy}."
      },
      {
        "required_types": ["item"],
        "template": "मला {item} पाहिजे."
      }
    ],
    "fallback": "{intents}"
  },
  "transport": {
    "intents": {
      "g_ticket": {"type": "item", "marathi": "तिकीट"},
      "g_one": {"type": "quantity", "marathi": "एक"},
      "g_two": {"type": "quantity", "marathi": "दोन"},
      "g_pune": {"type": "location", "marathi": "पुणे"},
      "g_mumbai": {"type": "location", "marathi": "मुंबई"},
      "g_buy": {"type": "action_buy", "marathi": "पाहिजे"},
      "g_when": {"type": "query_when", "marathi": "कधी आहे?"},
      "g_price": {"type": "query_price", "marathi": "किती आहे?"}
    },
    "templates": [
      {
        "required_types": ["location", "quantity", "item"],
        "template": "मला {location}चे {quantity} {item} पाहिजे."
      },
      {
        "required_types": ["location", "query_when"],
        "template": "{location}ची गाडी {query_when}"
      },
      {
        "required_types": ["location", "item", "query_price"],
        "template": "{location}चे {item} {query_price}"
      },
      {
        "required_types": ["location", "item"],
        "template": "मला {location}चे {item} पाहिजे."
      },
      {
        "required_types": ["quantity", "item"],
        "template": "मला {quantity} {item} पाहिजे."
      },
      {
        "required_types": ["item", "query_when"],
        "template": "{item} {query_when}"
      },
      {
        "required_types": ["item", "query_price"],
        "template": "{item}चे {query_price}"
      },
      {
        "required_types": ["item"],
        "template": "मला {item} पाहिजे."
      }
    ],
    "fallback": "{intents}"
  },
  "daily": {
    "intents": {
      "g_help": {"type": "action_help", "marathi": "मदत करा"},
      "g_water": {"type": "item", "marathi": "पाणी"},
      "g_buy": {"type": "action_buy", "marathi": "द्या"}
    },
    "templates": [
      {
        "required_types": ["item", "action_buy"],
        "template": "मला {item} {action_buy}."
      },
      {
        "required_types": ["item"],
        "template": "मला {item} पाहिजे."
      },
      {
        "required_types": ["action_help"],
        "template": "मला {action_help}."
      }
    ],
    "fallback": "{intents}"
  }
}

with open("data/templates.json", "w", encoding="utf-8") as f:
    json.dump(templates, f, ensure_ascii=False, indent=2)

print("Updated templates.json")
