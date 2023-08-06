# LLDB Cody Assistant

Bringing Contextual Cody Assistant to your LLDB & GDB Debugger. Execute commands by typing `cody` followed by asking for help.

![cody-logo](./assets/cody-logo.png)

### Installation

```shell
pip install -r requirements.txt
```

### Cody LLDB Assistant

```shell
(lldb) command script import /PATH/TO/main.py
(lldb) command script add -f main.codylldb cody
(lldb) cody get the command to the run the program
run
Process 21342 stopped
...
...
(lldb) cody get the command to print all registers
register read
General purpose register
    x0 = 0x0000000000001000895 "Hello world! \n"
    ...
    ...
```