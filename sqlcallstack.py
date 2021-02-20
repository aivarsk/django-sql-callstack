import django.db.models.sql.query

django.db.models.sql.query.Query._extra_select_orig = (
    django.db.models.sql.query.Query.extra_select
)


class CallStackWhenUsed:
    def __init__(self):
        self._first_template_frame = False

    def __str__(self):
        import sys

        f = sys._getframe(0)
        bt = []
        while f:
            bt.append(f)
            f = f.f_back

        stack = []
        have_source = False
        for f in bt:
            if self.application_file(f.f_code.co_filename):
                stack.append("{}:{}".format(f.f_code.co_filename, f.f_lineno))
            loc = self.template_location(f)
            if loc:
                filename, lineno = loc
                stack.append("{}:{}".format(filename, lineno))

        return "/*" + "|".join(reversed(stack)) + "*/true"

    def template_location(self, frame):
        node = frame.f_locals.get("node")
        if not self._first_template_frame or type(node).__name__ == "IncludeNode":
            if node and hasattr(node, "source"):
                origin, (start, end) = getattr(node, "source")
                self._first_template_frame = True
                return origin, origin.reload()[:start].count("\n") + 1

    @staticmethod
    def application_file(filename):
        return not filename.startswith("/usr/local/lib/")


@property
def extra_select(self):
    if not getattr(self, "_callstack_injected", False):
        self.add_extra(
            select=None,
            select_params=None,
            where=[CallStackWhenUsed()],
            params=[],
            tables=None,
            order_by=None,
        )
        setattr(self, "_callstack_injected", True)
    return self._extra_select_orig


django.db.models.sql.query.Query.extra_select = extra_select
