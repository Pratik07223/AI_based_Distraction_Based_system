import pyttsx3
import threading

# =========================
# 🔊 INIT ENGINE (ONCE)
# =========================
engine = pyttsx3.init()

# Voice settings
engine.setProperty('rate', 170)     # speed
engine.setProperty('volume', 1.0)   # max volume

voices = engine.getProperty('voices')

# Try to pick English voice by default
DEFAULT_VOICE = voices[0].id if voices else None

# =========================
# 🔁 THREAD FUNCTION
# =========================
def speak_thread(text, voice_id):
    try:
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 170)
        local_engine.setProperty('volume', 1.0)

        if voice_id:
            local_engine.setProperty('voice', voice_id)

        local_engine.say(text)
        local_engine.runAndWait()
    except:
        pass


# =========================
# 🚀 MAIN FUNCTION
# =========================
def speak_alert(text, lang="en", gender="female"):
    """
    lang: 'en' or 'hi'
    gender: 'male' or 'female'
    """

    voice_id = None

    try:
        for v in voices:
            name = v.name.lower()

            # 🎯 LANGUAGE + GENDER SELECTION
            if lang == "hi" and "hindi" in name:
                voice_id = v.id
                break

            elif lang == "en":
                if gender == "female" and ("female" in name or "zira" in name):
                    voice_id = v.id
                    break
                elif gender == "male" and ("male" in name or "david" in name):
                    voice_id = v.id
                    break

        # fallback
        if voice_id is None:
            voice_id = DEFAULT_VOICE

    except:
        voice_id = DEFAULT_VOICE

    # 🔥 NON-BLOCKING (THREAD)
    thread = threading.Thread(target=speak_thread, args=(text, voice_id))
    thread.daemon = True
    thread.start()