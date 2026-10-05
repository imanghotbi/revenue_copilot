## 4. 🧠 Chat templates: the model never sees your Python list

When you write `[{"role": "system", ...}, {"role": "user", ...}]` you are using a
convenient fiction. The model is a text-in, text-out function. Something has to
flatten your list into a single string, and that something is the **chat
template** — a Jinja template shipped inside the model repository.

Different families use different markers. Qwen uses `<|im_start|>role ...
<|im_end|>`. Llama uses `[INST] ... [/INST]` or `<|start_header_id|>`. If you
ever get bizarre output from a local model, nine times out of ten the chat
template was applied wrongly — usually by hand-formatting the prompt instead of
calling `apply_chat_template`.

Run the next cell with `show_prompt=True` and read the exact string the model
receives. Note the trailing `<|im_start|>assistant` with nothing after it: that
is the *generation prompt*, the model's cue that it is now its turn to speak.
