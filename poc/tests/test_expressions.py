import copy
import pickle
import unittest

from poc.expressions import trait, recursive, metadata
from poc.observe import (
    _is_not_none,
    NamedTraitListener, ListenerPath, MetadataListener,
)


class TestBasicExpression(unittest.TestCase):

    def test_basic_t(self):
        expression = trait("name")
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
        expression = trait("name").trait("attr")
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
        expression = trait("name") | trait("attr")
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
        e1 = trait("name") | trait("name")
        e2 = trait("name")
        self.assertEqual(len(e1.as_paths()), 1)
        self.assertEqual(len(e2.as_paths()), 1)
        self.assertEqual(e1.as_paths(), e2.as_paths())

    def test_or_with_same_paths(self):
        e1 = trait("name") | trait("age")
        e2 = trait("age") | trait("name")
        e3 = e1 | e2
        self.assertEqual(len(e3.as_paths()), 2)

    def test_or_then_extend(self):
        e1 = (trait("a").trait("b") | trait("c")).trait("d")

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
        expression = trait("child").then(trait("age") | trait("name"))
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


class TestRecursion(unittest.TestCase):

    def test_recursion(self):
        expression = trait("root").recursive(trait("left") | trait("right"))
        actual, = expression.as_paths()
        self.assertEqual(actual.node.name, "root")

        self.assertEqual(
            set(p.node.name for p in actual.nexts),
            set(["left", "right"])
        )
        nexts = list(actual.nexts)
        self.assertCountEqual(nexts[0].nexts, set(actual.nexts))
        self.assertCountEqual(nexts[1].nexts, set(actual.nexts))

    def test_recursion_with_equals(self):
        # Same test but use equality check
        expression = trait("root").recursive(trait("left") | trait("right"))
        actual, = expression.as_paths()

        expected = ListenerPath(
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
        expected.branches.update([left, right])
        left.cycles.update([left, right])
        right.cycles.update([left, right])

        self.assertEqual(actual, expected)

    def test_recursion_then_extend(self):
        expression = (
            trait("root").recursive(
                trait("left") | trait("right")).trait("value")
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

    def test_recursion_then_extend_with_equals(self):
        # Same test but use equality check
        expression = trait("root").recursive(
            trait("left") | trait("right")).trait("value")
        actual, = expression.as_paths()

        expected = ListenerPath(
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
        expected.branches.update([left, right])
        left.cycles.update([left, right])
        left.branches.add(value)
        right.cycles.update([left, right])
        right.branches.add(value)

        self.assertEqual(actual, expected)

    def test_recursion_different_order(self):
        expression1 = trait("root").recursive(trait("right") | trait("left")).trait("value")
        expression2 = trait("root").recursive(trait("left") | trait("right")).trait("value")
        self.assertEqual(
            expression1.as_paths(),
            expression2.as_paths(),
        )

    def test_recursion_not_equal(self):
        expression1 = trait("root").recursive(trait("left") | trait("right")).trait("value")
        expression2 = trait("root").recursive(trait("prev") | trait("right")).trait("value")
        self.assertNotEqual(
            expression1.as_paths(),
            expression2.as_paths(),
        )

    def test_recursion_branch_not_equal(self):
        expression1 = trait("root").recursive(trait("left") | trait("right")).trait("value")
        expression2 = trait("root").recursive(trait("left") | trait("right")).trait("age")
        self.assertNotEqual(
            expression1.as_paths(),
            expression2.as_paths(),
        )

    def test_recursion_multi_level(self):
        left_then_right = trait("left").trait("right")
        expression = (
            trait("root").recursive(left_then_right)
        )
        actual, = expression.as_paths()

        # First level, root only
        self.assertEqual(actual.node.name, "root")

        # Second level, left
        path, = actual.nexts
        self.assertEqual(path.node.name, "left")

        # Third level, right
        path, = path.nexts
        self.assertEqual(path.node.name, "right")

        # Fourth level, back to left again
        path, = path.nexts
        left_path = path
        self.assertEqual(path.node.name, "left")

        # And so on
        path, = path.nexts
        self.assertEqual(path.node.name, "right")
        path, = path.nexts
        self.assertIs(path, left_path)

        # The original left_or_right should not be
        # mutated
        new_left_then_right = trait("left").trait("right")
        self.assertEqual(
            left_then_right,
            new_left_then_right,
        )

    def test_recursion_multi_level_with_equals(self):
        # Same test but use equality check
        left_then_right = trait("left").trait("right")
        expression = (
            trait("root").recursive(left_then_right)
        )
        actual, = expression.as_paths()

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
        right_path.cycles.add(left_path)
        left_path.branches.add(right_path)
        expected.branches.add(left_path)

        self.assertEqual(actual, expected)

    def test_recursion_extended_twice(self):
        # This would match
        # root.left.right.value
        # root.left.right.left.right.value
        # root.left.right.left.right.left.right.value
        expression = trait("root").recursive(
            trait("left").trait("right")).trait("value")

        path, = expression.as_paths()

        # first is root
        self.assertEqual(path.node.name, "root")

        # second is left
        self.assertEqual([p.node.name for p in path.nexts], ["left"])
        path, = path.nexts

        # then it matches right
        self.assertEqual([p.node.name for p in path.nexts], ["right"])
        path, = path.nexts

        # then it might match left again, or value
        names = [p.node.name for p in path.nexts]
        self.assertCountEqual(names, ["left", "value"])

        # if it matches left, then it has to match right again
        for left_path in path.nexts:
            if left_path.node.name == "left":
                right_path, = left_path.nexts
                self.assertEqual(right_path.node.name, "right")
                break
        else:
            self.fail("No left node found.")

    def test_recursion_extended_twice_with_equals(self):
        # Same test, but use equality check
        # This would match
        # root.left.right.value
        # root.left.right.left.right.value
        # root.left.right.left.right.left.right.value
        expression = trait("root").recursive(
            trait("left").trait("right")).trait("value")

        expected = ListenerPath(
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
        right.branches.add(value)
        right.cycles.add(left)
        left.branches.add(right)
        expected.branches.add(left)

        actual, = expression.as_paths()
        self.assertEqual(actual, expected)

    def test_recursive_from_empty(self):
        expression = recursive(trait("name"))
        expected = ListenerPath(
            node=NamedTraitListener(
                name="name",
                notify=True,
                optional=False,
            ),
        )
        expected.cycles.add(expected)

        actual, = expression.as_paths()
        self.assertEqual(actual, expected)

    def test_recursive_different_paths(self):
        expression1 = trait("root").recursive(trait("one").trait("two"))
        expression2 = trait("root").recursive(trait("one").trait("three"))
        self.assertNotEqual(
            expression1.as_paths(),
            expression2.as_paths()
        )

    def test_deepcopy_strange_behaviour(self):
        e1 = recursive(trait("value") | trait("name"))
        e2 = trait("name")
        e3 = e1 | e2

        self.assertCountEqual(
            set(e1.as_paths()) | set(e2.as_paths()),
            e3.as_paths(),
        )

    def test_recurse_extend_then_recurse(self):
        recurse_c = recursive(trait("c"))
        e = recursive(recurse_c.trait("d"))
        e = recursive(recursive(trait("c")).trait("d"))

        path, = e.as_paths()

        # First is just "c"
        self.assertEqual(path.node.name, "c")

        # Then it matches either "c" or "d"
        self.assertCountEqual(
            [p.node.name for p in path.nexts],
            ["c", "d"]
        )

        # d is the branch...
        d_path, = path.branches

        # it should then go back to c
        self.assertEqual([p.node.name for p in d_path.nexts], ["c"])

    def test_extend_recurse_recurse(self):
        e = recursive(trait("b", False).recursive(trait("c")))

        path, = e.as_paths()

        # First it is just b
        self.assertEqual(path.node.name, "b")

        # then it matches "c"
        self.assertCountEqual([p.node.name for p in path.nexts], ["c"])

        c_path, = path.nexts

        # then it loops to "c" or "b"
        self.assertCountEqual([p.node.name for p in c_path.nexts], ["c", "b"])

        # With equality check
        expected = ListenerPath(
            node=NamedTraitListener(name="b", notify=False, optional=False),
        )
        c_path = ListenerPath(
            node=NamedTraitListener(name="c", notify=True, optional=False),
        )
        c_path.cycles.update([expected, c_path])
        expected.branches.add(c_path)
        self.assertEqual(path, expected)


class TestDeepCopySupper(unittest.TestCase):
    """ Integration test with the ListenerPath to test deepcopy
    support.

    When HasTraits methods are decorated with ``observe``, we may choose
    to hash the created ``ListenerPath`` low level objects, instead of
    hashing the user-facing ``Expression`` aiming at providing a user-friendly
    interface.

    With ``ListenerPath`` being a persisted internal state of an HasTraits
    instance, it needs to support deepcopy and pickling. Recursion would make this
    challenging.
    """

    def test_basic_path_pickle(self):
        expression = trait("a")
        path, = expression.as_paths()
        serialized = pickle.dumps(path)
        deserialized = pickle.loads(serialized)
        self.assertEqual(deserialized, path)

    def test_recursed_path_pickle(self):

        expression = recursive(trait("a"))
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
    instance, it needs to support deepcopy and pickling. Recursion would make this
    challenging.
    """

    def test_basic_path_pickling(self):
        expression = trait("a")
        path, = expression.as_paths()
        copied = copy.deepcopy(path)
        self.assertEqual(copied, path)

    def test_recursed_path_deep_copy(self):

        expression = recursive(trait("a"))
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
