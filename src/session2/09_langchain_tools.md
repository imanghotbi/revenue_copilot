### 2.2 Tools are still just functions

Northwind's 13 tools are ordinary Python, decorated with LangChain's `@tool`.
The decorator does what `make_schema()` did in Session 1: it attaches a JSON
schema the model can read. You already used `.invoke({...})` in Session 1.
`bind_tools` is how the *model* gets the same information.
