import unittest

from poc.expressions import t
from poc.observe import NamedTraitListener, ListenerPath


class TestExpression(unittest.TestCase):

    def test_basic_t(self):
        expression = t("name")
        actual, = expression.as_paths()
        self.assertEqual(
            actual,
            ListenerPath(
                node=NamedTraitListener(
                    name="name",
                    notify=True,
                    optional=False,
                ),
                nexts=(),
            ),
        )

    def test_basic_path(self):
        expression = t("name").t("attr")
        actual, = expression.as_paths()
        self.assertEqual(
            actual,
            ListenerPath(
                node=NamedTraitListener(
                    name="name",
                    notify=True,
                    optional=False,
                ),
                nexts=set([
                    ListenerPath(
                        node=NamedTraitListener(
                            name="attr",
                            notify=True,
                            optional=False,
                        ),
                    )
                ]),
            ),
        )

    def test_or_expression(self):
        expression = t("name") | t("attr")
        path1, path2 = expression.as_paths()
        self.assertEqual(
            path1,
            ListenerPath(
                node=NamedTraitListener(
                    name="name",
                    notify=True,
                    optional=False,
                ),
            ),
        )
        self.assertEqual(
            path2,
            ListenerPath(
                node=NamedTraitListener(
                    name="attr",
                    notify=True,
                    optional=False,
                ),
            ),
        )

    def test_then(self):
        expression = t("child").then(t("age") | t("name"))
        actual, = expression.as_paths()
        self.assertEqual(
            actual,
            ListenerPath(
                node=NamedTraitListener(
                    name="child",
                    notify=True,
                    optional=False,
                ),
                nexts=set([
                    ListenerPath(
                        node=NamedTraitListener(
                            name="age",
                            notify=True,
                            optional=False,
                        ),
                    ),
                    ListenerPath(
                        node=NamedTraitListener(
                            name="name",
                            notify=True,
                            optional=False,
                        ),
                    ),
                ])
            )
        )

    def test_recursion(self):
        expression = t("root").recursive(t("left") | t("right"))
        actual, = expression.as_paths()
        self.assertEqual(actual.node.name, "root")

        self.assertEqual(
            set(p.node.name for p in actual.nexts),
            set(["left", "right"])
        )
        nexts = list(actual.nexts)
        self.assertCountEqual(nexts[0].nexts, set(actual.nexts))
        self.assertCountEqual(nexts[1].nexts, set(actual.nexts))

    def test_recursion_then_extend(self):
        expression = (
            t("root").recursive(t("left") | t("right")).t("value")
        )
        actual, = expression.as_paths()

        # First level, root only
        self.assertEqual(actual.node.name, "root")

        # Second level, left or right
        self.assertCountEqual(
            [p.node.name for p in actual.nexts],
            ["left", "right"],
        )

        # Third level, left or right or value
        for path in actual.nexts:
            self.assertCountEqual(
                [p.node.name for p in path.nexts],
                ["left", "right", "value"],
            )


if __name__ == "__main__":
    unittest.main()
