class ClassificationReach(object):
    def __init__(self, polyline, classification):
        """
        :type polyline: The complete polyline
        :type classification: What the hydrologic regime of the stream is
        """
        self.polyline = polyline
        self.classification = classification