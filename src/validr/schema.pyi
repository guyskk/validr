import typing


class Builder:
    def __getitem__(self, keys: typing.Iterable[str]) -> "Builder": ...
    def __getattr__(self, name: str) -> "Builder": ...
    def __call__(self, *args, **kwargs) -> "Builder": ...


T: Builder
