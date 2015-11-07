# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from validater import schema


def test_schema():
    """"""
    leaf1 = "+int&required", 1, "leaf1 desc"
    leaf2 = "unicode&required"
    leaf3 = "unicode", None, "article table of content"

    branch1 = schema("leaf1", "leaf2")
    branch2 = schema("branch1", "leaf3")

    flower = schema(["branch1"])
    tree = schema(["branch2"])

    forest1 = schema(["tree"])
    forest2 = schema([["branch2"]])
    park = schema("tree", "flower")

    scope = locals()

    # import json

    # def pp(obj):
    #     print json.dumps(obj, ensure_ascii=False, indent=4)

    # pp(branch1(scope))
    # pp(branch2(scope))

    # pp(flower(scope))
    # pp(tree(scope))

    # pp(forest1(scope))
    # pp(forest2(scope))
    # pp(park(scope))

    branch1 = branch1(scope)
    assert branch1["leaf1"]["validate"] == "+int"
    assert branch1["leaf2"]["validate"] == "unicode"

    branch2 = branch2(scope)
    assert branch2["branch1"]["leaf1"]["validate"] == "+int"
    assert branch2["leaf3"]["validate"] == "unicode"

    flower = flower(scope)
    assert len(flower) == 1
    assert flower[0]["leaf1"]["validate"] == "+int"

    tree = tree(scope)
    assert len(tree) == 1
    assert tree[0]["branch1"]["leaf1"]["validate"] == "+int"
    assert tree[0]["leaf3"]["validate"] == "unicode"

    forest1 = forest1(scope)
    forest2 = forest2(scope)
    assert forest1[0][0]["leaf3"]["validate"] == "unicode"
    assert forest1 == forest2

    park = park(scope)
    assert park["tree"][0]["branch1"]["leaf1"]["validate"] == "+int"
    assert park["flower"][0]["leaf1"]["validate"] == "+int"


def test_schema_with_name():
    leaf_red = "leaf", ("+int&required", 1, "leaf_red")
    leaf_green = "leaf", ("unicode&required",)

    branch1 = "branch", schema("leaf_red")
    branch2 = "branch", schema("branch1", "leaf_green")

    flower = schema(["branch1"])
    tree = schema(["branch2"])

    forest1 = schema(["tree"])
    forest2 = schema([["branch2"]])
    park = schema("tree", "flower")

    scope = locals()

    # import json

    # def pp(obj):
    #     print json.dumps(obj, ensure_ascii=False, indent=4)

    # pp(flower(scope))
    # pp(tree(scope))

    # pp(forest1(scope))
    # pp(forest2(scope))
    # pp(park(scope))

    branch1 = branch1[1](scope)
    assert branch1["leaf"]["validate"] == "+int"

    branch2 = branch2[1](scope)
    assert branch2["branch"]["leaf"]["validate"] == "+int"

    flower = flower(scope)
    assert len(flower) == 1
    assert flower[0]["leaf"]["validate"] == "+int"

    tree = tree(scope)
    assert len(tree) == 1
    assert tree[0]["branch"]["leaf"]["validate"] == "+int"

    forest1 = forest1(scope)
    forest2 = forest2(scope)
    assert forest1[0][0]["leaf"]["validate"] == "unicode"
    assert forest1 == forest2

    park = park(scope)
    assert park["tree"][0]["branch"]["leaf"]["validate"] == "+int"
    assert park["flower"][0]["leaf"]["validate"] == "+int"
