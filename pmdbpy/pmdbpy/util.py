import functools

def overrides(*classes):
  def overrider(method):
    assert(method.__name__ in
      functools.reduce(lambda a, b: set(a) | set(b), map(dir, classes), set()))
    return method

  return overrider
