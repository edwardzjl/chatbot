from .air_quality import AirQualityAnswerBox
from .currency_converter import CurrencyConverterAnswerBox
from .dictionary import DictionaryAnswerBox
from .finance import FinanceAnswerBox
from .flight_duration import FlightDurationAnswerBox
from .flight_status import FlightStatusAnswerBox
from .flights import FlightsAnswerBox
from .formula import FormulaAnswerBox
from .hotels import HotelsAnswerBox
from .hours import HoursAnswerBox
from .math_solution import MathSolutionAnswerBox
from .organic_result import ExpandedListAnswerBox, OrganicResultAnswerBox
from .population import PopulationAnswerBox
from .public_alerts import PublicAlertsAnswerBox
from .time import TimeAnswerBox
from .translation import TranslationAnswerBox
from .transport_options import TransportOptionsAnswerBox
from .unit_converter import UnitConverterAnswerBox
from .weather import WeatherAnswerBox


def parse_answer_box(raw: dict) -> dict:
    """Parse the answer box in search results.

    Using pydantic as it by default ignores extra fields, so I only need to define those I'm interested in.
    Pydantic surely introduces some overhead, but it's a trade-off between performance and maintainability.
    And in case the upstream API changed, pydantic will provide a hopefully helpful error message.
    See <https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra>
    Also, I have not tried out these results:
    - <https://serpapi.com/direct-answer-box-api#api-examples-list-answer-box>
    - <https://serpapi.com/direct-answer-box-api#api-examples-organic-result-answer-box-type-2>
    - <https://serpapi.com/direct-answer-box-api#api-examples-organic-result-answer-box-type-3>
    - <https://serpapi.com/direct-answer-box-api#api-examples-organic-result-answer-box-type-4>
    - <https://serpapi.com/direct-answer-box-api#api-examples-organic-result-answer-box-type-5>
    - <https://serpapi.com/direct-answer-box-api#api-examples-multiple-answer-box>
    - <https://serpapi.com/direct-answer-box-api#api-examples-directions-answer-box-car>
    - <https://serpapi.com/direct-answer-box-api#api-examples-directions-answer-box-train>
    """
    res_type = raw.get("type")
    if res_type == "calculator_result":
        # <https://serpapi.com/direct-answer-box-api#api-examples-calculator-answer-box>
        return raw
    if res_type == "weather_result":
        return WeatherAnswerBox.model_validate(raw).model_dump()
    if res_type == "finance_results":
        return FinanceAnswerBox.model_validate(raw).model_dump()
    if res_type == "population_result":
        return PopulationAnswerBox.model_validate(raw).model_dump()
    if res_type == "currency_converter":
        return CurrencyConverterAnswerBox.model_validate(raw).model_dump()
    if res_type == "google_flights":
        return FlightsAnswerBox.model_validate(raw).model_dump()
    if res_type == "flight_duration":
        return FlightDurationAnswerBox.model_validate(raw).model_dump()
    if res_type == "hotels":
        return HotelsAnswerBox.model_validate(raw).model_dump()
    if res_type == "dictionary_results":
        return DictionaryAnswerBox.model_validate(raw).model_dump()
    if res_type == "organic_result":
        if "expanded_list" in raw:
            return ExpandedListAnswerBox.model_validate(raw).model_dump()
        return OrganicResultAnswerBox.model_validate(raw).model_dump()
    if res_type == "translation_result":
        return TranslationAnswerBox.model_validate(raw).model_dump()
    if res_type == "transport_options":
        return TransportOptionsAnswerBox.model_validate(raw).model_dump()
    if res_type == "formula":
        return FormulaAnswerBox.model_validate(raw).model_dump()
    if res_type == "unit_converter":
        return UnitConverterAnswerBox.model_validate(raw).model_dump()
    if res_type == "hours":
        return HoursAnswerBox.model_validate(raw).model_dump()
    if res_type == "time":
        return TimeAnswerBox.model_validate(raw).model_dump()
    if res_type == "public_alerts":
        return PublicAlertsAnswerBox.model_validate(raw).model_dump()
    if res_type == "air_quality":
        return AirQualityAnswerBox.model_validate(raw).model_dump()
    if res_type == "math_solution":
        return MathSolutionAnswerBox.model_validate(raw).model_dump()
    if res_type == "flight_status":
        return FlightStatusAnswerBox.model_validate(raw).model_dump()
