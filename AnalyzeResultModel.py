class Result:
    def __init__(self):
        self.DateTaken = None
        self.Location = None
        self.Tags = []
        self.Caption = None

class Location:
    def __init__(self):
        self.Country = None
        self.State = None
        self.County = None
        self.City = None

class Tag:
    def __init__(self):
        self.Name = None
        self.Confidence = None

class Caption:
    def __init__(self):
        self.Title = None
        self.IsPositive = None
        self.Confidence = None