from jinja2 import Markup


class momentjs(object):
    """
    Instead of adding <script> tags in the templates that show timestamps, we are going to create a wrapper for moment.js
    that we can invoke from the templates.
    This is going to save us time in the future if we need to change our timestamp rendering code,
    because we will have it just in one place.
    """

    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        # wraps a string into Markup obj:
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (
        self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
