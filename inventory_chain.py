from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from audit_enum import AuditLogStatus

class AuditLogStatusSchema(BaseModel):
    status: str = AuditLogStatus


load_dotenv()

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)

parser = JsonOutputParser(pydantic_object=AuditLogStatusSchema)


prompt = PromptTemplate(
    template="Provide me the status the user is asking for in this query: {question} \n {json_schema_instruction}",
    input_variables=["question"],
    partial_variables={"json_schema_instruction":parser.get_format_instructions()}
)

main_chain = prompt | llm | parser