# Structural Verilog Generator Script for Sequential Logic
## Created By Peter DiSanto (pkd442)

### Overview:
The Structural Verilog Generator Script (SVGS) for Sequential Logic is a python program
that takes in a finite-state-machine(FSM) truthtable and additonal information relevant to the expression(number of state-bits, input number/name, output number/name) in the form of a **.in file** and converts the simplified sum-of-products next-state and output logic into fully-compilable structural verilog, which is compatible with the libraries provided in ECE382N.19. The verilog is written to a new file, which the user has control of naming.

### How to use:
First: Create a fresh, new directory!!!! Then cd into that directory
```
mkdir new_directory
cd new_directory
```

**Also: make sure you have python downloaded and usable on your machine** 

List of files in new_directory needed for use:
- **state_machine_gen.py** : master script, what actually does the verilog conversion and file writing 
- **sm.in** : arbitrary state machine truth table (example shown below) which will be converted to structural verilog
- **espresso.linux** : UC Berkeley's SOP simplifying tool, have executable in the same directory as master script and .in file  (the executable can be found under problem set 2 or on UC Berkeley's website for espresso)

### sm.in example:
```
.s 1
.i 2
.o 2
.ilb s x_in
.ob s_next z_out

00 00
01 10
10 01
11 11
```
This format is almost identical to the combinational logic truth table input, but with a few inportant differences. 

1. There has been a new line added (the first line), which is the .s argument, specifing the number of state bits (or flipflops) in the sequential machine. 
2. Although there is only 1 actual input/output (x_in/z_out) tp the FSM, there are TWO inputs/outputs because the current state is counted as an INPUT to the machine and the next state is counted as an OUTPUT of the machine. Importantly, when aligning the positioning of these variables, the MSB of the state-bit Inputs/Outputs MUST COME FIRST. Then the other I/O variables can come arbitraily afterward. For example, two state bit inputs (S1, S0) and two state bit ouputs(S1_n, S0_n) must be the first named in the inputs and the outputs, and also the first (leftmost) column of the inputs and outputs state machine truth table.

That culminates the differences from the Combo Logic Generator to the Sequenrial Logic Generator

**Once all of these modules are in your desired directory** the following command can be run to execute SVGS
```
python3 state_machine_gen.py sm.in sm.v
```
**sm.v** is the name of the verilog file where the generated structural verilog will be dumped into, creating a compilable and integratable module ready at the user's disposal. **The naming for the .in and .v files are fully up to the user**

### What to expect:
Once the above command is run with a correct directory setup, if you are using a linux-based machine with a viewable terminal, there should be an ouput saying **"Wrote Verilog to sm.v"** and a new file in your directory called **"sm.v"**

### Troubleshooting and Reminders:
If there is a compilation issue, make sure all files are within the same directory.
Make sure you also have python, specifically python3, downloaded on your machine

If both of these requirements are met and the script still will not run, then check the espresso tool individually
using commands like
```
espresso.linux sm.in
```
or 
```
espresso.linux -o eqntott sm.in
```
in order to check if the espresso executable works correctly. 
If there are no or unintelligble outputs, then make sure you have the correct/updated espresso tool. NOTE: the esresso tool will still run file even with the new ".s" file argument 

If you encounter any run-time/generation errors, please contact the SVGS service team @ **+1 617-448-4817**

### Thank you and Happy Verilogging

