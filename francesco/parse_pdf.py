import openai
import ndjson

# Set up your OpenAI API key
openai.api_key = ''

table_to_read = 1
n_batches_to_test = None ## set to None if you want to process the whole file

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
    # 3: """{}""",
    # 4: """{}""",
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
    """
}


def split_table_in_batches(data, n):
    """
    splits the table into a list of lists
    """

    lines = data.split('\n')

    output = []
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
            
    return output
            
            

# Define the input data (this could be a large text table)
with open(f'/home/jovyan/work/dufourspitze_16/francesco/table_{table_to_read}.txt', 'r') as f:
    table_data = f.read()

batches = split_table_in_batches(table_data, 5)

json_data = []
if n_batches_to_test is not None:
    batches = batches[:n_batches_to_test]
    
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
    #print("Formatted JSON Output:")
    print(output)

    lines = output.split('\n')
    good_lines = [i for i in lines if i.startswith('{')]


with open(f'data_from_table_{table_to_read}.ndjson', 'w') as f:
    ndjson.dump(good_lines, f)
