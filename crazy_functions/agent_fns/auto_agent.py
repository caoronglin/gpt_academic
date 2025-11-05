from crazy_functions.agent_fns.general import AutoGenGeneral
from crazy_functions.agent_fns.pipe import PipeCom, PluginMultiprocessManager
from toolbox import (
    CatchException,
    ProxyNetworkActivate,
    Singleton,
    gen_time_str,
    get_log_folder,
    report_exception,
    trimmed_format_exc,
    update_ui,
    update_ui_latest_msg,
)


class AutoGenMath(AutoGenGeneral):

    def define_agents(self):
        from autogen import AssistantAgent, UserProxyAgent

        return [
            {
                "name": "assistant",  # name of the agent.
                "cls": AssistantAgent,  # class of the agent.
            },
            {
                "name": "user_proxy",  # name of the agent.
                "cls": UserProxyAgent,  # class of the agent.
                "human_input_mode": "ALWAYS",  # always ask for human input.
                "llm_config": False,  # disables llm-based auto reply.
            },
        ]
