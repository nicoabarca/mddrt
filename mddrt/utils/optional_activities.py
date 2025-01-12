from typing import ClassVar


class OptionalActivities:
    _instance = None
    _activities: ClassVar[list] = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def set_activities(self, activities: list[str]) -> None:
        if isinstance(activities, list) and all(isinstance(item, str) for item in activities):
            self._activities = activities
        else:
            error_msg = "Activities must be a list of strings"
            raise ValueError(error_msg)

    def reset_activities(self) -> None:
        self._activities = []

    def get_activities(self) -> list[str]:
        return self._activities
