import openai
import ndjson

# Set up your OpenAI API key
openai.api_key = ''

table_to_read = 3
batch_size = 30
n_batches_to_test = None ## set to None if you want to process the whole file

print(f"parsing table {table_to_read} with batch size = {batch_size}")
if n_batches_to_test is not None:
    print(f" .. testing on only {n_batches_to_test} batches")
else:
    print(" .. parsing all the file!!!")

## table 4: 
## Compartment Location Variable Name Units Variable Definition

table_to_input_example = {
    1: """
1 [Blood-Lymph].CTLA4_mabB <-> Lymph_Node.CTLA4_mab
2 [Blood-Lymph].CTLA4_mabB <-> Peripheral.CTLA4_mabP_leaky
3 [Blood-Lymph].CTLA4_mabB <-> Peripheral.CTLA4_mabP_tight
""",
    2: """
1 Kpa_LNB*S_LNB*VL*f_LN_CTLA4*([Blood-Lymph].CTLA4_mabB/Vc_CTLA4-Lymph_Node.CTLA4_mab/VL)
2 0.67*Q_L*[Blood-Lymph].CTLA4_mabB*(1-Sigma1_CTLA4)/Vc_CTLA4 -
(Peripheral.CTLA4_mabP_leaky/(0.35*ISF*KP_CTLA4))*0.33*Q_L*(1-Sigma1_CTLA4)
3 0.33*Q_L*[Blood-Lymph].CTLA4_mabB*(1-Sigma2_CTLA4)/Vc_CTLA4-
(Peripheral.CTLA4_mabP_tight/(0.65*ISF*KP_CTLA4))*0.33*Q_L*(1-Sigma2_CTLA4)
""",
    3: """
1 Distribution of Anti-CTLA-4 mAb between the central and lymph node compartments
2 Distribution of Anti-CTLA-4 mAb between the central and leaky tissues
3 Distribution of Anti-CTLA-4 mAb between the central and tight tissues
""",
    4: """
Blood-Lymph CTLA4_mabB mole Anti-CTLA-4 antibody in the blood
Blood-Lymph CTLA4_mabB_ugml µg/ml Serum concentration of Anti-CTLA-4
Blood-Lymph Effector_T_TOTAL cell
Lymph_Node NEG_Sig_PNT_CD86 mole Receptor-receptor interactions at the immunological synapse between CTLA-4 expressed on Primed Naive T cells and CD80 expressed on mAPCs during the second phase of priming 
Lymph_Node CTLA4_mAb_CTLA4 mole Heterogeneous receptor-antibody interactions at the immunological synapse between CTLA-4 expressed on Primed Naive T cells during the second priming phase and Anti-CTLA-4 mAb delivered to the lymph node by way of IV injection into the blood 
""",
    # 5: """{}""",
    # 6: """{}""",
    # 7: """{}""",
    # 8: """{}""",
    # 9: """{}""",
    # 10: """{}""",
    # 11: """{}""",
}

