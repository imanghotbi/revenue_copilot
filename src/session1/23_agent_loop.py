# 💻 THE AGENT LOOP. ~50 lines, no framework. Everything else in this course
# is a hardened, feature-rich version of this function.
import json

def render_tool_prompt(schemas):
    """Turn tool schemas into prompt text (the JSON-prompting technique)."""
    lines = ["You have access to these tools:", ""]
    for s in schemas:
        f = s["function"]
        args = ", ".join(f"{k}: {v.get('type', 'string')}" for k, v in f["parameters"]["properties"].items())
        lines.append(f"- {f['name']}({args}) - {f['description']}")
    lines += [
        "",
        "To use a tool, reply with ONLY a JSON object in this exact shape:",
        '  {"thought": "<why>", "tool": "<name>", "args": {<arguments>}}',
        "When the task is finished, reply with ONLY:",
        '  {"thought": "<why>", "final_answer": "<your answer to the user>"}',
        "Never invent values. If you need a fact, call a tool.",
    ]
    return "\n".join(lines)


def parse_model_json(text):
    """Extract the first JSON object from a model's reply, tolerating prose
    and ```json fences. Returns None if there is nothing parseable."""
    text = text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start, depth = text.find("{"), 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except Exception:
                    return None
    return None


def agent_loop(task, schemas, tool_functions, call_model, system_prompt,
               max_steps=6, verbose=True):
    """Run one agent to completion.

    task           the user's request
    schemas        JSON tool schemas, to show the model
    tool_functions {name: callable} - the real implementations
    call_model     fn(messages: list[dict]) -> str   (any model will do)
    """
    messages = [
        {"role": "system", "content": system_prompt + "\n\n" + render_tool_prompt(schemas)},
        {"role": "user", "content": task},
    ]
    trace = []

    for step in range(1, max_steps + 1):
        reply = call_model(messages)
        parsed = parse_model_json(reply)

        if parsed is None:                       # model ignored the format
            if verbose:
                print(f"  step {step}: could not parse a tool call -> treating as final answer")
            trace.append({"step": step, "type": "unparsed", "text": reply[:200]})
            return {"answer": reply, "trace": trace, "steps": step, "status": "unparsed"}

        thought = parsed.get("thought", "")

        if "final_answer" in parsed:             # ← THE EXIT CONDITION
            if verbose:
                print(f"  step {step}: FINAL  (thought: {thought[:90]})")
            trace.append({"step": step, "type": "final", "thought": thought,
                          "answer": parsed["final_answer"]})
            return {"answer": parsed["final_answer"], "trace": trace,
                    "steps": step, "status": "ok"}

        name, args = parsed.get("tool"), parsed.get("args", {}) or {}
        if name not in tool_functions:           # hallucinated tool name
            observation = json.dumps({"error": f"unknown tool '{name}'",
                                      "available": sorted(tool_functions)})
        else:
            try:
                observation = tool_functions[name](**args)
            except TypeError as exc:             # wrong arguments
                observation = json.dumps({"error": f"bad arguments for {name}: {exc}",
                                          "expected": list(tool_functions[name].__code__.co_varnames)})
            except Exception as exc:             # tool blew up: feed it back, don't crash
                observation = json.dumps({"error": f"{type(exc).__name__}: {exc}"})

        if verbose:
            print(f"  step {step}: CALL {name}({json.dumps(args, default=str)[:80]})")
            print(f"           -> {str(observation)[:110]}")

        trace.append({"step": step, "type": "tool", "tool": name, "args": args,
                      "thought": thought, "observation": str(observation)[:300]})

        # The two messages that make it an agent: the model's action, and the
        # world's answer. Both go back into the context.
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": f"[tool result] {observation}"})

    return {"answer": None, "trace": trace, "steps": max_steps, "status": "max_steps_exceeded"}


print("agent_loop defined. Note the three exits: final_answer, unparsable reply, max_steps.")
