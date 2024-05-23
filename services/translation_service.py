from utils.bhashini_utils import translate
from utils.redis_utils import get_redis_cache, set_redis_cache


def get_translated_text(text, source_lang="en", target_lang="hi"):
    # Check if data present in cache? if yes return else translate
    cache_key = f"{text}_{source_lang}_{target_lang}"
    cache_translation = get_redis_cache(cache_key)

    if cache_translation:
        cache_translation = cache_translation.decode('utf-8')
        print("translation found in cache", cache_translation)
        return cache_translation
    else:
        translated_text = translate({
            "text": text,
            "source_language": source_lang,
            "target_language": target_lang,
        })
        if translated_text:
            set_redis_cache(cache_key, translated_text)
        return translated_text
