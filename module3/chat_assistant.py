# chat_assistant.py

import json
from IPython.display import display, HTML
import markdown

class Tools:
    def __init__(self):
        self.tools = {}
        self.functions = {}

    def add_tool(self, function, description):
        self.tools[function.__name__] = description
        self.functions[function.__name__] = function
    
    def get_tools(self):
        return list(self.tools.values())

    def function_call(self, tool_call_response):
        function_name = tool_call_response.name
        arguments = json.loads(tool_call_response.arguments)

        f = self.functions[function_name]
        result = f(**arguments)

        return {
            "type": "function_call_output",
            "call_id": tool_call_response.call_id,
            "output": json.dumps(result, indent=2),
        }

def shorten(text, max_length=50):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

class ChatInterface:
    def input(self):
        return input("You: ")
    
    def display(self, message):
        print(message)

    def display_function_call(self, entry, result):
        call_html = f"""
            <details>
            <summary>Function call: <tt>{entry['name']}({shorten(entry['arguments'])})</tt></summary>
            <div>
                <b>Call</b>
                <pre>{entry}</pre>
            </div>
            <div>
                <b>Output</b>
                <pre>{result['output']}</pre>
            </div>
            </details>
        """
        display(HTML(call_html))

    def display_response(self, entry):
        response_html = markdown.markdown(entry['content'])
        html = f"""
            <div>
                <div><b>Assistant:</b></div>
                <div>{response_html}</div>
            </div>
        """
        display(HTML(html))

class ChatAssistant:
    def __init__(self, tools, developer_prompt, chat_interface, client):
        self.tools = tools
        self.developer_prompt = developer_prompt
        self.chat_interface = chat_interface
        self.client = client

    def gpt(self, chat_messages):
        return self.client.chat.completions.create(
            model="gpt-4o",
            messages=chat_messages,
            tools=self.tools.get_tools(),
        )

    def run(self):
        chat_messages = [{"role": "system", "content": self.developer_prompt}]

        while True:
            question = self.chat_interface.input()
            if question.strip().lower() == 'stop':
                self.chat_interface.display("Chat ended.")
                break

            user_message = {"role": "user", "content": question}
            chat_messages.append(user_message)

            while True:
                response = self.gpt(chat_messages)
                choice = response.choices[0]
                message = choice.message
                has_messages = False

                # Handle function calls
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                        entry = {
                            "type": "function_call",
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                            "call_id": tool_call.id,
                        }
                        result = self.tools.function_call(entry)
                        chat_messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": result["output"],
                        })
                        self.chat_interface.display_function_call(entry, result)
                elif message.content:
                    chat_messages.append({"role": "assistant", "content": message.content})
                    self.chat_interface.display_response({"content": message.content})
                    has_messages = True

                if has_messages:
                    break