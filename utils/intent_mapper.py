"""
Intent pattern matcher for MSL recognition
MSL ओळखीसाठी हेतू पॅटर्न मॅपर
"""
import json
import os
from typing import List, Dict, Optional, Tuple

class IntentPatternMatcher:
    """
    Maps gesture sequences to intents and Marathi sentences
    हावभाव अनुक्रम हेतू आणि मराठी वाक्यांशी मॅप करते
    """
    
    def __init__(self, mappings_path: str = None):
        """
        Initialize intent pattern matcher
        
        Args:
            mappings_path: Path to intent mappings JSON file
        """
        if mappings_path is None:
            mappings_path = os.path.join('models', 'intent_mappings.json')
        
        self.mappings_path = mappings_path
        self.intent_patterns = self._initialize_patterns()
        
        # Try to load saved patterns
        if os.path.exists(mappings_path):
            self.load_patterns(mappings_path)
    
    def _initialize_patterns(self) -> Dict:
        """Initialize default intent patterns"""
        return {
            # ============== SHOP CONTEXT ==============
            'SHOP': {
                'buy_item': {
                    'patterns': [
                        ['हे', 'हवे'],
                        ['ते', 'हवे'],
                        ['हे', 'पाहिजे'],
                        ['द्या', 'हे'],
                    ],
                    'output': 'मला हे पाहिजे',
                    'description': 'Want to buy this item'
                },
                'ask_price': {
                    'patterns': [
                        ['किंमत'],
                        ['हे', 'किंमत'],
                        ['किती'],
                        ['किंमत', 'काय'],
                    ],
                    'output': 'याची किंमत किती आहे?',
                    'description': 'Ask price of item'
                },
                'ask_price_that': {
                    'patterns': [
                        ['ते', 'किंमत'],
                        ['ते', 'किती'],
                    ],
                    'output': 'त्याची किंमत किती आहे?',
                    'description': 'Ask price of that item'
                },
                'show_item': {
                    'patterns': [
                        ['दाखवा', 'हे'],
                        ['हे', 'दाखवा'],
                    ],
                    'output': 'हे दाखवा',
                    'description': 'Show this item'
                },
                'too_expensive': {
                    'patterns': [
                        ['किंमत', 'नाही'],
                        ['नाही', 'किंमत'],
                        ['जास्त'],
                    ],
                    'output': 'किंमत जास्त आहे',
                    'description': 'Price is too high'
                },
                'will_buy': {
                    'patterns': [
                        ['ठीक', 'घे'],
                        ['होय', 'घे'],
                    ],
                    'output': 'ठीक आहे, घेतो',
                    'description': 'Will buy it'
                },
            },
            
            # ============== MARKET CONTEXT ==============
            'MARKET': {
                'buy_1kg': {
                    'patterns': [
                        ['द्या', 'एक', 'किलो'],
                        ['एक', 'किलो', 'द्या'],
                        ['हवे', 'एक', 'किलो'],
                        ['एक', 'किलो'],
                    ],
                    'output': 'मला १ किलो द्या',
                    'description': 'Give 1 kg'
                },
                'buy_2kg': {
                    'patterns': [
                        ['द्या', 'दोन', 'किलो'],
                        ['दोन', 'किलो', 'द्या'],
                        ['दोन', 'किलो'],
                    ],
                    'output': 'मला २ किलो द्या',
                    'description': 'Give 2 kg'
                },
                'buy_half_kg': {
                    'patterns': [
                        ['द्या', 'अर्धा', 'किलो'],
                        ['अर्धा', 'किलो', 'द्या'],
                        ['अर्धा', 'किलो'],
                    ],
                    'output': 'मला अर्धा किलो द्या',
                    'description': 'Give half kg'
                },
                'vegetable_price': {
                    'patterns': [
                        ['भाजी', 'किंमत'],
                        ['भाजी', 'किती'],
                    ],
                    'output': 'भाजीची किंमत किती?',
                    'description': 'Vegetable price'
                },
                'fruit_price': {
                    'patterns': [
                        ['फळ', 'किंमत'],
                        ['फळ', 'किती'],
                    ],
                    'output': 'फळाची किंमत किती?',
                    'description': 'Fruit price'
                },
            },
            
            # ============== RAILWAY STATION CONTEXT ==============
            'RAILWAY_STATION': {
                'ticket_pune': {
                    'patterns': [
                        ['तिकीट', 'पुणे'],
                        ['पुणे', 'तिकीट'],
                        ['द्या', 'तिकीट', 'पुणे'],
                    ],
                    'output': 'मला पुण्याचे तिकीट पाहिजे',
                    'description': 'Ticket to Pune'
                },
                'ticket_mumbai': {
                    'patterns': [
                        ['तिकीट', 'मुंबई'],
                        ['मुंबई', 'तिकीट'],
                    ],
                    'output': 'मला मुंबईचे तिकीट पाहिजे',
                    'description': 'Ticket to Mumbai'
                },
                'train_time': {
                    'patterns': [
                        ['ट्रेन', 'वेळ'],
                        ['ट्रेन', 'केव्हा'],
                        ['वेळ', 'ट्रेन'],
                    ],
                    'output': 'ट्रेन किती वाजता आहे?',
                    'description': 'Train timing'
                },
                'platform_number': {
                    'patterns': [
                        ['ट्रेन', 'कुठे'],
                        ['प्लॅटफॉर्म', 'कोणता'],
                    ],
                    'output': 'ट्रेन कोणत्या प्लॅटफॉर्मवर आहे?',
                    'description': 'Which platform'
                },
                'ticket_price': {
                    'patterns': [
                        ['तिकीट', 'किंमत'],
                        ['तिकीट', 'किती'],
                    ],
                    'output': 'तिकिटाची किंमत किती?',
                    'description': 'Ticket price'
                },
            },
            
            # ============== HOSPITAL CONTEXT ==============
            'HOSPITAL': {
                'need_help': {
                    'patterns': [
                        ['मदत', 'हवे'],
                        ['मदत'],
                    ],
                    'output': 'मला मदत पाहिजे',
                    'description': 'Need help'
                },
                'where_doctor': {
                    'patterns': [
                        ['डॉक्टर', 'कुठे'],
                        ['कुठे', 'डॉक्टर'],
                    ],
                    'output': 'डॉक्टर कुठे आहेत?',
                    'description': 'Where is doctor'
                },
                'medicine_need': {
                    'patterns': [
                        ['औषध', 'हवे'],
                        ['औषध', 'पाहिजे'],
                        ['द्या', 'औषध'],
                    ],
                    'output': 'मला औषध पाहिजे',
                    'description': 'Need medicine'
                },
            },
            
            # ============== RESTAURANT CONTEXT ==============
            'RESTAURANT': {
                'want_food': {
                    'patterns': [
                        ['जेवण', 'हवे'],
                        ['हवे', 'जेवण'],
                        ['द्या', 'जेवण'],
                    ],
                    'output': 'मला जेवण हवे',
                    'description': 'Want food'
                },
                'want_water': {
                    'patterns': [
                        ['पाणी', 'हवे'],
                        ['द्या', 'पाणी'],
                    ],
                    'output': 'मला पाणी द्या',
                    'description': 'Want water'
                },
                'food_price': {
                    'patterns': [
                        ['जेवण', 'किंमत'],
                        ['जेवण', 'किती'],
                    ],
                    'output': 'जेवणाची किंमत किती?',
                    'description': 'Food price'
                },
            },
            
            # ============== GENERAL CONTEXT ==============
            'GENERAL': {
                'thank_you': {
                    'patterns': [
                        ['धन्यवाद'],
                    ],
                    'output': 'धन्यवाद',
                    'description': 'Thank you'
                },
                'sorry': {
                    'patterns': [
                        ['माफ करा'],
                    ],
                    'output': 'माफ करा',
                    'description': 'Sorry'
                },
                'yes': {
                    'patterns': [
                        ['होय'],
                        ['ठीक'],
                    ],
                    'output': 'होय',
                    'description': 'Yes'
                },
                'no': {
                    'patterns': [
                        ['नाही'],
                    ],
                    'output': 'नाही',
                    'description': 'No'
                },
                'wait': {
                    'patterns': [
                        ['थांबा'],
                        ['थांबा', 'कृपया'],
                    ],
                    'output': 'जरा थांबा',
                    'description': 'Wait'
                },
            }
        }
    
    def match_intent(self, gesture_sequence: List[str], context: str = 'GENERAL') -> Optional[Tuple[str, str, str]]:
        """
        Match gesture sequence to intent
        
        Args:
            gesture_sequence: List of gesture labels (Marathi)
            context: Current context
            
        Returns:
            Tuple of (intent_name, marathi_output, description) or None
        """
        if not gesture_sequence:
            return None
        
        # Get patterns for current context
        context_patterns = self.intent_patterns.get(context, {})
        
        # Also check GENERAL context
        if context != 'GENERAL':
            general_patterns = self.intent_patterns.get('GENERAL', {})
            context_patterns = {**general_patterns, **context_patterns}
        
        # Try to match patterns
        for intent_name, intent_data in context_patterns.items():
            patterns = intent_data['patterns']
            
            for pattern in patterns:
                if self._matches_pattern(gesture_sequence, pattern):
                    return (
                        intent_name,
                        intent_data['output'],
                        intent_data['description']
                    )
        
        return None
    
    def _matches_pattern(self, sequence: List[str], pattern: List[str]) -> bool:
        """Check if gesture sequence matches a pattern"""
        # Exact match
        if sequence == pattern:
            return True
        
        # Partial match (sequence contains all pattern elements in order)
        if len(sequence) >= len(pattern):
            pattern_idx = 0
            for gesture in sequence:
                if pattern_idx < len(pattern) and gesture == pattern[pattern_idx]:
                    pattern_idx += 1
            
            if pattern_idx == len(pattern):
                return True
        
        return False
    
    def save_patterns(self, filepath: str = None):
        """Save intent patterns to JSON"""
        filepath = filepath or self.mappings_path
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.intent_patterns, f, ensure_ascii=False, indent=2)
        
        print(f"Intent patterns saved to: {filepath}")
    
    def load_patterns(self, filepath: str = None):
        """Load intent patterns from JSON"""
        filepath = filepath or self.mappings_path
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.intent_patterns = json.load(f)
            print(f"Intent patterns loaded from: {filepath}")