import ai
from config import Config
import json
from customLogging import generate_id

print("initialize build graph")
graph = ai.create_graph()

response, threadid  = ai.process_messages(name="Cho Tae-yul",
        countryName="Korea",
        designation="",
        human_message_template=Config.HUMAN_MESSAGE_TEMPLATE,
        # sectionNameList=["career"], 
        sectionNameList=["main_particulars","education","career","appointments","languages","reference"], 
        # sectionNameList=["education","reference"], 
        graph=graph)
jsonResponse = json.dumps(response)

print(f"Thread id : {threadid}")
print(f"Formatted Response : \n {jsonResponse}")
# print(f"Response : {response}")

# print(generate_id(prefix="test"))
