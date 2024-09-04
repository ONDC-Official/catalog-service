from logger.custom_logging import log
from utils.hash_utils import get_md5_hash
from utils.mongo_utils import get_mongo_collection
from utils.bhashini_utils import translate
from utils.redis_utils import get_redis_cache, set_redis_cache


def get_translated_text(text, source_lang="en", target_lang="hi"):
    # Check if data present in cache? if yes return else translate
    cache_key = f"{text}_{source_lang}_{target_lang}"
    cache_translation = get_redis_cache(cache_key)

    if cache_translation:
        log(f"translation found in cache of {text} for {target_lang}")
        cache_translation = cache_translation.decode('utf-8')
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


def get_word_translation(text, language):
    mongo_collection = get_mongo_collection("translation")
    resp = mongo_collection.find_one({"_id": get_md5_hash(f"{text}_{language}")})
    return resp.get("translation") if resp else None


def set_word_translation(text, language, translation):
    mongo_collection = get_mongo_collection("translation")
    mongo_collection.replace_one({"_id": get_md5_hash(f"{text}_{language}")},
                                 {
                                     "text": text,
                                     "language": language,
                                     "translation": translation,
                                 }, upsert=True)
