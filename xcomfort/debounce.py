from threading import Timer


def debounce(wait):
    """Decorator that will postpone a functions
    execution until after wait seconds
    have elapsed since the last time it was invoked."""

    def decorator(fn):
        def debounced(*args, **kwargs):
            def callIt():
                fn(*args, **kwargs)

            try:
                debounced.t.cancel()
            except AttributeError:
                pass
            debounced.originalFn = fn
            debounced.t = Timer(wait, callIt)
            debounced.t.start()

        return debounced

    return decorator
