import subprocess 
import sys

filename = sys.argv[1] 

result = subprocess.run(
    ["./espresso.linux", filename],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
    check=True
)
#print(result.stdout)

output_lines = result.stdout.splitlines()
product_terms_raw = []
outputs_raw = []
for line in output_lines:
    if line.startswith('.i '):
        input_num = line.split()[1]
    elif line.startswith('.o '):
        output_num = line.split()[1]
    elif line.startswith('.ilb'):
        input_names = line.split()[1:]
    elif line.startswith('.ob'):
        output_names = line.split()[1:]
    elif line.startswith('.p'):
        product_term_num = line.split()[1]
    elif line.startswith('.s '):
        state_bits = line.split()[1]
    elif line.startswith('.e'):
        continue
    else:
        input, output = line.split()
        product_terms_raw.append(input)
        outputs_raw.append(output)

inverter_wires = []
inverters = []
and_wires = []
and_output_wires = []
num_and_output_wires = 0
ands = []
wire_count = 0
inv_num = 0

for i in product_terms_raw:
    and_out = {}
    inp_cnt = 0

    for j in range(int(input_num)):
        if i[j] == '0':
            key = "wire " + input_names[j] + "_b;"
            if key not in inverter_wires:
                inverter_wires.append("wire " + input_names[j] + "_b;")
                inverters.append("inv1$ inv" + str(inv_num) + "(" + input_names[j] + "_b, " + input_names[j] + ");")
                inv_num += 1
            and_out["in" + str(j)] = input_names[j] + "_b"
            inp_cnt += 1
        elif i[j] == '1':
            and_out["in" + str(j)] = input_names[j]
            inp_cnt += 1
        else:
            continue

    and_terms = []
    for k in and_out:
        if k.startswith("in"):
            if inp_cnt > 1:
                and_terms.append(and_out[k])
            else:
                and_terms.append(and_out[k])
                and_terms.append(and_out[k])

    while len(and_terms) > 4:
        temp_wire = "and_temp_" + str(wire_count)
        and_wires.append("wire " + temp_wire + ";")

        wire0, wire1, wire2, wire3 = and_terms[0], and_terms[1], and_terms[2], and_terms[3]
        ands.append(f"and4$ and{wire_count}({temp_wire}, {wire0}, {wire1}, {wire2}, {wire3});")

        and_terms = [temp_wire] + and_terms[4:]
        wire_count += 1
    
    if len(and_terms) == 2:
        and_output_wires.append("wire and_final_out_" + str(num_and_output_wires) + ";")
        ands.append(f"and2$ and_final{num_and_output_wires}(and_final_out_{num_and_output_wires}, {and_terms[0]}, {and_terms[1]});")
        num_and_output_wires += 1
    elif len(and_terms) == 3:
        and_output_wires.append("wire and_final_out_" + str(num_and_output_wires) + ";")
        ands.append(f"and3$ and_final{num_and_output_wires}(and_final_out_{num_and_output_wires}, {and_terms[0]}, {and_terms[1]}, {and_terms[2]});")
        num_and_output_wires += 1
    else:  # 4
        and_output_wires.append("wire and_final_out_" + str(num_and_output_wires) + ";")
        ands.append(f"and4$ and_final{num_and_output_wires}(and_final_out_{num_and_output_wires}, {and_terms[0]}, {and_terms[1]}, {and_terms[2]}, {and_terms[3]});")
        num_and_output_wires += 1

or_gates = []
out_x_indicies = []

for j in range(int(output_num)):
    temp = []
    count = 0
    for i in outputs_raw:
        if i[j] == '1':
            wire_temp = and_output_wires[count]
            temp.append(wire_temp[5:-1])
        count += 1
    out_x_indicies.append(temp)

count = 0
or_wire_cnt = 0
or_wires = []
for i in out_x_indicies:
    while(len(i) > 4):
        temp_wire = "or_temp_" + str(or_wire_cnt)
        or_wires.append("wire " + temp_wire + ";")

        wire0, wire1, wire2, wire3 = i[0], i[1], i[2], i[3]
        or_gates.append(f"or4$ or{or_wire_cnt}({temp_wire}, {wire0}, {wire1}, {wire2}, {wire3});")

        i = [temp_wire] + i[4:]
        or_wire_cnt += 1
        
    if (len(i) == 2):
        or_term = (f"or2$ or_final{count} ({output_names[count]}, {i[0]}, {i[1]});")
    elif (len(i) == 3):
        or_term = (f"or3$ or_final{count} ({output_names[count]}, {i[0]}, {i[1]}, {i[2]});")
    elif (len(i) == 4):
        or_term = (f"or4$ or_final{count} ({output_names[count]}, {i[0]}, {i[1]}, {i[2]}, {i[3]});")
    else:
        or_term = "or2$ or" + str(count) + "(" + output_names[count] + ", " + i[0] + ", " + i[0] + ");"
    count += 1
    or_gates.append(or_term)

curr_state_inp = []
next_state_out = []
for i in range (int(state_bits)):
    curr_state_inp.append(input_names[i])
    next_state_out.append(output_names[i])
flop_count = 0
flops = []
for i in range (int(state_bits)):
    flop = (f"dff$ flop{flop_count}(.clk(clk), .r(reset), .d({output_names[i]}), .q({input_names[i]}));")
    flop_count += 1
    flops.append(flop)

out_filename = sys.argv[2] if len(sys.argv) > 2 else "seq_logic.v"

with open(out_filename, "w") as f:
    print("module " + out_filename[:-2] + "(", file=f)
    inputs = ""
    for i in input_names[int(state_bits):]:
        inputs += "input " + i + ", "
    inputs += "input clk, input reset, "
    for i in output_names[int(state_bits):]:
        inputs += "output " + i + ", "
    inputs = inputs[:-2] + "\n);"
    print(inputs, file=f)

    for line in inverter_wires:
        print(line, file=f)
    print("", file=f)

    for line in and_wires:
        print(line, file=f)
    print("", file=f)
    
    for line in and_output_wires:
        print(line, file=f)
    print("", file=f)
    
    for line in or_wires:
        print(line, file=f)
    print("", file=f)

    for line in inverters:
        print(line, file=f)
    print("", file=f)

    for line in ands:
        print(line, file=f)
    print("", file=f)

    for line in or_gates:
        print(line, file=f)
    print("", file=f)
    
    for line in flops:
        print(line, file = f) 
    print("endmodule", file=f)

print("Wrote Verilog to " + out_filename)
