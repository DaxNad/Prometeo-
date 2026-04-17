from enum import Enum


class TaskType(str, Enum):
    DOMAIN_TRANSLATION = "DOMAIN_TRANSLATION"
    CI_FIX = "CI_FIX"
    SMALL_PATCH = "SMALL_PATCH"
    MULTI_FILE_PATCH = "MULTI_FILE_PATCH"
    ARCH_REVIEW = "ARCH_REVIEW"
    DOMAIN_VALIDATION = "DOMAIN_VALIDATION"
    SMF_MAPPING_CHANGE = "SMF_MAPPING_CHANGE"
    PLANNER_LOGIC_CHANGE = "PLANNER_LOGIC_CHANGE"


class AgentRole(str, Enum):
    CHATGPT = "CHATGPT"
    CODEX = "CODEX"
    CLAUDE = "CLAUDE"


ROUTING_TABLE = {
    TaskType.DOMAIN_TRANSLATION: [AgentRole.CHATGPT],

    TaskType.CI_FIX: [
        AgentRole.CHATGPT,
        AgentRole.CODEX
    ],

    TaskType.SMALL_PATCH: [
        AgentRole.CHATGPT,
        AgentRole.CODEX
    ],

    TaskType.MULTI_FILE_PATCH: [
        AgentRole.CHATGPT,
        AgentRole.CODEX,
        AgentRole.CLAUDE
    ],

    TaskType.ARCH_REVIEW: [
        AgentRole.CHATGPT,
        AgentRole.CLAUDE
    ],

    TaskType.DOMAIN_VALIDATION: [
        AgentRole.CHATGPT,
        AgentRole.CLAUDE
    ],

    TaskType.SMF_MAPPING_CHANGE: [
        AgentRole.CHATGPT,
        AgentRole.CODEX,
        AgentRole.CLAUDE
    ],

    TaskType.PLANNER_LOGIC_CHANGE: [
        AgentRole.CHATGPT,
        AgentRole.CODEX,
        AgentRole.CLAUDE
    ],
}


def get_route(task_type: TaskType):
    return ROUTING_TABLE.get(task_type, [AgentRole.CHATGPT])
