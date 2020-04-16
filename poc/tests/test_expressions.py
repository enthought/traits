import copy
import pickle
import unittest

from poc.expressions import t, metadata
from poc.observe import (
    _is_not_none,
    NamedTraitListener, ListenerPath, MetadataListener,
)


class TestBasicExpression(unittest.TestCase):

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
                branches=set([
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


class TestOrExpression(unittest.TestCase):

    def test_or_expression(self):
        expression = t("name") | t("attr")
        expected = [
            ListenerPath(
                node=NamedTraitListener(
                    name="name",
                    notify=True,
                    optional=False,
                ),
            ),
            ListenerPath(
                node=NamedTraitListener(
                    name="attr",
                    notify=True,
                    optional=False,
                ),
            ),
        ]
        self.assertCountEqual(
            expression.as_paths(),
            expected,
        )

    def test_or_with_same_nodes(self):
        e1 = t("name") | t("name")
        e2 = t("name")
        self.assertEqual(len(e1.as_paths()), 1)
        self.assertEqual(len(e2.as_paths()), 1)
        self.assertEqual(e1.as_paths(), e2.as_paths())

    def test_or_with_same_paths(self):
        e1 = t("name") | t("age")
        e2 = t("age") | t("name")
        e3 = e1 | e2
        self.assertEqual(len(e3.as_paths()), 2)

    def test_or_then_extend(self):
        e1 = (t("a").t("b") | t("c")).t("d")

        a_path, c_path = e1.as_paths()
        if a_path.node.name == "c":
            c_path, a_path = a_path, c_path

        self.assertEqual(
            [p.node.name for p in a_path.nexts],
            ["b"]
        )
        b_path, = a_path.nexts
        self.assertEqual(
            [p.node.name for p in b_path.nexts],
            ["d"]
        )
        self.assertEqual(
            [p.node.name for p in c_path.nexts],
            ["d"]
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
                branches=set([
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


class TestMetadata(unittest.TestCase):

    def test_metadata_on_its_own(self):
        expression = metadata("updated")
        actual, = expression.as_paths()
        expected = ListenerPath(
            node=MetadataListener(
                metadata_name="updated",
                value=_is_not_none,
                notify=True,
            )
        )
        self.assertEqual(actual, expected)


class TestDeepCopySupper(unittest.TestCase):
    """ Integration test with the ListenerPath to test deepcopy
    support.

    When HasTraits methods are decorated with ``observe``, we may choose
    to hash the created ``ListenerPath`` low level objects, instead of
    hashing the user-facing ``Expression`` aiming at providing a user-friendly
    interface.

    With ``ListenerPath`` being a persisted internal state of an HasTraits
    instance, it needs to support deepcopy and pickling.
    """

    def test_basic_path_pickle(self):
        expression = t("a")
        path, = expression.as_paths()
        serialized = pickle.dumps(path)
        deserialized = pickle.loads(serialized)
        self.assertEqual(deserialized, path)



class TestPicklingSupport(unittest.TestCase):
    """ Integration test with the ListenerPath for pickling support.

    When HasTraits methods are decorated with ``observe``, we may choose
    to hash the created ``ListenerPath`` low level objects, instead of
    hashing the user-facing ``Expression`` aiming at providing a user-friendly
    interface.

    With ``ListenerPath`` being a persisted internal state of an HasTraits
    instance, it needs to support deepcopy and pickling.
    """

    def test_basic_path_pickling(self):
        expression = t("a")
        path, = expression.as_paths()
        copied = copy.deepcopy(path)
        self.assertEqual(copied, path)


class TestPathEquality(unittest.TestCase):
    """ For sanity checks."""

    def test_recursion_paths(self):

        path1 = create_path()
        path2 = create_path()

        self.assertEqual(path1, path2)

    def test_recursion_paths2(self):

        path1 = create_path2()
        path2 = create_path2()

        self.assertEqual(path1, path2)


def create_path():
    path1 = ListenerPath(
        node=NamedTraitListener(
            name="root",
            notify=True,
            optional=False,
        ),
    )
    left = ListenerPath(
        node=NamedTraitListener(
            name="left",
            notify=True,
            optional=False,
        ),
    )
    right = ListenerPath(
        node=NamedTraitListener(
            name="right",
            notify=True,
            optional=False,
        )
    )
    value = ListenerPath(
        node=NamedTraitListener(
            name="value",
            notify=True,
            optional=False,
        )
    )
    left.cycles.update([left, right])
    left.branches.add(value)
    right.cycles.update([left, right])
    right.branches.add(value)
    path1.branches.update([left, right])
    return path1


def create_path2():
    expected = ListenerPath(
        node=NamedTraitListener(
            name="root",
            notify=True,
            optional=False,
        )
    )
    left_path = ListenerPath(
        node=NamedTraitListener(
            name="left",
            notify=True,
            optional=False,
        ),
    )

    right_path = ListenerPath(
        node=NamedTraitListener(
            name="right",
            notify=True,
            optional=False,
        )
    )
    left_path.branches.add(right_path)
    right_path.cycles.add(left_path)
    expected.branches.add(left_path)
    return expected


if __name__ == "__main__":
    unittest.main()
