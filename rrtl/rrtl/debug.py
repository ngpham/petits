
class Debug:
  debug_on = True
  @classmethod
  def trace(self, *args):
    if Debug.debug_on:
      s = 'Debug: '
      for a in args: s += str(a) + ' '
      print(s)
