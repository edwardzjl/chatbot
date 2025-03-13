from serpapi import GoogleSearch

def search(query):
    params = {
        "api_key": "0a07daa35bea72f9fdb0aa13ccd01b9d472cc40075f482ba558e93723d1c670c",
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
