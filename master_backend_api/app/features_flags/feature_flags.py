# https://www.flagsmith.com/
from enum import StrEnum
import json

from flagsmith import Flagsmith

from settings import settings


class Features(StrEnum):
    SEARCH_PRODUCT_IN_DESCRIPTION = "search_product_in_description"


class FeatureFlags:
    def __init__(self):
        self.service = Flagsmith(environment_key=settings.FLAGSMITH_API_KEY)
        self.flags = self.service.get_environment_flags()

    @property
    def should_search_in_description(self) -> bool:
        is_feature_enabled = self.flags.is_feature_enabled(Features.SEARCH_PRODUCT_IN_DESCRIPTION)
        if is_feature_enabled:
            feature_content = self.flags.get_feature_value(Features.SEARCH_PRODUCT_IN_DESCRIPTION)
            details = json.loads(feature_content)
            if details["enabled"]:
                return True
        return False
