from app.domain.article_group_registry import (
    get_article_group,
    is_group_dependent_article,
    list_article_groups,
)


def test_ragnetto_12074_12078_members_resolve_to_group():
    for article in ["12074", "12075", "12076", "12077", "12078"]:
        group = get_article_group(article)

        assert group is not None
        assert group["group_id"] == "ragnetto_12074_12078"
        assert group["group_type"] == "ASSEMBLY_GROUP"
        assert group["source"] == "TL"
        assert group["status"] == "DA_MODELLARE"
        assert group["confidence"] == "CERTO"
        assert group["planner_policy"] == "GROUP_DEPENDENCY_NOT_INDEPENDENT"
        assert article in group["members"]


def test_ragnetto_members_are_group_dependent_articles():
    assert is_group_dependent_article("12074") is True
    assert is_group_dependent_article("12078") is True


def test_non_group_article_does_not_resolve_to_ragnetto():
    assert get_article_group("12063") is None
    assert is_group_dependent_article("12063") is False


def test_list_article_groups_returns_copy():
    groups = list_article_groups()

    assert len(groups) >= 1
    ragnetto = [g for g in groups if g["group_id"] == "ragnetto_12074_12078"][0]

    ragnetto["members"].append("BROKEN")

    fresh = get_article_group("12074")
    assert fresh is not None
    assert "BROKEN" not in fresh["members"]
