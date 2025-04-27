from .models import Token, Sentence, Text

from django.db.models import Count


def get_texts_id_and_data_on_tokens(data_count, texts_id, id_data, label_language):
    data_count_on_tokens = []
    id_data_count_on_tokens = []

    for data in data_count:
        if data["sentence__idtext"] not in texts_id[data[label_language]]:
            texts_id[data[label_language]].append(data["sentence__idtext"])

        if data[id_data] not in id_data_count_on_tokens:
            id_data_count_on_tokens.append(data[id_data])
            data_copy = data.copy()
            del data_copy["sentence__idtext"]
            data_count_on_tokens.append(data_copy)
        else:
            idx = 0
            while data_count_on_tokens[idx][id_data] != data[id_data]:
                idx += 1
            data_count_on_tokens[idx]["count_data"] += data["count_data"]

    return data_count_on_tokens, texts_id


def get_on_tokens(texts_id, data_count, label_language):
    count_tokens = {}

    for language in texts_id.keys():
        count_tokens_language = Token.objects.filter(
            idsentence__idtext__in=texts_id[language]
        ).aggregate(res=Count("idsentence__idtext"))
        count_tokens[language] = (
            count_tokens_language["res"] or 1
        )  # Чтобы не делить на 0

    for data in data_count:
        data["count_data_on_tokens"] = (
            data["count_data"] * 100 / count_tokens.get(data[label_language], 1)
        )

    return data_count


def get_texts_id_keys(data_count, texts_id, label_language):
    for data in data_count:
        if data[label_language] not in texts_id:
            texts_id[data[label_language]] = []
    return texts_id


def get_data_on_tokens(
    data_count, id_data, label_language, is_unique_data, is_for_one_group
):
    texts_id = {}
    texts_id = get_texts_id_keys(data_count, texts_id, label_language)

    if is_for_one_group:
        count_errors = 0

        for data in data_count:
            if data["sentence__idtext"] not in texts_id[data[label_language]]:
                texts_id[data[label_language]].append(data["sentence__idtext"])
            count_errors += data["count_data"]

        count_tokens = {}
        for language in texts_id.keys():
            count_tokens_language = Token.objects.filter(
                idsentence__idtext__in=texts_id[language]
            ).aggregate(res=Count("idsentence__idtext"))
            count_tokens[language] = count_tokens_language["res"] or 1

        data_count[0]["count_data"] = count_errors
        data_count[0]["count_data_on_tokens"] = (
            count_errors * 100 / count_tokens[data_count[0][label_language]]
        )

        return [data_count[0]]

    if is_unique_data:
        data_count_on_tokens, texts_id = get_texts_id_and_data_on_tokens(
            data_count, texts_id, id_data, label_language
        )
        data_count_on_tokens = get_on_tokens(
            texts_id, data_count_on_tokens, label_language
        )
        return data_count_on_tokens

    for data in data_count:
        count_tokens = Token.objects.filter(
            idsentence__idtext=data["sentence__idtext"]
        ).aggregate(res=Count("idsentence__idtext"))
        token_count = count_tokens["res"] or 1
        data["count_data_on_tokens"] = data["count_data"] * 100 / token_count

    return data_count


def get_data_on_tokens(
    data_count, id_data, label_language, is_unique_data, is_for_one_group
):
    texts_id = {}
    texts_id = get_texts_id_keys(data_count, texts_id, label_language)

    if is_for_one_group:
        count_errors = 0

        for data in data_count:
            if data["sentence__idtext"] not in texts_id[data[label_language]]:
                texts_id[data[label_language]].append(data["sentence__idtext"])
            count_errors += data["count_data"]

        count_tokens = {}
        for language in texts_id.keys():
            count_tokens_language = Token.objects.filter(
                idsentence__idtext__in=texts_id[language]
            ).aggregate(res=Count("idsentence__idtext"))
            count_tokens[language] = (
                count_tokens_language["res"] or 1
            )  # чтобы не делить на 0

        data_count[0]["count_data"] = count_errors
        data_count[0]["count_data_on_tokens"] = (
            count_errors * 100 / count_tokens[data_count[0][label_language]]
        )

        return [data_count[0]]

    if is_unique_data:
        data_count_on_tokens, texts_id = get_texts_id_and_data_on_tokens(
            data_count, texts_id, id_data, label_language
        )
        data_count_on_tokens = get_on_tokens(
            texts_id, data_count_on_tokens, label_language
        )
        return data_count_on_tokens

    for data in data_count:
        count_tokens = Token.objects.filter(
            idsentence__idtext=data["sentence__idtext"]
        ).aggregate(res=Count("idsentence__idtext"))
        token_count = count_tokens["res"] or 1
        data["count_data_on_tokens"] = data["count_data"] * 100 / token_count

    return data_count
