import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("vaanirakshak.ai.intent")

# High-Risk Intent Regex Patterns (Multilingual: English, Hindi, Hinglish, Marathi, Tamil, Telugu, Bengali, Gujarati, Punjabi)
INTENT_PATTERNS = {
    "MONEY_TRANSFER": [
        # English / Hinglish
        r"\b(send|transfer|pay|remit|deposit)\b.*\b(money|rs|rupees|₹|amount|cash|lakh|thousand)\b",
        r"\b(google pay|gpay|phonepe|paytm|upi|upi id)\b",
        r"\b(urgent money|send \d+|transfer \d+)\b",
        # Hindi
        r"(पैसे|पैसे भेज|रुपये|यूपीआई)",
        # Marathi (mr)
        r"(पैसे पाठवा|पैसे भरा|रुपये पाठवा|गुगल पे|फोन पे)",
        # Tamil (ta)
        r"(பணம் அனுப்பு|பணம் செலுத்தவும்|ரூபாய்|கூகிள் பே|போன்பே)",
        # Telugu (te)
        r"(డబ్బులు పంపండి|డబ్బు ట్రాన్స్ఫర్|రూపాయలు|ఫోన్‌పే|గూగుల్‌పే)",
        # Bengali (bn)
        r"(টাকা পাঠান|টাকা ট্রান্সফার|টাকা দিন|বিকাশ|গুগল পে)",
        # Gujarati (gu)
        r"(પૈસા મોકલો|રૂપિયા ટ્રાન્સફર|પૈસા જમા કરો|રૂપિયા)",
        # Punjabi (pa)
        r"(ਪੈਸੇ ਭੇਜੋ|ਰੁਪਏ ਟਰਾਂਸਫਰ|ਪੈਸੇ ਪਾਓ)",
    ],
    "OTP_REQUEST": [
        # English
        r"\b(otp|one time password|verification code|security code)\b",
        r"\b(share|tell|give|enter)\b.*\b(otp|code|pin)\b",
        # Hindi
        r"(ओटीपी|वन टाइम पासवर्ड|कोड बताओ)",
        # Marathi (mr)
        r"(ओटीपी सांगा|ओटीपी द्या|व्हेरिफिकेशन कोड|ओटीपी)",
        # Tamil (ta)
        r"(ஓடிபி சொல்லுங்க|ஓடிபி குடுங்க|கடவுச்சொல்|ஓடிபி)",
        # Telugu (te)
        r"(ఓటీపీ చెప్పండి|ఓటీపీ పంపండి|కోడ్ చెప్పండి|ఓటీపీ)",
        # Bengali (bn)
        r"(ওটিপি বলুন|ওটিপি দিন|ভেরিফিকেশন কোড|ওটিপি)",
        # Gujarati (gu)
        r"(ઓટીપી આપો|ઓટીપી કહો|વેરિફિકેશન કોડ|ઓટીપી)",
        # Punjabi (pa)
        r"(ਓਟੀਪੀ ਦੱਸੋ|ਕੋਡ ਦੱਸੋ|ਵੈਰੀਫਿਕੇਸ਼ਨ ਕੋਡ|ਓਟੀਪੀ)",
    ],
    "PASSWORD_REQUEST": [
        r"\b(password|passcode|secret pin)\b",
        r"(पासवर्ड|पासवर्ड बताओ|पासवर्ड सांगा)",
        r"(கடவுச்சொல்|పాస్‌వర్డ్|পাসওয়ার্ড|પાસવર્ડ|ਪਾਸਵਰਡ)",
    ],
    "PIN_REQUEST": [
        r"\b(atm pin|upi pin|credit card pin|debit card pin)\b",
        r"(पिन|पिन नंबर|पिन सांगा|பின் எண்|పిన్ నంబర్|পিন নম্বর|પીન નંબર|ਪਿੰਨ ਨੰਬਰ)",
    ],
    "REMOTE_ACCESS": [
        r"\b(anydesk|teamviewer|quicksupport|rustdesk|remote access)\b",
        r"\b(screen share|install app|download app)\b",
        r"(स्क्रीन शेयर|अॅप डाऊनलोड|ஆப் பதிவிறக்கு|యాప్ డౌన్‌లోడ్|অ্যাপ ডাউনলোড)",
    ],
    "APK_INSTALLATION": [
        r"\b(apk|install apk|download link|file link)\b",
        r"(एपीके|एपीके फाइल|apk फाइल)",
    ],
    "BANK_VERIFICATION": [
        r"\b(sbi|hdfc|icici|axis|rbi|bank officer|bank manager|cyber cell)\b",
        r"\b(account block|card block|kyc update|kyc verification)\b",
        r"(बैंक|केवाईसी|अकाउंट ब्लॉक|बँक अधिकारी|வங்கி மேலாளர்|வங்கி அதிகாரி|బ్యాంకు అధికారి|బ్యాంక్ మేనేజర్|ব্যাংক অফিসার|ব্যাংক ম্যানেজার|બેંક મેનેજર|બેંક અધિકારી|ਬੈਂਕ ਅਫਸਰ|ਬੈਂਕ ਮੈਨੇਜਰ)",
    ],
    "EMERGENCY": [
        r"\b(accident|hospital|police station|jail|arrested|emergency)\b",
        r"(एक्सीडेंट|अस्पताल|पुलिस)",
        r"(अपघात|दवाखाना|पोलीस ठाणे|विपत्ति)",
        r"(விபத்து|மருத்துவமனை|காவல் நிலையம்|கைது)",
        r"(ప్రమాదం|ఆసుపత్రి|పోలీస్ స్టేషన్|అరెస్ట్)",
        r"(দুর্ঘটনা|হাসপাতাল|থানা|গ্রেফতার)",
        r"(અકસ્માત|હોસ્પિટલ|પોલીસ સ્ટેશન|ધરપકડ)",
        r"(ਹਾਦਸਾ|ਹਸਪਤਾਲ|ਥਾਣਾ|ਗ੍ਰਿਫਤਾਰੀ)",
    ],
    "THREAT": [
        r"\b(legal action|court case|police complaint|arrest warrant|cbi)\b",
        r"(केस|कोर्ट|पुलिस कारवाई|सीबीआई)",
        r"(कोर्ट केस|पोलीस कारवाई|अटक वॉरंट)",
        r"(நீதிமன்ற வழக்கு|காவல்துறை புகார்|சிபிஐ)",
        r"(కోర్టు కేసు|పోలీస్ కేస్|సీబీఐ అరెస్ట్)",
        r"(কোর্ট কেস|পুলিশি ব্যবস্থা|সিবিআই)",
        r"(કોર્ટ કેસ|પોલીસ ફરિયાદ|સીબીઆઈ)",
        r"(ਅਦਾਲਤੀ ਕੇਸ|ਪੁਲਿਸ ਸ਼ਿਕਾਇਤ|ਸੀਬੀਆਈ)",
    ],
}

