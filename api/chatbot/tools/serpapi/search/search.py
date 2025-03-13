from serpapi import GoogleSearch


def search(query):
    params = {
        "engine": "google",
        "q": "今天天气怎么样",
        "google_domain": "google.com",
        "start": "0",
        "num": "5",
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    if "answer_box" in results:
        return parse_answer_box(results["answer_box"])
    # don't forget to include the search url as metadata:
    # results["search_metadata"]["google_url"]
    ...