table_to_output_example = {
    1: """
    {"reaction number":1, "reaction":"[Blood-Lymph].CTLA4_mabB <-> Lymph_Node.CTLA4_mab"}
    {"reaction number":2, "reaction":"[Blood-Lymph].CTLA4_mabB <-> Peripheral.CTLA4_mabP_leaky"}
    {"reaction number":3, "reaction":"[Blood-Lymph].CTLA4_mabB <-> Peripheral.CTLA4_mabP_tight"}
    """,
    2:"""
    {"reaction number": 1, "reaction rate": "Kpa_LNB*S_LNB*VL*f_LN_CTLA4*([Blood-Lymph].CTLA4_mabB/Vc_CTLA4-Lymph_Node.CTLA4_mab/VL)"}
    {"reaction number":2, "reaction rate": "0.67*Q_L*[Blood-Lymph].CTLA4_mabB*(1-Sigma1_CTLA4)/Vc_CTLA4 -
(Peripheral.CTLA4_mabP_leaky/(0.35*ISF*KP_CTLA4))*0.33*Q_L*(1-Sigma1_CTLA4)"}
    {"reaction number":3, "reaction rate": "0.33*Q_L*[Blood-Lymph].CTLA4_mabB*(1-Sigma2_CTLA4)/Vc_CTLA4-
(Peripheral.CTLA4_mabP_tight/(0.65*ISF*KP_CTLA4))*0.33*Q_L*(1-Sigma2_CTLA4)"}
    """,
    3:"""
{"reaction number":1, "description":"Distribution of Anti-CTLA-4 mAb between the central and lymph node compartments"},
{"reaction number":2, "description":"Distribution of Anti-CTLA-4 mAb between the central and leaky tissues"},
{"reaction number":3, "description":"Distribution of Anti-CTLA-4 mAb between the central and tight tissues"}
""",
    4:"""
{"compartment_location":"Blood-Lymph", "variable_name":"CTLA4_mabB", "units":"mole", "variable_definition":"Anti-CTLA-4 antibody in the blood"}
{"compartment_location":"Blood-Lymph", "variable_name":"CTLA4_mabB_ugml", "units":"µg/ml", "variable_definition":"Serum concentration of Anti-CTLA-4"}
{"compartment_location":"Lymph_Node", "variable_name":"NEG_Sig_PNT_CD86", "units":"mole", "variable_definition":"Receptor-receptor interactions at the immunological synapse between CTLA-4 expressed on Primed Naive T cells and CD80 expressed on mAPCs during the second phase of priming"}
{"compartment_location":"Lymph_Node", "variable_name":"CTLA4_mAb_CTLA4", "units":"mole", "variable_definition":"Heterogeneous receptor-antibody interactions at the immunological synapse between CTLA-4 expressed on Primed Naive T cells during the second priming phase and Anti-CTLA-4 mAb delivered to the lymph node by way of IV injection into the blood"} 
"""
}


def split_table_in_batches(data, n, table_number):
    """
    splits the table into a list of lists
    """

    lines = data.split('\n')

    output = []
    if table_number <= 3:
        
        count = 0
        tmp = []
        
        for line in lines:
            tokens = line.split(' ')
            if tokens[0].isdigit():
                count += 1
            tmp.append(line)
            if count % n == 0:
                output.append(tmp)
                tmp = []
                count = 0

    elif table_number == 4:
        count = 0
        tmp = []
        for line in lines:
            count += 1
            tmp.append(line)
            if count % n == 0:
                output.append(tmp)
                tmp = []
                count = 0
            
    return output
            
            
# Define the input data (this could be a large text table)
with open(f'/home/jovyan/work/dufourspitze_16/data/table_{table_to_read}.txt', 'r') as f:
    table_data = f.read()

batches = split_table_in_batches(table_data, batch_size, table_to_read)

json_data = []
if n_batches_to_test is not None:
    batches = batches[:n_batches_to_test]

full_output = []
for i,batch in enumerate(batches):

    print(f"parsing batch #{i}")
    
    # Define the system prompt and input prompt for the model
    system_prompt = "You are an expert at formatting text into JSON."
    user_prompt = """
    Convert the following table data into new-line-delimited JSON format.
    The format should be as simple as possible, e.g. "column name": "column content" for each column for each entry. Please show the whole content of the json object!!!
    For an input like this:
    {0}
    I want an output like this:
    {1}

    Please in the output only show the formatted data and no additional text.
    Here is the text:
    {2}""".format(table_to_input_example[table_to_read], table_to_output_example[table_to_read], batch)

    #print(user_prompt)
    
    # Call OpenAI API with GPT-4 model
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ]
    )
    
    # Extract the model's output
    output = response['choices'][0]['message']['content']
    
    # Display the JSON output
    print(output)

    lines = output.split('\n')
    good_lines = [i for i in lines if i.startswith('{')]
    full_output += good_lines

with open(f'data_from_table_{table_to_read}.ndjson', 'w') as f:
    ndjson.dump(full_output, f)