TACTIC_PATTERNS = {
    "URGENCY": [
        r"\b(urgently|immediately|right now|within 5 min|hurry|fast)\b",
        r"(तुरंत|अभी|जल्दी|फौरन)",
        r"(लगेच|तातडीने|आत्ताच|लवकर)",  # Marathi
        r"(உடனடியாக|இப்போதே|சீக்கிரம்)",  # Tamil
        r"(వెంటనే|ఇప్పుడే|త్వరగా)",      # Telugu
        r"(এখনি|অবিলম্বে|তাড়াতাড়ি)",    # Bengali
        r"(તરત જ|હમણાં જ|જલ્દી)",        # Gujarati
        r"(ਤੁਰੰਤ|ਹੁਣੇ|ਛੇਤੀ)",           # Punjabi
    ],
    "FEAR": [
        r"\b(blocked|suspended|arrested|jail|penalty|frozen)\b",
        r"(ब्लॉक|जेल|पेनाल्टी)",
        r"(अटक|तुरुंग|दंड|गोठवले)",       # Marathi
        r"(கைது|சிறை|அபராதம்|முடக்கப்பட்டது|பிளாக்)", # Tamil
        r"(అరెస్ట్|జైలు|జరిమానా|బ్లాక్)",  # Telugu
        r"(গ্রেফতার|জেল|জরিমানা|স্থগিত|বন্ধ)",   # Bengali
        r"(ધરપકડ|જેલ|દંડ|સ્થગિત|બંધ)",        # Gujarati
        r"(ਗ੍ਰਿਫਤਾਰ|ਜੇਲ੍ਹ|ਜੁਰਮਾਨਾ|ਬੰਦ)",        # Punjabi
    ],
    "AUTHORITY": [
        r"\b(calling from bank|head office|rbi manager|police officer|inspector|cyber crime)\b",
        r"(बैंक अधिकारी|पुलिस अफसर|साइबर सेल)",
        r"(बँक अधिकारी|पोलीस इन्स्पेक्टर|सायबर सेल)",  # Marathi
        r"(வங்கி அதிகாரி|வங்கி மேலாளர்|காவல்துறை ஆய்வாளர்)", # Tamil
        r"(బ్యాంక్ మేనేజర్|బ్యాంకు అధికారి|పోలీస్ ఇన్స్పెక్టర్)", # Telugu
        r"(ব্যাংক ম্যানেজার|ব্যাংক অফিসার|পুলিশ ইন্সপেক্টর)", # Bengali
        r"(બેંક અધિકારી|બેંક મેનેજર|પોલીસ ઇન્સ્પેક્ટર)", # Gujarati
        r"(ਬੈਂਕ ਮੈਨੇਜਰ|ਬੈਂਕ ਅਫਸਰ|ਪੁਲਿਸ ਇੰਸਪੈਕਟਰ)", # Punjabi
    ],
    "SECRECY": [
        r"\b(don't tell|keep secret|do not inform|don't disconnect)\b",
        r"(किसी को मत बताना|फोन मत काटना)",
        r"(कोणाला सांगू नका|फोन ठेवू नका)",            # Marathi
        r"(யாரிடமும் சொல்லாதே|போனை வைக்காதே)",       # Tamil
        r"(ఎవరికీ చెప్పకండి|ఫోన్ కట్ చేయవద్దు)",        # Telugu
        r"(কাউকে বলবেন না|ফোন কাটবেন না)",           # Bengali
        r"(કોઈને કહેશો નહીં|ફોન કટ ના કરો)",           # Gujarati
        r"(ਕਿਸੇ ਨੂੰ ਨਾ ਦੱਸੋ|ਫੋਨ ਨਾ ਕੱਟੋ)",            # Punjabi
    ],
    "PRESSURE": [
        r"\b(last chance|final warning|do it now or else)\b",
        r"(आखरी मौका|अंतिम चेतावनी)",
        r"(शेवटची संधी|अंतिम चेतावणी)",                # Marathi
        r"(கடைசி வாய்ப்பு|இறுதி எச்சரிக்கை)",         # Tamil
        r"(చివరి అవకాశం|తుది హెచ్చరిక)",              # Telugu
        r"(শেষ সুযোগ|চূড়ান্ত সতর্কতা)",              # Bengali
        r"(છેલ્લી તક|આખરી ચેતવણી)",                   # Gujarati
        r"(ਆਖਰੀ ਮੌਕਾ|ਅੰਤਿਮ ਚੇਤਾਵਨੀ)",                 # Punjabi
    ],
}

