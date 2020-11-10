class Attatchment():
    def __init__(self,data):
        self._filename = data["filename"]
        self._mediaurl = data["media_url"]
        self._raw = data

    @property
    def filename(self):
        return self._filename

    @property
    def media_url(self):
        return self._mediaurl
    
    @property
    def raw(self): #Different files have different attribs
        return self._raw
        