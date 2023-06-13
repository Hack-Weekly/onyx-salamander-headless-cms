"""storage/utils.py

Borrowed from werkzeug/utils.py

"""
import os
import re
import typing as t
import unicodedata


_T = t.TypeVar("_T")


class _Missing:
    def __repr__(self) -> str:
        return "no value"

    def __reduce__(self) -> str:
        return "_missing"


_missing = _Missing()

_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_windows_device_files = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(10)),
    *(f"LPT{i}" for i in range(10)),
}

def secure_filename(filename: str) -> str:
    """Used to secure filenames.
    """

    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii","ignore").decode("ascii")
    for sep in os.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )
    if os.name == "nt" and filename and filename.split(".")[0].upper() in _windows_device_files:
        filename = f"_{filename}"
    if not filename:
        raise FileNotFoundError("No filename provided.")
    return filename


class cached_property(property, t.Generic[_T]):
    """A :func:`property` that is only evaluated once. Subsequent access
    returns the cached value. Setting the property sets the cached
    value. Deleting the property clears the cached value, accessing it
    again will evaluate it again.

    .. code-block:: python

        class Example:
            @cached_property
            def value(self):
                # calculate something important here
                return 42

        e = Example()
        e.value  # evaluates
        e.value  # uses cache
        e.value = 16  # sets cache
        del e.value  # clears cache

    If the class defines ``__slots__``, it must add ``_cache_{name}`` as
    a slot. Alternatively, it can add ``__dict__``, but that's usually
    not desirable.

    .. versionchanged:: 2.1
        Works with ``__slots__``.

    .. versionchanged:: 2.0
        ``del obj.name`` clears the cached value.
    """

    def __init__(
        self,
        fget: t.Callable[[t.Any], _T],
        name: t.Optional[str] = None,
        doc: t.Optional[str] = None,
    ) -> None:
        super().__init__(fget, doc=doc)
        self.__name__ = name or fget.__name__
        self.slot_name = f"_cache_{self.__name__}"
        self.__module__ = fget.__module__

    def __set__(self, obj: object, value: _T) -> None:
        if hasattr(obj, "__dict__"):
            obj.__dict__[self.__name__] = value
        else:
            setattr(obj, self.slot_name, value)

    def __get__(self, obj: object, type: type = None) -> _T:  # type: ignore
        if obj is None:
            return self  # type: ignore

        obj_dict = getattr(obj, "__dict__", None)

        if obj_dict is not None:
            value: _T = obj_dict.get(self.__name__, _missing)
        else:
            value = getattr(obj, self.slot_name, _missing)  # type: ignore[arg-type]

        if value is _missing:
            value = self.fget(obj)  # type: ignore

            if obj_dict is not None:
                obj.__dict__[self.__name__] = value
            else:
                setattr(obj, self.slot_name, value)

        return value

    def __delete__(self, obj: object) -> None:
        if hasattr(obj, "__dict__"):
            del obj.__dict__[self.__name__]
        else:
            setattr(obj, self.slot_name, _missing)