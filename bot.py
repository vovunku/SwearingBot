import logging
import re

from df_engine.core.keywords import TRANSITIONS, RESPONSE
from df_engine.core import Context, Actor
import df_engine.conditions as cnd
import df_engine.labels as lbl
import df_engine.responses as rsp
from typing import Any

from examples import example_1_basics

logger = logging.getLogger(__name__)

def reuse_phrase(pattern: str):
    def reuse_phrase_inner(ctx: Context, actor: Actor, *args, **kwargs) -> Any:
        return pattern.format(ctx.last_request)

    return reuse_phrase_inner


plot = {
    "global_flow": {
        "start_node": {
            RESPONSE: "Oh, you are helpless. Let's try again",
            TRANSITIONS: {
                ("greeting_flow", "node1"): cnd.regexp(r".*[hi|hello].*", re.IGNORECASE),
                "fallback_node": cnd.true(),
            },
        },
        "fallback_node": {
            RESPONSE: "Didn't understand a word. Can you even speak english?",
            TRANSITIONS: {
                lbl.previous(): cnd.regexp(r".*previous.*", re.IGNORECASE),
                "start_node": cnd.true()
            },
        },
    },
    "greeting_flow": {
        "node1": {
            RESPONSE: reuse_phrase('"{}"? Who the hell are you and what in the world do you want?'),
            TRANSITIONS: {
                ("global_flow", "fallback_node", 0.1): cnd.true(),
                "node2": cnd.regexp(r".*[I am|name].*", re.IGNORECASE),
            },
        },
        "node2": {
            RESPONSE: "Nevermind, useless info. Wanna hear a joke?",
            TRANSITIONS: {
                lbl.to_fallback(0.1): cnd.true(),
                ("greeting_flow", "no_joke"): cnd.regexp(r"no", re.IGNORECASE),
                ("greeting_flow", "joke"): cnd.regexp(r"yes", re.IGNORECASE),
            },
        },
        "joke": {
            RESPONSE: "Google it. Do I look like a clown for you??", 
            TRANSITIONS: {
                "end": cnd.true(),
            },
        },
        "no_joke": {
            RESPONSE: "Oh, actually I don't need to tell anything. Just look in the mirror",
            TRANSITIONS: {
                "end": cnd.true(),
            },
        },
        "end" : {
            RESPONSE: 'Okay we should end this stupid dialog. Write "exit" to leave me alone',
            TRANSITIONS: {
                ("bye_flow", "used_exit"): cnd.exact_match("exit"),
                ("bye_flow", "didnt_use_exit"): cnd.true()
            }, 
        }
    },
    "bye_flow": {
        "didnt_use_exit":  {
            RESPONSE: reuse_phrase('Are you really so stupid? You should use "exit". Obviously not "{}"'),
            TRANSITIONS: {
                "used_exit": cnd.exact_match("exit"),
                lbl.repeat(): cnd.true()
            },
        },
        "used_exit": {
            RESPONSE: "Lol, you really did it? You are pathetic. Go away now",
            TRANSITIONS: {
                lbl.forward(): cnd.true()
            }
        },
        "exit": {
            RESPONSE: rsp.choice(["That's dumb, I don't want to talk with you", 
                                  "So boring. You are boring. Get out!",
                                  "You are pissing me off. Get out!",
                                  "So stupid. You are stupid. Go away"]),
            TRANSITIONS: {lbl.repeat(): cnd.true()},
        },
    },
}

actor = Actor(
    plot, start_label=("global_flow", "start_node"), fallback_label=("global_flow", "fallback_node"), label_priority=1.0
)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s", level=logging.DEBUG
    )
    # run_test()
    example_1_basics.run_interactive_mode(actor)