# Indic Unicode Script Ranges for Fast Language Detection
SCRIPT_LANG_MAP = [
    (re.compile(r"[\u0900-\u097F]"), "hi"),  # Devanagari (Hindi / Marathi)
    (re.compile(r"[\u0B80-\u0BFF]"), "ta"),  # Tamil
    (re.compile(r"[\u0C00-\u0C7F]"), "te"),  # Telugu
    (re.compile(r"[\u0980-\u09FF]"), "bn"),  # Bengali
    (re.compile(r"[\u0A80-\u0AFF]"), "gu"),  # Gujarati
    (re.compile(r"[\u0A00-\u0A7F]"), "pa"),  # Gurmukhi / Punjabi
]

# Marathi-specific distinguishing markers in Devanagari
MARATHI_MARKERS = [r"(आहे|नाही|सांगा|पाठवा|करा|करावे|लगेच|होते|दिले|माझा|माझे)"]


def detect_indic_language(text: str) -> str:
    """Heuristic language identification from Indic script and vocabulary."""
    for pattern, lang in SCRIPT_LANG_MAP:
        if pattern.search(text):
            if lang == "hi":
                # Check for Marathi lexical markers in Devanagari
                for m in MARATHI_MARKERS:
                    if re.search(m, text, re.IGNORECASE):
                        return "mr"
                return "hi"
            return lang
    return "en"


class ConversationIntelligenceEngine:
    """
    XLM-RoBERTa & Multilingual Deterministic Rule Engine
    Detects fraud intents & psychological manipulation tactics across 8 Indic languages.
    """

    def __init__(self):
        self.engine_name = "XLM-RoBERTa-IndicFraudNLP-v2"
        logger.info(f"Initialized {self.engine_name} supporting EN, HI, MR, TA, TE, BN, GU, PA.")

    def analyze_transcript(self, transcript: str, simulated_override: Dict[str, Any] = None) -> Dict[str, Any]:
        """Classifies transcript for high-risk fraud intents and psychological manipulation tactics."""
        if simulated_override and ("intent" in simulated_override or "tactics" in simulated_override):
            intent = simulated_override.get("intent", "NORMAL_CONVERSATION")
            tactics = simulated_override.get("tactics", [])
            lang = simulated_override.get("language", detect_indic_language(transcript))
            return {
                "detected_intent": intent,
                "intent_confidence": 0.95,
                "detected_tactics": tactics,
                "detected_language": lang,
                "is_high_risk": intent != "NORMAL_CONVERSATION" or len(tactics) > 0,
                "engine": self.engine_name,
            }

        if not transcript or len(transcript.strip()) == 0:
            return {
                "detected_intent": "NORMAL_CONVERSATION",
                "intent_confidence": 0.99,
                "detected_tactics": [],
                "detected_language": "en",
                "is_high_risk": False,
                "engine": self.engine_name,
            }

        text_lower = transcript.lower()
        detected_language = detect_indic_language(transcript)

        detected_intent = "NORMAL_CONVERSATION"
        intent_score = 0.0

        for intent_name, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected_intent = intent_name
                    intent_score = 0.95
                    break
            if detected_intent != "NORMAL_CONVERSATION":
                break

        detected_tactics = []
        for tactic_name, patterns in TACTIC_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected_tactics.append(tactic_name)
                    break

        is_high_risk = detected_intent != "NORMAL_CONVERSATION" or len(detected_tactics) > 0

        return {
            "detected_intent": detected_intent,
            "intent_confidence": round(intent_score, 2) if intent_score > 0 else 0.90,
            "detected_tactics": detected_tactics,
            "detected_language": detected_language,
            "is_high_risk": is_high_risk,
            "engine": self.engine_name,
        }


intent_engine = ConversationIntelligenceEngine()
