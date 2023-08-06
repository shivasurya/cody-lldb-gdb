import json
import requests
import os

# write a global multi line string message to set it inital context
GDB_LLDB_PROMPT = '''
You are a secure and powerful LLDB debug assistant. Unless or otherwise told, you should always
generate valid and useful GDB or LLDB commands to inspect and debug code without any explaination.
For example: give me code for breakpoint at foo function
Your answer should be just "break foo".
Strictly remove any hello, formatting or code explaination. 
Just reply with valid command without any chat style prefix such as Human or Assistant
'''

QA_LLDB_PROMPT = '''
{user_prompt}
Just reply with valid command without any chat style prefix such as Human or Assistant
'''

MESSAGE_HISTORY = []

CODY_URL = "https://sourcegraph.com/.api/completions/stream"
CODY_ACCESS_TOKEN = os.environ.get('CODY_ACCESS_TOKEN')

def codylldb(debugger, command, result, internal_dict):
  init_message()
  command = set_cody_context(CODY_URL, command)
  debugger.HandleCommand(command)

# write a function to make http post request to cody API
def set_cody_context(url, user_prompt):
  data = prepare_message(QA_LLDB_PROMPT.format(user_prompt=user_prompt), actor='human')
  headers = {
    'Authorization': "token "+ CODY_ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Requested-With': 'Sourcegraph',
  }
  response = requests.post(url, headers=headers, json=data, stream=True)
  # persist system text and speaker to as object to store in message_history
  # parse line by line and get the last occurance of event: completion line9
  lines = response.text.split('\n')
  recent_message = {}
  for i,line in enumerate(lines):
    if line == "event: completion":
      # remove data: from line
      completion = lines[i+1].split("data:")[1]
      codyLLDBCommands = json.loads(completion)['completion']
      codyLLDBCommands = str(codyLLDBCommands).strip()
      # Assistant: break foo 
      # remove Assistant: from string if it present
      if codyLLDBCommands.startswith("Assistant: "):
        codyLLDBCommands = codyLLDBCommands[len("Assistant: "):]

      if codyLLDBCommands.startswith("Human: "):
        codyLLDBCommands = codyLLDBCommands[len("Human: "):]

      recent_message = {
        "speaker": "assistant",
        "text": codyLLDBCommands,
      }
  
  MESSAGE_HISTORY.append(recent_message)
  return codyLLDBCommands

# write a function to prepare cody message payload as system or actor param
def prepare_message(message, actor='human'):
  CHAT_MESSAGE = { "speaker": actor, "text": message }
  global MESSAGE_HISTORY
  MESSAGE_HISTORY.append(CHAT_MESSAGE)
  data = {
    "maxTokensToSample": 500,
    "temperature": 0.1,
    "messages" : MESSAGE_HISTORY,
    "topK": -1,
		"topP": -1,
  }
  return data

def init_message():
  CHAT_MESSAGE = { "speaker": 'human', "text": GDB_LLDB_PROMPT }
  ASSISTANT_MESSAGE = { "speaker": "assistant", "text": "ok" }
  MESSAGE_HISTORY.append(CHAT_MESSAGE)
  MESSAGE_HISTORY.append(ASSISTANT_MESSAGE)